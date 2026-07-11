
from __future__ import annotations
import math
import matplotlib
matplotlib.use('TkAgg') 

from matplotlib import animation
import matplotlib.pyplot as plt
import sounddevice as sd
import soundfile as sf
import numpy as np


class VisualizeEnv:
    
    def __init__(self, start, velocity , total_time_sec, mics, label = None,  audio_file=None, auto_close = False, rotate = False):     
        self.start = start
        self.velocity = velocity
        self.total_time_sec = total_time_sec
        self.mics = mics
        self.trajectory = self._generate_1ms_trajectory()
        self.auto_close = auto_close
        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.audio_file = audio_file
        self.audio_data = None
        self.audio_sr = None
        self.rotate = rotate
        self.label = self._format_info(label)
        if self.audio_file:
            self.audio_data, self.audio_sr = sf.read(self.audio_file)
            if  self.audio_data.ndim == 2:
                 self.audio_data = np.mean( self.audio_data, axis=1)
    
    
    def _format_info(self, info):
        
        if info is None:
            return None
        
        return "\n".join(f"{k:<12}: {v}" for k, v in info.items())

    def _generate_1ms_trajectory(self):
        """
        Generates a 3D trajectory array sampled at exactly 1-millisecond intervals.
        
        Parameters:
        start_pos: list or array of [x, y, z] starting coordinates
        velocity: list or array of [vx, vy, vz] constant speed in meters per second
        total_time_sec: total duration of the flight flight path in seconds
        """
        # 1. Total number of 1ms steps (e.g., 5 seconds = 5000 steps)
        total_ms_steps = int( self.total_time_sec * 1000)
        
        step_factor = max(1, self.velocity.shape[0] // total_ms_steps)
        
        clip_vel = self.velocity[::step_factor]
        
        if len(clip_vel) > total_ms_steps:
            clip_vel = clip_vel[:total_ms_steps]
        elif len(clip_vel) < total_ms_steps:
            # If too short, pad it by repeating the last velocity vector
            padding = np.tile(clip_vel[-1], (total_ms_steps - len(clip_vel), 1))
            clip_vel = np.vstack([clip_vel, padding])

        # 4. Calculate positions for all steps simultaneously using vectorization
        # Reshaping timestamps to (N, 1) multiplies it across [vx, vy, vz] evenly
        #trajectory_1ms = start + (clip_vel * timestamps[:, np.newaxis])
        trajectory_1ms = self.start + np.cumsum(clip_vel * 0.001, axis=0)
        
        return trajectory_1ms

    def render(self):
        
        if self.label is not None:
            self.fig.text(
                0.01,          # x position
                0.99,          # y position
                self.label,
                ha="left",
                va="top",
                fontsize=8,
                family="monospace",
                bbox=dict(
                    facecolor="white",
                    edgecolor="gray",
                    alpha=0.8,
                    boxstyle="round"
                )
            )
            #self.fig.subplots_adjust(left=0.28)
            
        # Render persistent background paths
        self.ax.plot(
            self.trajectory[:, 0], self.trajectory[:, 1], self.trajectory[:, 2],
            linewidth=1, alpha=0.3, color='gray', label='Full Trajectory'
        )
        self.ax.scatter(*self.trajectory[0], color='green', s=80, label='Start')
        self.ax.scatter(*self.trajectory[-1], color='red', s=80, label='End')

        # Create the line object handle used for tracking the moving point marker
        self.point, = self.ax.plot(
            [self.trajectory[0, 0]], 
            [self.trajectory[0, 1]], 
            [self.trajectory[0, 2]],
            'bo', markersize=10, zorder=10
        )

        self.ax.plot(
            self.mics[0],
            self.mics[1],
            self.mics[2],
            'bo', markersize=10, zorder=10
        )
        z = np.linspace(self.mics[2], self.mics[2] + 100, 50)
        x = np.full_like(z, self.mics[0])
        y = np.full_like(z, self.mics[1])
        self.ax.scatter(x, y, z, color='blue', s=3)

        self.ax.legend()
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.azim_offset = 0.0
        
        self._set_view_angle(self.azim_offset)
        
        render_interval_ms = 100  
        data_step_per_frame = render_interval_ms 
        self.last_frame = math.floor(len(self.trajectory) / render_interval_ms) + 1
        # Define the updater sequence triggered automatically by the animation engine
        def update_frame(frame_index):
            
            if (frame_index  >= self.last_frame):
                if self.audio_file:
                    sd.stop()
               
                if self.auto_close:
                    self.fig.canvas.manager.window.after(2000, lambda: plt.close(self.fig))
                
            data_idx = frame_index * data_step_per_frame
            data_idx = min(data_idx, len(self.trajectory) - 1)
            x, y, z = self.trajectory[data_idx]
            self.point.set_data([x], [y])
            self.point.set_3d_properties([z])
        
             # ---- camera rotation ----
            if self.rotate:
                self.azim_offset = (self.azim_offset + 360 / self.last_frame)
                self._set_view_angle(self.azim_offset)
            
            return self.point,

        # Register the frame loop inside Matplotlib's native event window loop
        self.ani = animation.FuncAnimation(
            fig=self.fig,
            func=update_frame,
            frames= self.last_frame,
            interval=render_interval_ms,     # Target refresh interval delay in milliseconds
            repeat=False,   # Keeps the point resting at the end position 
            blit=False      # Must be False for 3D layout contexts
        )

        if self.audio_file:
            sd.play(self.audio_data, self.audio_sr)
    
        # block=True forces the active Python execution context to anchor itself to the 
        # UI window, letting the operating system handle the painting loops correctly.
        plt.show(block=True)

    def _set_view_angle(self, azim_offset:float):
        
        delta = self.mics - self.trajectory[0]

        # horizontal distance only (ignore altitude for azimuth)
        dx, dy = delta[0], delta[1]

        # Azimuth: rotate in XY plane only
        calc_azim = np.degrees(np.arctan2(dy, dx)) + azim_offset

        # FIXED ground plane view (no tilt from trajectory)
        # Choose a stable elevation angle (e.g., 90 = top-down, 0 = side view)
        # For a natural 3D view slightly tilted from start:
        start_altitude = self.trajectory[0][2] 
        target_altitude = self.mics[2]
       
        altitude_diff = target_altitude - start_altitude

        # scale factor to control viewing tilt sensitivity
        scale = 0.1
        calc_elev = 20 + scale * altitude_diff

        # clamp for stability
        calc_elev = np.clip(calc_elev, -89, 89)

        self.ax.view_init(elev=calc_elev, azim=calc_azim)
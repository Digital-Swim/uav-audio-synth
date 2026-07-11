from __future__ import annotations
from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np
from src.config.data_classes import ScenarioConfig
from src.sim.visual import VisualizeEnv
from src.logging.logger import log

class TrajectoryFactory:
    
    """
    All trajectories are parameterised so the drone starts / ends
    in physically meaningful positions relative to the array.
    Array centre is used as the reference point.
    """

    def __init__(self, cfg: ScenarioConfig):
        self.cfg   = cfg
        self.array = np.array(cfg.array.center, dtype=float)
        self.rng   = np.random.default_rng(cfg.seed)
        W, D, H = cfg.outdoor.width, cfg.outdoor.depth, cfg.outdoor.height
        self._W, self._D, self._H = W, D, H
        self.start_pos = None
        self.end_pos = None

    # ── public ────────────────────────────────────────────────────────────────

    def build(self, n_samples: int) -> np.ndarray:
        """Returns (N, 3) world-frame positions in metres."""
        label = self.cfg.label
        dispatch = {
            "approaching":  self._approaching,
            "leaving":      self._leaving,
            "flyby":          self._flyby,
            "hover":    self._hover
        }
        fn = dispatch.get(label, self._approaching)
        return fn(n_samples)

    def _approaching(self, N: int) -> np.ndarray:
        """Drone starts far, flies toward array."""
        dist_start = min(self.cfg.trajectory.speed * self.cfg.duration_s * 0.95,
                         self._W * 0.45)
        dist_end   = 8.0 + self.rng.uniform(0, 6)
        bearing    = np.deg2rad(self.cfg.trajectory.azimuth)
        elev_start = self.rng.uniform(25, 45)
        elev_end   = self.rng.uniform(10, 25)
        t = np.linspace(0, 1, N)
        dist  = dist_start + t * (dist_end - dist_start)
        elev  = np.deg2rad(elev_start + t * (elev_end - elev_start))
        bx    = self.array[0] + dist * np.cos(bearing) * np.cos(elev)
        by    = self.array[1] + dist * np.sin(bearing) * np.cos(elev)
        bz    = self.array[2] + dist * np.sin(elev)
        full_trajectory = self._clip(np.stack([bx, by, bz], axis=1))
        
        # 2. Extract the first and last [x, y, z] coordinate vectors
        self.start_pos = full_trajectory[0]   # Index 0 is the start position (0ms)
        self.end_pos = full_trajectory[-1]   # Index -1 is the final position (End of flight)

        print(f"Start position: {self.start_pos}")
        print(f"End position: {self.end_pos}")
        return full_trajectory

    def _leaving(self, N: int) -> np.ndarray:
        """Drone starts near, flies away."""
        pos = self._approaching(N)
        t = pos[::-1].copy() 
        self.start_pos = t[0]   # 
        self.end_pos = t[-1]
        return pos[::-1].copy()   # reverse = leaving

    def _hover(self, N: int) -> np.ndarray:
        """Stationary drone with micro-jitter."""
        d =self.rng.uniform(15, 200)  # distance from array
        bearing = np.deg2rad(self.cfg.trajectory.azimuth)
        elev    = np.deg2rad(self.rng.uniform(15, 40))
        cx = self.array[0] + d * np.cos(bearing) * np.cos(elev)
        cy = self.array[1] + d * np.sin(bearing) * np.cos(elev)
        cz = self.array[2] + d * np.sin(elev)
        jitter = self.rng.normal(0, 0.001, (N, 3))
        pos = np.tile([cx, cy, cz], (N, 1))  + jitter
        
        t = self._clip(pos) 
        self.start_pos = t[0]   # 
        self.end_pos = t[-1]
        
        return t 

    def _flyby(self, N: int) -> np.ndarray:
        """Drone crosses past the array – radial speed sign flips."""
        t       = np.linspace(0, 1, N)
        speed   = self.cfg.trajectory.speed #self.rng.uniform(8, 15)
        h       = self.rng.uniform(15, 35)
        # Lateral offset (closest approach distance)
        ca_dist = 1 #self.rng.uniform(5, 150)
        bearing = np.deg2rad(self.cfg.trajectory.azimuth) #self.rng.uniform(0, 2 * np.pi)
        perp    = bearing + np.pi / 2
        total   = speed * self.cfg.duration_s
        progress = (t - 0.5) * total   # centred so sign flips at mid
        bx = self.array[0] + ca_dist * np.cos(bearing) \
             + progress * np.cos(perp)
        by = self.array[1] + ca_dist * np.sin(bearing) \
             + progress * np.sin(perp)
        bz = np.full(N, self.array[2] + h)
        
        t =   self._clip(np.stack([bx, by, bz], axis=1))
        self.start_pos = t[0]   # 
        self.end_pos = t[-1]
        
        print(f"Start position: {self.start_pos}")
        print(f"End position: {self.end_pos}")
        return t

    # ── helpers ───────────────────────────────────────────────────────────────

    def _clip(self, pos: np.ndarray) -> np.ndarray:
        """Keep positions inside the outdoor volume with margin."""
        m = 1.0
        lo = [m,          m,          0.5]
        hi = [self._W - m, self._D - m, self._H - 1.0]
        return np.clip(pos, lo, hi)

    @staticmethod
    def velocity(positions: np.ndarray, dt: float) -> np.ndarray:
        """Central-difference velocity (N, 3) in m/s."""
        return np.gradient(positions, dt, axis=0)

    @staticmethod
    def radial_speed(
        positions: np.ndarray,
        velocities: np.ndarray,
        observer: np.ndarray,
    ) -> np.ndarray:
        """
        Signed radial speed (m/s) from observer's perspective.
        Positive = moving away, negative = approaching.
        """
        delta = positions - observer          # (N, 3)
        dist  = np.linalg.norm(delta, axis=1, keepdims=True) + 1e-9
        unit  = delta / dist
        return np.sum(velocities * unit, axis=1)

    @staticmethod
    def calculate_elevation_deg(center, target):
        """
        Calculates the elevation angle in degrees from a center observer to a target point.
        Assumes array format: [x, y, z] where z is height.
        """
        # 1. Get the relative vector pointing from center to target
        relative_vec = target - center
        x, y, z = relative_vec[0], relative_vec[1], relative_vec[2]
        
        # 2. Calculate the horizontal ground distance (hypotenuse of X and Y)
        ground_dist = np.sqrt(x**2 + y**2)
        
        # 3. Calculate the angle in radians, then convert to degrees
        # np.arctan2(y, x) handles signs safely and avoids division-by-zero errors
        elevation_rad = np.arctan2(z, ground_dist)
        elevation_deg = np.degrees(elevation_rad)
        
        return round(float(elevation_deg),2)
    
    
def test_scenario(cfg:ScenarioConfig):
    
    log.info("=" * 64)
    log.info(f"Scenario : {cfg.name}  label={cfg.label}")
    log.info(f"Mic mode : {cfg.array.mic_mode}")
    log.info(f"Duration : {cfg.duration_s} s")
    log.info(f"Sampling : {cfg.sim.fs}")
    log.info("=" * 64)
    
    N   = int(cfg.duration_s * cfg.sim.fs)
    dt  = 1.0 / cfg.sim.fs
    traj = TrajectoryFactory(cfg=cfg)

    log.info("Step - Generating trajectory …")
    positions  = traj.build(N)             
    velocities = TrajectoryFactory.velocity(positions, dt) 
    audio_path = "dataset\\test1\\scenario_000\\audio_8ch.wav"
    
    vis = VisualizeEnv(start=traj.start_pos, total_time_sec=cfg.duration_s, velocity=velocities,
                       mics=traj.array, audio_file=audio_path, label=cfg.label)
    vis.render()  

    
if __name__ == "__main__":
    cfg = ScenarioConfig()
    test_scenario(cfg=cfg)



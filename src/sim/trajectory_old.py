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
            "approaching_fast":  self._approaching,
            "approaching_slow":  self._approaching,
            "leaving_fast":      self._leaving,
            "leaving_slow":      self._leaving,
            "hover_near":        self._hover,
            "hover_far":         self._hover,
            "flyby":             self._flyby,
            "curved_approach":   self._curved_approach,
            "spiral_descent":    self._spiral_descent,
        }
        fn = dispatch.get(label, self._approaching)
        return fn(n_samples)

    def _approaching(self, N: int) -> np.ndarray:
        """Drone starts far, flies toward array."""
        speed = 12.0 if "fast" in self.cfg.label else 4.0
        dist_start = min(speed * self.cfg.duration_s * 0.95,
                         self._W * 0.45)
        dist_end   = 8.0 + self.rng.uniform(0, 6)
        bearing    = self.rng.uniform(0, 2 * np.pi)
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
        d = 10.0 if "near" in self.cfg.label else 60.0
        bearing = self.rng.uniform(0, 2 * np.pi)
        elev    = np.deg2rad(self.rng.uniform(15, 40))
        cx = self.array[0] + d * np.cos(bearing) * np.cos(elev)
        cy = self.array[1] + d * np.sin(bearing) * np.cos(elev)
        cz = self.array[2] + d * np.sin(elev)
        jitter = self.rng.normal(0, 0.05, (N, 3))
        pos = np.tile([cx, cy, cz], (N, 1)) + jitter
        
        t = self._clip(pos) 
        self.start_pos = t[0]   # 
        self.end_pos = t[-1]
        
        return t 

    def _flyby(self, N: int) -> np.ndarray:
        """Drone crosses past the array – radial speed sign flips."""
        t       = np.linspace(0, 1, N)
        speed   = self.rng.uniform(8, 15)
        h       = self.rng.uniform(15, 35)
        # Lateral offset (closest approach distance)
        ca_dist = self.rng.uniform(5, 20)
        bearing = self.rng.uniform(0, 2 * np.pi)
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
        
        return t

    def _curved_approach(self, N: int) -> np.ndarray:
        """Quadratic Bézier curve approaching from altitude."""
        t       = np.linspace(0, 1, N)
        d_far   = self.rng.uniform(60, 90)
        d_near  = self.rng.uniform(8, 15)
        b0      = self._rand_pos_at_dist(d_far,  elev_deg=(30, 50))
        b2      = self._rand_pos_at_dist(d_near, elev_deg=(8, 20))
        # Control point: offset laterally
        b1      = (b0 + b2) / 2 + self.rng.uniform(-15, 15, 3) * [1, 1, 0]
        pos     = (np.outer((1-t)**2, b0)
                   + np.outer(2*(1-t)*t, b1)
                   + np.outer(t**2, b2))
        
        t = self._clip(pos)
        self.start_pos = t[0]   # 
        self.end_pos = t[-1]
        return t

    def _spiral_descent(self, N: int) -> np.ndarray:
        """Helical descent toward array (surveillance pattern)."""
        t       = np.linspace(0, 1, N)
        r_start = self.rng.uniform(30, 55)
        r_end   = self.rng.uniform(5, 12)
        z_start = self.array[2] + self.rng.uniform(40, 55)
        z_end   = self.array[2] + self.rng.uniform(8, 18)
        n_turns = self.rng.uniform(1.5, 3.5)
        theta   = t * n_turns * 2 * np.pi + self.rng.uniform(0, 2*np.pi)
        r       = r_start + t * (r_end - r_start)
        bx      = self.array[0] + r * np.cos(theta)
        by      = self.array[1] + r * np.sin(theta)
        bz      = z_start + t * (z_end - z_start)
        
        t = self._clip(np.stack([bx, by, bz], axis=1))
        self.start_pos = t[0]   # 
        self.end_pos = t[-1]
        return t

    # ── helpers ───────────────────────────────────────────────────────────────

    def _rand_pos_at_dist(
        self, dist: float,
        elev_deg: Tuple[float, float] = (10, 45)
    ) -> np.ndarray:
        bearing = self.rng.uniform(0, 2 * np.pi)
        elev    = np.deg2rad(self.rng.uniform(*elev_deg))
        return self.array + dist * np.array([
            np.cos(bearing) * np.cos(elev),
            np.sin(bearing) * np.cos(elev),
            np.sin(elev),
        ])

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



SCENARIOS = [
    "approaching_fast",
    "approaching_slow",
    "leaving_fast",
    "leaving_slow",
    "hover_near",
    "hover_far",
    "flyby",
    "curved_approach",
    "spiral_descent",
]

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



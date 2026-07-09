
import json
from pathlib import Path
from typing import Dict, List

import numpy as np

from src.config.data_classes import ScenarioConfig
from src.logging.logger import log
from src.sim.mics import MicrophoneArray

class MetadataBuilder:
    """Accumulates per-sample ground-truth and serialises to JSON."""

    # We downsample metadata to 100 Hz (every 160 samples @ 16 kHz)
    METADATA_RATE_HZ = 100

    def __init__(self, cfg: ScenarioConfig):
        self.cfg     = cfg
        self.records: List[Dict] = []

    def build(
        self,
        positions:    np.ndarray,   # (N, 3)
        velocities:   np.ndarray,   # (N, 3)
        radial_speed: np.ndarray,   # (N,)  positive=leaving, negative=approaching
        mic_array:    MicrophoneArray,
        snr_db:       float,
    ):
        fs    = self.cfg.sim.fs
        step  = max(1, fs // self.METADATA_RATE_HZ)
        N     = len(positions)
        label = self.cfg.label

        for i in range(0, N, step):
            pos = positions[i]
            vel = velocities[i]
            rs  = float(radial_speed[i])
            array_center = np.array(self.cfg.array.center)
            delta = pos - array_center
            dist = float(np.linalg.norm(delta))

            # Azimuth and elevation angles of the drone relative to the microphone array center
            azimuth_rad = np.arctan2(delta[1], delta[0])
            elevation_rad = np.arctan2(delta[2], np.linalg.norm(delta[:2]))
            
            tdoa = mic_array.tdoa_gt(pos, self.cfg.sim.sound_speed)

            # Per-sample movement sub-label for model training signal
            if abs(rs) < 0.5:
                motion = "hover"
            elif rs < 0:
                motion = "approaching"
            else:
                motion = "leaving"

            self.records.append({
                "sample_idx":    i,
                "time_s":        round(i / fs, 4),
                "position_m":    [round(float(v), 3) for v in pos],
                "velocity_ms":   [round(float(v), 3) for v in vel],
                "distance_m":    round(dist, 3),
                "radial_speed_ms": round(rs, 4),
                "motion":        motion,
                "azimuth_deg":  round(np.degrees(azimuth_rad), 2),
                "elevation_deg": round(np.degrees(elevation_rad), 2),   
                "tdoa_us":       [round(float(v), 3) for v in tdoa],
            })

    def to_dict(self) -> Dict:
        ac  = self.cfg.array
        oc  = self.cfg.outdoor
        return {
            "scenario":           self.cfg.name,
            "label":              self.cfg.label,
            "duration_s":         self.cfg.duration_s,
            "mic_mode":           ac.mic_mode,
            "cardioid_p":         ac.cardioid_p if ac.mic_mode == "directional" else None,
            "audio": {
                "sample_rate_hz": self.cfg.sim.fs,
                "n_channels":     ac.n_mics,
                "array_center_m": list(ac.center),
                "array_radius_m": ac.radius,
            },
            "outdoor_env": {
                "dimensions_m":   [oc.width, oc.depth, oc.height],
                "wall_material":  oc.wall_material,
                "ground_material":oc.ground_material,
                "sky_material":   oc.sky_material,
                "max_rir_order":  oc.max_rir_order,
            },
            "samples": self.records,
        }

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        log.info(f"Metadata  → {path}  ({len(self.records)} records)")


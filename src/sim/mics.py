
from typing import List, Optional
from src.config.data_classes import MicArrayConfig
from typing import  List,  Optional 
import numpy as np
from pyroomacoustics.directivities import CardioidFamily, DirectionVector
from src.logging.logger import log

class MicrophoneArray:
    """
    8-microphone circular array with two modes:

    OMNIDIRECTIONAL
        Standard pressure microphones – equal sensitivity in all directions.
        Implemented as pra.Omnidirectional (no directivity object needed).

    DIRECTIONAL (Cardioid)
        Each mic faces *outward* from the array centre along its own radial
        direction.  This gives the array a heightened directional sensitivity
        so that mics facing the drone receive more energy than mics on the
        far side – a key cue for bearing estimation.
        Implemented via pra.CardioidFamily(p=cfg.cardioid_p).
    """

    def __init__(self, cfg: MicArrayConfig):
        self.cfg    = cfg
        self.n      = cfg.n_mics
        self.mode   = cfg.mic_mode
        self._build()

    # ── public ────────────────────────────────────────────────────────────────

    @property
    def positions(self) -> np.ndarray:
        """(3, n_mics) world-frame coordinates."""
        return self._pos

    @property
    def directivities(self) -> Optional[List]:
        """List of pra directivity objects, or None for omni."""
        return self._directivities

    def tdoa_gt(
        self, drone_pos: np.ndarray, sound_speed: float, ref_mic: int = 0
    ) -> np.ndarray:
        """
        Ground-truth TDOA (µs) relative to ref_mic.
        tdoa[i] = (dist_i − dist_0) / c × 1e6
        """
        dists = np.linalg.norm(self._pos.T - drone_pos, axis=1)
        return (dists - dists[ref_mic]) / sound_speed * 1e6

    # ── private ───────────────────────────────────────────────────────────────

    def _build(self):
        n   = self.n
        r   = self.cfg.radius
        cx, cy, cz = self.cfg.center
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)

        self._pos = np.array([
            cx + r * np.cos(angles),
            cy + r * np.sin(angles),
            np.full(n, cz),
        ])  # (3, n_mics)

        if self.mode == "directional":
            # Each mic points radially outward – azimuth = angle in XY plane,
            # colatitude = π/2 (horizontal, elevation = 0)
            self._directivities = [
                CardioidFamily(
                    orientation=DirectionVector(
                        azimuth=float(a),
                        colatitude=float(np.pi / 2),
                        degrees=False,
                    ),
                    p=self.cfg.cardioid_p,
                )
                for a in angles
            ]
            log.info(
                f"Mic array: DIRECTIONAL (cardioid p={self.cfg.cardioid_p}), "
                f"n={n}, r={r} m"
            )
        else:
            self._directivities = None
            log.info(f"Mic array: OMNIDIRECTIONAL, n={n}, r={r} m")


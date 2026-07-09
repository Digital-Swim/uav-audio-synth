from src.config.data_classes import DroneConfig, SimConfig
import numpy as np

from src.logging.logger import log


class DroneSourceSynth:
    """
    Synthesises a physically plausible drone acoustic source signal.

    Model
    -----
    • Multi-harmonic rotor model at base frequency f0 with exponential
      harmonic decay.
    • Per-sample Doppler shift derived from instantaneous radial velocity
      relative to the array centre.
    • 1/r amplitude attenuation applied per-sample before RIR convolution
      so the signal amplitude reflects true distance change over time.
    • Normalised to cfg.source_rms at 1 m reference distance.
    """

    def __init__(self, cfg: DroneConfig, sim: SimConfig, array_center: np.ndarray):
        self.cfg    = cfg
        self.sim    = sim
        self.center = array_center
        self.fs     = sim.fs

    def synthesise(
        self,
        positions:  np.ndarray,   # (N, C)   Number of samples, channels
        velocities: np.ndarray,   # (N, C)  
    ) -> np.ndarray:
        """Returns (N,) float32 Doppler-shifted, distance-attenuated signal."""
        N  = len(positions)
        dt = 1.0 / self.fs

        # Radial velocity (positive = moving away)
        delta    = positions - self.center
        dist     = np.linalg.norm(delta, axis=1) + 1e-9          # (N,)
        unit_vec = delta / dist[:, None]
        v_radial = np.sum(velocities * unit_vec, axis=1)          # (N,)

        c              = self.sim.sound_speed
        doppler_factor = c / (c + v_radial)                       # (N,)

        # Build signal: sum of Doppler-shifted harmonics
        signal = np.zeros(N, dtype=np.float64)
        for h in range(1, self.cfg.n_harmonics + 1):
            amp   = self.cfg.harmonic_decay ** (h - 1)
            f_inst = self.cfg.rotor_base_hz * h * doppler_factor  # (N,)
            phase  = np.cumsum(2.0 * np.pi * f_inst * dt)
            signal += amp * np.sin(phase)

        # Normalise to source_rms at 1 m
        rms    = np.sqrt(np.mean(signal ** 2)) + 1e-12
        signal = signal * (self.cfg.source_rms / rms)

        # 1/r distance attenuation (reference = 1 m)
        ref_dist = 1.0
        signal   = signal * (ref_dist / dist)

        return signal.astype(np.float32)


def test():
  pass

if __name__ == "__main__":
  test()

    
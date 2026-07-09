import numpy as np
import scipy.signal as ss
from src.config.data_classes import EnvNoiseConfig
import colorednoise as cn

class EnvNoiseSynth:
    """  
    Generates a single-channel outdoor noise floor that is later added to
    *each* mic channel independently (with small per-mic variation).

    Layers
    ------
    wind        – pink noise (1/f²) shaped to peak at 50–300 Hz,
                  with random turbulence bursts
    traffic     – very low-frequency rumble (10–80 Hz) representing
                  distant road / aircraft noise
    impulses    – sporadic transients (car horn, dog bark…)
    """

    def __init__(self, cfg: EnvNoiseConfig, fs: int, seed: int):
        self.cfg  = cfg
        self.fs   = fs
        # Note: colorednoise accepts an integer seed or a RandomState/Generator
        self.seed = seed ^ cfg.noise_seed

    def generate(self, n_samples: int) -> np.ndarray:
        wind     = self._wind(n_samples)
        traffic  = self._traffic(n_samples)
        impulses = self._impulses(n_samples)
        noise    = wind + traffic + impulses
        
        # Normalise to prevent dominating the drone signal
        peak = np.max(np.abs(noise)) + 1e-12
        return (noise / peak * (self.cfg.wind_rms + self.cfg.traffic_rms)).astype(np.float32)

    # ── layers ────────────────────────────────────────────────────────────────

    def _wind(self, N: int) -> np.ndarray:
        # generate Pink Noise (exponent = 1)
        # We pass the seed directly to the powerlaw generator
        pink = cn.powerlaw_psd_gaussian(exponent=1, size=N, random_state=self.seed)
        
        # Band-pass to wind frequency range (20–400 Hz)
        sos  = ss.butter(4, [20, 400], btype="bandpass", fs=self.fs, output="sos")
        pink = ss.sosfilt(sos, pink).astype(np.float32)

        # Turbulence bursts (using a local RNG instance to keep it isolated)
        rng = np.random.default_rng(self.seed + 1)
        gust = np.zeros(N, dtype=np.float32)
        i = 0
        while i < N:
            if rng.random() < self.cfg.wind_gust_prob:
                dur  = int(rng.uniform(0.3, 1.5) * self.fs)
                env  = np.hanning(min(dur, N - i)).astype(np.float32)
                amp  = rng.uniform(0.5, 1.0) * self.cfg.wind_gust_amp
                gust[i:i + len(env)] += amp * env
                i   += dur
            i += 1

        return (pink * self.cfg.wind_rms) + gust

    def _traffic(self, N: int) -> np.ndarray:
        # Traffic is heavy/low-end rumble. Brown noise (exponent = 2) is perfect.
        # It rolls off at -6dB/octave naturally before filtering.
        rumble = cn.powerlaw_psd_gaussian(exponent=2, size=N, random_state=self.seed + 2)
        
        sos    = ss.butter(3, [8, 80], btype="bandpass", fs=self.fs, output="sos")
        rumble = ss.sosfilt(sos, rumble).astype(np.float32)
        
        rms    = np.sqrt(np.mean(rumble ** 2)) + 1e-12
        return rumble * (self.cfg.traffic_rms / rms)

    def _impulses(self, N: int) -> np.ndarray:
        rng = np.random.default_rng(self.seed + 3)
        sig = np.zeros(N, dtype=np.float32)
        mask = rng.random(N) < self.cfg.impulse_prob
        idx  = np.where(mask)[0]
        for i in idx:
            dur = int(rng.uniform(0.01, 0.05) * self.fs)
            env = np.exp(-np.linspace(0, 8, min(dur, N - i)))
            amp = rng.uniform(0.5, 1.0) * self.cfg.impulse_amp
            sig[i:i + len(env)] += (amp * env).astype(np.float32)
        return sig

import math

from src.config.data_classes import ScenarioConfig
from src.sim.matadata import MetadataBuilder

from pathlib import Path
import numpy as np
import scipy.io.wavfile as wavfile
from src.logging.logger import log

class DatasetWriter:
    def __init__(self, cfg: ScenarioConfig):
        self.out = Path(cfg.output_dir) / cfg.label / cfg.name
        self.out.mkdir(parents=True, exist_ok=True)
        self.fs  = cfg.sim.fs

    def write_audio(self, mic_signals: np.ndarray, env_noise: np.ndarray):
        """
        Saves two WAV files:
          audio_8ch.wav       – drone + env noise (training input)
          noise_only_8ch.wav  – env noise alone (for SNR computation / noise model)
        """
        # Mix noise into each channel with slight per-mic variation
        rng = np.random.default_rng(42)
        n_mics = mic_signals.shape[1]
        mixed  = mic_signals.copy()
        noise_out = np.zeros_like(mic_signals)
        for m in range(n_mics):
            variation = rng.uniform(0.85, 1.0)
            noise_ch  = env_noise * variation
            # trim/pad noise to signal length
            N = len(mixed)
            if len(noise_ch) < N:
                noise_ch = np.tile(noise_ch, math.ceil(N / len(noise_ch)))[:N]
            else:
                noise_ch = noise_ch[:N]
            mixed[:, m]     += noise_ch
            noise_out[:, m]  = noise_ch
        # Normalise and convert to int16
        for arr, fname in [(mixed, "audio_8ch.wav"), (noise_out, "noise_only_8ch.wav")]:
            peak = np.max(np.abs(arr)) + 1e-12
            pcm  = (arr / peak * 0.95 * 32767).astype(np.int16)
            path = self.out / fname
            wavfile.write(str(path), self.fs, pcm)
            log.info(f"Audio     → {path}  shape={pcm.shape}")

    def write_metadata(self, meta: MetadataBuilder):
        meta.save(self.out / "metadata.json")

    def summary(self) -> str:
        files = list(self.out.rglob("*"))
        return (
            f"\n{'─'*64}\n"
            f"  Scenario : {self.out.parent.name}/{self.out.name}\n"
            f"  Files    : {len(files)}\n"
            f"{'─'*64}"
        )


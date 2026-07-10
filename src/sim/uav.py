
import math
import time

import numpy as np

from src.config.data_classes import ScenarioConfig
from src.sim.dataset import DatasetWriter
from src.sim.drone_audio import DroneSourceSynth
from src.sim.env import EnvNoiseSynth
from src.sim.matadata import MetadataBuilder
from src.sim.mics import MicrophoneArray
from src.sim.outdoor import OutdoorAcousticSim
from src.sim.trajectory import TrajectoryFactory
from src.logging.logger import log
from src.sim.visual import VisualizeEnv

class AntiUAVAudioGenerator:
    """
    End-to-end pipeline:

      TrajectoryFactory  →  DroneSourceSynth  →  OutdoorAcousticSim
                        ↘  EnvNoiseSynth      ↗  DatasetWriter
                                               ↘  MetadataBuilder
    """

    def __init__(self, cfg: ScenarioConfig):
        self.cfg      = cfg
        self.mic_arr  = MicrophoneArray(cfg.array)
        self.traj     = TrajectoryFactory(cfg)
        self.drone_src = DroneSourceSynth(
            cfg.drone, cfg.sim,
            np.array(cfg.array.center)
        )
        self.room_sim = OutdoorAcousticSim(cfg, self.mic_arr)
        self.env_noise_synth = EnvNoiseSynth(
            cfg.env_noise, cfg.sim.fs, cfg.seed
        )
        self.writer   = DatasetWriter(cfg)

    def run(self):
        t0 = time.perf_counter()
        log.info("=" * 64)
        log.info(f"Scenario : {self.cfg.name}  label={self.cfg.label}")
        log.info(f"Mic mode : {self.cfg.array.mic_mode}")
        log.info(f"Duration : {self.cfg.duration_s} s")
        log.info("=" * 64)

        fs  = self.cfg.sim.fs
        N   = int(self.cfg.duration_s * fs)
        dt  = 1.0 / fs

        # ── 1. Trajectory ────────────────────────────────────────────────────
        log.info("Step 1/4  Generating trajectory …")
        positions  = self.traj.build(N)              # (N, 3)
        velocities = TrajectoryFactory.velocity(positions, dt)  # (N, 3)
        radial_spd = TrajectoryFactory.radial_speed(
            positions, velocities, np.array(self.cfg.array.center)
        )
        
        #vis = VisualizeEnv(start=self.traj.start_pos, total_time_sec=self.cfg.duration_s, velocity=velocities, mics=self.traj.array)
        #vis.render()
        #print("visual render completed")
            
        # ── 2. Drone source signal ───────────────────────────────────────────
        log.info("Step 2/4  Synthesising Doppler drone source …")
        source = self.drone_src.synthesise(positions, velocities)

        # ── 3. Acoustic propagation (outdoor RIR) ────────────────────────────
        log.info("Step 3/4  Convolving with outdoor RIRs …")
        mic_signals =  self.room_sim.simulate(source, positions)  # (N, 8)
        
        # Test source signals
        #mic_signals = np.repeat(source[:, np.newaxis], 8, axis=1)
        
        
        # ── 4. Environmental noise ───────────────────────────────────────────
        log.info("Step 4/4  Generating env noise + writing outputs …")
        env_noise = self.env_noise_synth.generate(N)

        # Compute approx SNR (signal power vs noise power at mic 0)
        sig_rms   = float(np.sqrt(np.mean(mic_signals[:, 0] ** 2)) + 1e-12)
        noise_rms = float(np.sqrt(np.mean(env_noise[:N] ** 2)) + 1e-12)
        snr_db    = 20 * math.log10(sig_rms / noise_rms + 1e-12)

        # ── Metadata ─────────────────────────────────────────────────────────
        meta = MetadataBuilder(self.cfg)
        meta.build(positions, velocities, radial_spd, self.mic_arr, snr_db)

        # ── Write ────────────────────────────────────────────────────────────
        self.writer.write_audio(mic_signals, env_noise)
        self.writer.write_metadata(meta)

        elapsed = time.perf_counter() - t0
        log.info(f"Done in {elapsed:.1f} s  SNR≈{snr_db:.1f} dB")
        log.info(self.writer.summary())


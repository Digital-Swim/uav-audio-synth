# All scenario label variants supported by the generator
from pathlib import Path
from typing import List

from src.config.data_classes import DroneConfig, EnvNoiseConfig, MicArrayConfig, OutdoorConfig, ScenarioConfig, SimConfig, TrajectoryConfig
from src.sim.uav import AntiUAVAudioGenerator
from src.config.sim_env import drones, env_noises, labels, mic_arrays, outdoors, sims, speeds_test, speeds_train, azimuths_test, azimuths_train, duration_s, root_dir, speeds_val, azimuths_val, mode


def build_scenarios():
    
    if mode == "train":
        speeds = speeds_train
        azimuths = azimuths_train
    elif mode == "test":
        speeds = speeds_test
        azimuths = azimuths_test
    elif mode == "validation":
        speeds = speeds_val
        azimuths = azimuths_val
    else:
        raise ValueError("Invalid configuration")
      
    scenarios = []
    counter = 0
    for label in labels:
        for outdoor in outdoors:
            for drone in drones:
                for env_noise in env_noises:
                    for mics in mic_arrays:
                        for sim in sims:
                            for i, speed in enumerate(speeds):
                                # skip hover other than the first speed (0) to avoid duplicates
                                if label == "hover" and i > 0:
                                    continue 
                                for azimuth in azimuths:
                                    scenario = ScenarioConfig(
                                        name=f"scenario_{counter:03d}",
                                        label=label,
                                        output_dir=Path(root_dir) / mode,
                                        duration_s=duration_s,
                                        array=MicArrayConfig(**mics),
                                        sim=SimConfig(**sim),
                                        drone=DroneConfig(**drone),
                                        outdoor=OutdoorConfig(**outdoor),
                                        env_noise=EnvNoiseConfig(**env_noise),
                                        trajectory=TrajectoryConfig(
                                            speed=speed,
                                            azimuth=azimuth
                                        ),
                                        seed=counter + 100,
                                    )
                                    scenarios.append(scenario)
                                    counter += 1
    print(f"Built {len(scenarios)} scenarios.")
    return scenarios
                        
def run_batch(cfgs: List[ScenarioConfig]):
    for cfg in cfgs:
        AntiUAVAudioGenerator(cfg).run()

# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    scenarios = build_scenarios()    
    run_batch(scenarios)


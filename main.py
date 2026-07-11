# All scenario label variants supported by the generator
import argparse
from pathlib import Path
from typing import List

from src.analyses.distribution import DataDistAnalyzer
from src.config.data_classes import DroneConfig, EnvNoiseConfig, MicArrayConfig, OutdoorConfig, ScenarioConfig, SimConfig, TrajectoryConfig
from src.sim.uav import AntiUAVAudioGenerator
from src.config.sim_env import drones, env_noises, labels, mic_arrays, outdoors, sims, speeds_test, speeds_train, azimuths_test, azimuths_train, duration_s, root_dir, speeds_val, azimuths_val, mode


def build_scenarios(scenario_nos:List[str]=None):
    print(scenario_nos)
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
                                    counter_str = f"{counter:04d}"
                                    if scenario_nos is None or counter_str in scenario_nos:
                                        print(counter_str)
                                        scenario = ScenarioConfig(
                                            name=f"scenario_{counter_str}",
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
                        
def run_batch():
    scenarios = build_scenarios()
    for cfg in scenarios:
        AntiUAVAudioGenerator(cfg).run()

def plot_traj(scenarios:List[str]=["0000"]):
    scenarios = build_scenarios(scenario_nos=scenarios)
    if len(scenarios) > 0:
        AntiUAVAudioGenerator(scenarios[0]).plot_trajectory()
    else:
        print("No scenario found with this label")

def show_distribution(feature):
    analyzer = DataDistAnalyzer()
    if feature == "velocity":
        analyzer.show_velocity_distribution()
    elif feature == "distance":
        analyzer.show_distance_distribution()
    elif feature == "azimuth":
        analyzer.show_azimuth_distribution()
    elif feature == "elevation":
        analyzer.show_elevation_distribution()

# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Audio generation and plotting tool."
    )

    # Create top-level subparsers
    subparsers = parser.add_subparsers(dest="mode", required=True, help="Modes")

    # 1. 'run' mode subparser
    subparsers.add_parser("run", help="Generate audio data")

    # 2. 'plot' mode subparser
    plot_parser = subparsers.add_parser("plot", help="Plotting modes")

    # Add a sub-command under plot to choose WHAT to plot
    plot_subparsers = plot_parser.add_subparsers(
        dest="plot_type", required=True, help="Type of plot"
    )

    # 'plot trajectory' sub-command
    traj_parser = plot_subparsers.add_parser("trajectory", help="Plot the spatial trajectory")    
    traj_parser.add_argument(
        "--scenario",       # Added dashes to make it an optional flag
        default=0,
        type=int,
        help="The specific scenario ID to plot (e.g., 0000, 0001). Datasets not required."
    )
    
    # 'plot distribution' sub-command
    dist_parser = plot_subparsers.add_parser(
        "distribution", help="Plot data distributions"
    )

    # 'distribution' requires picking a specific feature
    dist_parser.add_argument(
        "--feature",
        choices=["velocity", "azimuth", "distance", "elevation"],
        help="The specific metric/feature distribution to plot",
    )

    # Parse the arguments
    args = parser.parse_args()

    # --- How to use the parsed arguments in your code ---
    if args.mode == "run":
        run_batch()
    elif args.mode == "plot":
        if args.plot_type == "trajectory":
            plot_traj([f"{args.scenario:04d}"])
        elif args.plot_type == "distribution":
           show_distribution(args.feature)


if __name__ == "__main__":
    main()

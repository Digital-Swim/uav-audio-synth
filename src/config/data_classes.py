
# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass, field
from typing import Literal, Tuple

MicMode = Literal["omnidirectional", "directional"]
TrajectoryDirection = Literal[
    "approaching", "hover", "leaving", "flyby", "circular"
]
    
@dataclass
class OutdoorConfig:
    """
    Simulates an urban outdoor space: wide open area bounded by
    concrete/brick building facades on all 4 sides, asphalt ground,
    and an open (anechoic) sky ceiling.
    """
    name:   str   = "default_urban"
    description: str   = "Default urban outdoor environment with open sky and surrounding buildings."
    width:  float = 1000.0          # m  – between buildings (E/W)
    depth:  float = 1000.0          # m  – between buildings (N/S)
    height: float = 1000.0           # m  – up to open sky
    wall_material:   str = "rough_concrete"   # building facades
    ground_material: str = "concrete_floor"   # asphalt/concrete ground
    sky_material:    str = "anechoic"         # open sky = no reflection
    max_rir_order:   int = 3                  # image-source reflections
    air_absorption:  bool = True
    wall_scattering:   float = 0.3                # 0=perfect specular, 1=fully diffuse
    ground_scattering: float = 0.2                # 0=perfect specular


@dataclass
class MicArrayConfig:
    """8-microphone circular array fixed at a pole/tripod outdoors."""
    name:   str   = "default_circular"
    description: str   = "Default 8-channel circular microphone array with omnidirectional elements."
    n_mics:    int   = 8
    radius:    float = 0.05          # 5 cm – compact array
    center:    Tuple[float, float, float] = (500.0, 500.0, 10.0)  # 1.8 m pole height
    mic_mode:  MicMode = "omnidirectional"  # "omnidirectional" | "directional"
    # Directional: cardioid p-value (0=omni, 0.5=cardioid, 0.75=hypercardioid, 1=figure8)
    cardioid_p: float = 0.5


@dataclass
class DroneConfig:
    """Simplified drone acoustic model: rotor blade-pass harmonics + broadband noise."""
    name:           str   = "default_quadcopter"
    description:    str   = "Default quadcopter drone with standard rotor noise characteristics."
    rotor_base_hz:  float = 150.0   # blade-pass fundamental
    n_harmonics:    int   = 6
    harmonic_decay: float = 0.55    # per-harmonic amplitude decay
    source_rms:     float = 0.7     # normalised RMS before attenuation


@dataclass
class EnvNoiseConfig:
    """Layered outdoor environmental noise model."""
    name:             str   = "default_env_noise"
    description:      str   = "Default outdoor environmental noise with wind, traffic, and occasional impulses."
    wind_rms:         float = 0.04   # pink-noise wind
    wind_gust_prob:   float = 0.003  # per-sample probability of gust onset
    wind_gust_amp:    float = 0.12
    traffic_rms:      float = 0.03   # distant low-frequency traffic rumble
    impulse_prob:     float = 0.0002 # random impulsive events (car horn, etc.)
    impulse_amp:      float = 0.25
    noise_seed:       int   = 0      # mixed with scenario seed


@dataclass
class SimConfig:
    name:         str   = "default_sim"
    description:  str   = "Default simulation parameters for outdoor drone audio."
    fs:           int   = 16_000
    sound_speed:  float = 343.0
    n_rir_snapshots: int = 16      # moving-source approximation segments

@dataclass
class TrajectoryConfig:
    name:         str   = "default_trajectory"
    description:  str   = "Default drone trajectory configuration."
    direction: TrajectoryDirection = "approaching"
    speed: float = 15
    azimuth: float = 120

@dataclass
class ScenarioConfig:
    name:      str           = "scenario_000"
    label:     TrajectoryDirection = "hover"
    duration_s: float        = 6.0
    outdoor:   OutdoorConfig  = field(default_factory=OutdoorConfig)
    array:     MicArrayConfig    = field(default_factory=MicArrayConfig)
    drone:     DroneConfig    = field(default_factory=DroneConfig)
    env_noise: EnvNoiseConfig = field(default_factory=EnvNoiseConfig)
    sim:       SimConfig      = field(default_factory=SimConfig)
    output_dir: str           = "datasets"
    trajectory: TrajectoryConfig = field(default_factory=TrajectoryConfig)
    seed:       int           = 42
outdoors = [
  {
    "name": "urban_suburban",
    "description": "Wide street bordered by low-height wood structures with moderate wall scattering and an asphalt roadway floor.",
    "width": 1000.0,
    "depth": 1000.0,
    "height": 1000.0,
    "wall_material": "wood_1.6cm",
    "ground_material": "linoleum_on_concrete",
    "sky_material": "anechoic",
    "max_rir_order": 2,
    "air_absorption": True,
    "wall_scattering": 0.25,
    "ground_scattering": 0.1
  }
]

mic_arrays = [
  {
    "name": "circular_omni_8ch_compact",
    "description": "Compact 8-channel circular microphone array using omnidirectional elements, ideal for uniform 360-degree spatial audio capture.",
    "n_mics": 8,
    "center": [150.0, 150.0, 10.0],
    "mic_mode": "omnidirectional",
    "radius": 0.05,
    "cardioid_p": 0.5
  }
]

drones = [
  {
    "name": "quadcopter_commercial_standard",
    "description": "Standard 5-inch commercial drone at hover speed with prominent mid-frequency motor noise",
    "rotor_base_hz": 100.0,
    "n_harmonics": 6,
    "harmonic_decay": 0.55,
    "source_rms": 0.7
  }
]

env_noises = [
  {
    "name": "urban_downtown_heavy_traffic",
    "description": "Dense urban canyon environment dominated by continuous low-frequency road traffic noise with occasional sharp mechanical impulses.",
    "wind_rms": 0.01,
    "wind_gust_prob": 0.0005,
    "wind_gust_amp": 0.03,
    "traffic_rms": 0.08,
    "impulse_prob": 0.001,
    "impulse_amp": 0.3,
    "noise_seed": 42
  },
  {
    "name": "gale_force_forest_valley",
    "description": "High-altitude woodland exposed to severe, highly turbulent wind conditions and frequent powerful gusts moving through foliage.",
    "wind_rms": 0.15,
    "wind_gust_prob": 0.015,
    "wind_gust_amp": 0.45,
    "traffic_rms": 0.0,
    "impulse_prob": 0.0008,
    "impulse_amp": 0.15,
    "noise_seed": 101
  },
  {
    "name": "suburban_combat_zone",
    "description": "Quiet residential backdrop broken by high-amplitude, irregular impulse noise simulating distant explosions or structural collapses.",
    "wind_rms": 0.03,
    "wind_gust_prob": 0.002,
    "wind_gust_amp": 0.1,
    "traffic_rms": 0.01,
    "impulse_prob": 0.005,
    "impulse_amp": 0.85,
    "noise_seed": 777
  },
  {
    "name": "open_woodland_calm",
    "description": "Baseline natural environment with very light ambient breeze, zero traffic, and rare organic impulse noises like snapping twigs.",
    "wind_rms": 0.02,
    "wind_gust_prob": 0.001,
    "wind_gust_amp": 0.05,
    "traffic_rms": 0.0,
    "impulse_prob": 0.0001,
    "impulse_amp": 0.1,
    "noise_seed": 12
  },
  {
    "name": "highway_perimeter",
    "description": "Constant, heavy broadband rushing sound from a nearby motorway with steady wind and minimal impulsive events.",
    "wind_rms": 0.05,
    "wind_gust_prob": 0.003,
    "wind_gust_amp": 0.12,
    "traffic_rms": 0.12,
    "impulse_prob": 0.0002,
    "impulse_amp": 0.2,
    "noise_seed": 2026
  }
]

sims = [
  {
    "name": "sim_standard_clean",
    "description": "Standard high-fidelity acoustic simulation configuration running at a 16 kHz sampling rate under nominal ambient temperature and sound propagation speed.",
    "fs": 16000,
    "sound_speed": 343.0,
    "n_rir_snapshots": 16
  }
]


duration_s = 30.0
labels = ["approaching", "flyby", "hover"]
speeds = [4, 8, 12, 15, 20, 25, 30, 35, 40, 45, 50]
azimuths = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350]


outdoors = [
  {
    "name": "urban_dense_downtown",
    "description": "High reflection canyon between commercial glass skyscrapers with low wall scattering and hard concrete ground reflections.",
    "width": 100.0,
    "depth": 100.0,
    "height": 100.0,
    "wall_material": "glass_window",
    "ground_material": "concrete_floor",
    "sky_material": "anechoic",
    "max_rir_order": 5,
    "air_absorption": True,
    "wall_scattering": 0.1,
    "ground_scattering": 0.05
  },
  {
    "name": "urban_old_town",
    "description": "Narrow, highly diffuse street alley lined with brick buildings creating complex acoustic reflections.",
    "width": 100.0,
    "depth": 100.0,
    "height": 100.0,
    "wall_material": "brickwork",
    "ground_material": "hard_surface",
    "sky_material": "anechoic",
    "max_rir_order": 4,
    "air_absorption": True,
    "wall_scattering": 0.4,
    "ground_scattering": 0.2
  },
  {
    "name": "urban_suburban",
    "description": "Wide street bordered by low-height wood structures with moderate wall scattering and an asphalt roadway floor.",
    "width": 100.0,
    "depth": 100.0,
    "height": 100.0,
    "wall_material": "plywood",
    "ground_material": "asphalt",
    "sky_material": "anechoic",
    "max_rir_order": 2,
    "air_absorption": True,
    "wall_scattering": 0.25,
    "ground_scattering": 0.1
  },
  {
    "name": "forest_dense_pine",
    "description": "High acoustic scattering and dense absorption from heavy canopy foliage and soft, pine-needle covered soil.",
    "width": 100.0,
    "depth": 100.0,
    "height": 100.0,
    "wall_material": "carpet_tufted",
    "ground_material": "carpet_tufted",
    "sky_material": "anechoic",
    "max_rir_order": 2,
    "air_absorption": True,
    "wall_scattering": 0.85,
    "ground_scattering": 0.6
  },
  {
    "name": "forest_sparse_woodland",
    "description": "Open clearing with distant scattered tree trunks and a standard natural grass floor showing low echo return order.",
    "width": 250.0,
    "depth": 250.0,
    "height": 50.0,
    "wall_material": "cork_tiles",
    "ground_material": "grass",
    "sky_material": "anechoic",
    "max_rir_order": 1,
    "air_absorption": True,
    "wall_scattering": 0.5,
    "ground_scattering": 0.3
  }
]

mic_arrays = [
  {
    "name": "circular_omni_8ch_compact",
    "description": "Compact 8-channel circular microphone array using omnidirectional elements, ideal for uniform 360-degree spatial audio capture.",
    "n_mics": 8,
    "center": [60.0, 60.0, 1.8],
    "mic_mode": "omnidirectional",
    "radius": 0.05,
    "cardioid_p": 0.5
  },
  {
    "name": "circular_cardioid_8ch_compact",
    "description": "Compact 8-channel circular microphone array using directional cardioid elements pointing outward to maximize spatial separation.",
    "n_mics": 8,
    "center": [60.0, 60.0, 1.8],
    "mic_mode": "directional",
    "radius": 0.05,
    "cardioid_p": 0.5
  }
]

drones = [
  {
    "name": "quadcopter_commercial_standard",
    "description": "Standard 5-inch commercial drone at hover speed with prominent mid-frequency motor noise",
    "rotor_base_hz": 150.0,
    "n_harmonics": 6,
    "harmonic_decay": 0.55,
    "source_rms": 0.7
  },
  {
    "name": "mini_fpv_high_rpm",
    "description": "Small racing drone operating at very high RPM, causing a piercing, high-pitched whine",
    "rotor_base_hz": 280.0,
    "n_harmonics": 8,
    "harmonic_decay": 0.65,
    "source_rms": 0.5
  },
  {
    "name": "heavy_lift_octocopter",
    "description": "Large industrial drone carrying a heavy payload, creating low-frequency, deep blade hums",
    "rotor_base_hz": 85.0,
    "n_harmonics": 10,
    "harmonic_decay": 0.45,
    "source_rms": 1.2
  },
  {
    "name": "fixed_wing_uav",
    "description": "Fixed-wing surveillance drone cruising at a stable, continuous motor speed",
    "rotor_base_hz": 120.0,
    "n_harmonics": 5,
    "harmonic_decay": 0.5,
    "source_rms": 0.6
  },
  {
    "name": "stealth_low_noise",
    "description": "Drone equipped with aerodynamic, low-noise propellers reducing high-frequency harmonic propagation",
    "rotor_base_hz": 160.0,
    "n_harmonics": 3,
    "harmonic_decay": 0.25,
    "source_rms": 0.3
  },
  {
    "name": "shahed_136_loitering_moped",
    "description": "MD-550 two-stroke internal combustion engine. Characterised by an aggressive, low-frequency 'moped' buzz with massive acoustic propagation and long harmonic chains.",
    "rotor_base_hz": 72.0,
    "n_harmonics": 15,
    "harmonic_decay": 0.78,
    "source_rms": 2.5
  },
  {
    "name": "orlan_10_recon_uav",
    "description": "Gasoline-powered fixed-wing reconnaissance drone. Distinct four-stroke piston engine hum with heavy low-frequency harmonics and moderate acoustic dampening.",
    "rotor_base_hz": 95.0,
    "n_harmonics": 10,
    "harmonic_decay": 0.62,
    "source_rms": 1.4
  },
  {
    "name": "baba_yaga_heavy_bomber_hexacopter",
    "description": "Large agricultural conversion octo/hexacopter used for night operations. Extreme low-pitch, high-torque rotor thrumming carrying immense sound energy.",
    "rotor_base_hz": 55.0,
    "n_harmonics": 12,
    "harmonic_decay": 0.50,
    "source_rms": 2.1
  },
  {
    "name": "switchblade_300_kamikaze",
    "description": "Miniature electric loitering munition. High-RPM electric pusher prop generating a faint but highly piercing, high-frequency acoustic needle signature.",
    "rotor_base_hz": 210.0,
    "n_harmonics": 6,
    "harmonic_decay": 0.40,
    "source_rms": 0.4
  },
  {
    "name": "rq_11_raven_hand_launched",
    "description": "Lightweight tactical electric recon drone. Runs quietly at high operating altitudes with minimal fundamental signature and fast harmonic dissipation.",
    "rotor_base_hz": 175.0,
    "n_harmonics": 4,
    "harmonic_decay": 0.32,
    "source_rms": 0.25
  },
  {
    "name": "bayraktar_tb2_tactical_uav",
    "description": "Rotax 912 internal combustion engine with a variable-pitch pusher propeller. Complex acoustic spectrum combining engine firing frequency and high-order blade-vortex interaction tones.",
    "rotor_base_hz": 115.0,
    "n_harmonics": 14,
    "harmonic_decay": 0.70,
    "source_rms": 1.9
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


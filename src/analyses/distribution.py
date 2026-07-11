import glob
import json
import os
from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

class DataDistAnalyzer():
    
    def __init__(self, data_dir:str = "datasets"):
        self.data_dir = Path(data_dir)
        self.metadata_files=[]
        self.load_files(data_dir=self.data_dir)
    

    def load_samples_field(self, field):
        values = []
        
        for file in tqdm(self.metadata_files, desc="Reading JSON files", unit="file"):
            with open(file) as f:
                data = json.load(f)

            for sample in data.get("samples", []):
                if field in sample:
                    values.append(sample[field])

        return values

    def load_files(self, data_dir:Path): 
        for folder in sorted(os.listdir(data_dir)):
            folder_path = os.path.join(data_dir, folder)
            metadata_files = glob.glob(
                            os.path.join(folder_path, '**', '*.json'),
                            recursive=True)
            self.metadata_files = metadata_files
            
            if len(self.metadata_files) == 0:
                print("Metadata files not found")
                                    
   
    def show_distribution(self, values):
        # Calculate the distribution of distances
        unique_values, counts = np.unique(values, return_counts=True)
        distribution = dict(zip(unique_values, counts))
        
        return distribution
    
    def plot_distribution(self, values, title="Distribution", label="Values", kde_samples_count = 20000):
        s = pd.Series(values)
        kde_samples = min(kde_samples_count, len(s))
        print(f"Number of samples: {len(s)}")
        print(f"distribution of {label}:")
        print(s.describe().round(2))
        print("Skewness:", s.skew())
        plt.figure(figsize=(8,5))
        s.plot(kind="hist", bins=40, density=True, alpha=0.5)
        s.sample(kde_samples).plot(kind="kde")
        plt.xlabel(label)
        plt.title(title)
        plt.grid(True)
        plt.show()
    
    def show_distance_distribution(self):
        values = self.load_samples_field("distance_m")
        self.plot_distribution(values, title="Distance Distribution", label="Distance (m)")

    def show_azimuth_distribution(self):
        values = self.load_samples_field("azimuth_deg")
        self.plot_distribution(values, title="Azimuth Distribution", label="Azimuth (deg)")

    def show_elevation_distribution(self):
        values = self.load_samples_field("elevation_deg")
        self.plot_distribution(values, title="Elevation Distribution", label="Elevation (deg)")
        
    def show_velocity_distribution(self):
        values = self.load_samples_field("velocity_ms")
        velocities = np.array(values)
        v = np.linalg.norm(velocities, axis=1)
        self.plot_distribution(v, title="Velocity Distribution", label="Velocities")
    
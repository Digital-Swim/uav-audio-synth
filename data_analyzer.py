

from src.analyses.distribution import DataDistAnalyzer

def alalyse_distribution():
    analyzer = DataDistAnalyzer()
    #analyzer.show_distance_distribution()
    analyzer.show_azimuth_distribution()
    #analyzer.show_elevation_distribution()

if __name__ == "__main__":
    alalyse_distribution()


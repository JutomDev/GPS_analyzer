from gps_analyzer import CSVAnalyzer


def main() -> None:
    """Main execution pipeline for GPS analysis."""
    # Path to test dataset
    csv_file_path = 'dane/gps_test.csv' 

    print("--- Starting GPS analysis ---")
    
    # 1. Initialize CSV analyzer
    analyzer = CSVAnalyzer(file_path=csv_file_path)

    # 2. Load and clean raw points
    try:
        analyzer.load_and_clean_data()
    except FileNotFoundError:
        print(f"ERROR: Could not find {csv_file_path}. Please check data path.")
        return

    # 3. Kinematics, spoofing/speed anomaly detection, and trajectory smoothing
    analyzer.calculate_kinematics_and_smooth(max_speed_kmh=150.0)

    # 4. Detect stationary stops using spatial clustering (DBSCAN)
    # eps_meters: maximum search radius for stop points
    # min_samples: minimum points required to form a stop cluster
    analyzer.detect_stops(eps_meters=25.0, min_samples=5)

    # 5. Visualization and CSV export
    print("Generating visualization plot...")
    analyzer.plot_results()
    analyzer.export_clean_csv(output_filename='czyste_dane_gps.csv')

    print("--- Analysis finished successfully ---")


if __name__ == "__main__":
    main()

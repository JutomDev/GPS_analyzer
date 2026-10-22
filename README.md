# GPS Trajectory Analyzer

A university coursework project for processing, filtering, and analyzing raw GPS telemetry data.

## Overview

This project provides a simple data pipeline to clean GPS tracks and detect stops:
* **Data Cleaning:** Parses timestamps and removes invalid zero coordinates.
* **Anomaly Detection:** Flags GPS spoofing and speed spikes using the Haversine distance formula.
* **Trajectory Smoothing:** Applies a Savitzky-Golay filter to reduce receiver noise.
* **Stop Detection:** Groups stop points using DBSCAN density-based clustering.
* **Output:** Exports clean data to CSV and generates a trajectory plot in PNG.

## Project Structure

* `dane/gps_test.csv` - Sample raw GPS input data.
* `gps_analyzer.py` - Core analysis classes (`BaseGPSAnalyzer`, `CSVAnalyzer`).
* `main.py` - Execution pipeline script.
* `requirements.txt` - Project dependencies.

## Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script:
```bash
python main.py
```

### Parameters in `main.py`
* `max_speed_kmh`: Speed threshold in km/h for flagging spoofing anomalies (default: `150.0`).
* `eps_meters`: Maximum cluster radius in meters for stop detection (default: `25.0`).
* `min_samples`: Minimum number of points required to form a stop (default: `5`).

## Output Files

* `czyste_dane_gps.csv` - Cleaned GPS points with calculated speeds, smoothed coordinates, and stop flags.
* `wynik_analizy.png` - Visual plot displaying the smoothed trajectory, stop clusters, and detected anomalies.

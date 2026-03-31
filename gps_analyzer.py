import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

import numpy as np
from scipy.signal import savgol_filter
from sklearn.cluster import DBSCAN

# Konfiguracja Matplotlib dla środowisk bez interfejsu graficznego
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt


class BaseGPSAnalyzer:
    """
    Bazowa klasa dla analizatorów GPS
    Zawiera wspólną logikę obliczeń i wizualizacji, niezależną od formatu źródłowego
    """

    def __init__(self, file_path: str):
        """
        Inicjalizuje bazowy analizator GPS
        """
        self.file_path: str = file_path
        self.data: List[Dict[str, Any]] = []

    def calculate_kinematics_and_smooth(self, max_speed_kmh: float = 150.0) -> None:
        """
        Oblicza dystans i prędkość między punktami
        Wykrywa anomalie spoofing i wygładza trajektorię filtrem Savitzkyego-Golaya
        """
        if len(self.data) < 2:
            print("Zbyt mało danych do obliczeń kinematycznych")
            return

        lats = np.array([d['GPS_Lat'] for d in self.data])
        lons = np.array([d['GPS_Lon'] for d in self.data])
        times = np.array([d['Time_ts'] for d in self.data])
        
        speeds = np.zeros(len(self.data))
        anomalies = np.zeros(len(self.data), dtype=bool)

        last_valid_idx = 0
        for i in range(1, len(self.data)):

            # jeśli czas przeskoczy przez północ różnica byłaby ujemna
            dt = times[i] - times[last_valid_idx]
            if dt < 0: dt += 86400.0
            if dt == 0: dt = 1.0

            lat1, lon1 = np.radians(lats[last_valid_idx]), np.radians(lons[last_valid_idx])
            lat2, lon2 = np.radians(lats[i]), np.radians(lons[i])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            # oblicza odległość między dwoma punktami na kuli - 6371000.0 to średni promień Ziemi w metrach
            a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
            c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
            dist_meters = 6371000.0 * c
            
            speed_kmh = (dist_meters / dt) * 3.6
            speeds[i] = speed_kmh
            
            if speed_kmh > max_speed_kmh:
                anomalies[i] = True
            else:
                last_valid_idx = i

        for i, d in enumerate(self.data):
            d['is_anomaly'] = bool(anomalies[i])
            d['Speed_kmh'] = float(speeds[i])

        valid_indices = [i for i, is_anom in enumerate(anomalies) if not is_anom]
        if len(valid_indices) > 3:
            window_length = min(15, len(valid_indices))
            if window_length % 2 == 0: window_length -= 1
            
            # Filtr Savitzkyego - wygładza punkty
            smooth_lats = savgol_filter(lats[valid_indices], window_length=window_length, polyorder=3)
            smooth_lons = savgol_filter(lons[valid_indices], window_length=window_length, polyorder=3)
            
            for idx, s_lat, s_lon in zip(valid_indices, smooth_lats, smooth_lons):
                self.data[idx]['Smooth_Lat'] = s_lat
                self.data[idx]['Smooth_Lon'] = s_lon
        else:
            for idx in valid_indices:
                self.data[idx]['Smooth_Lat'] = self.data[idx]['GPS_Lat']
                self.data[idx]['Smooth_Lon'] = self.data[idx]['GPS_Lon']

        print(f"Zakończono obliczenia. Wykryto {sum(anomalies)} anomalii spoofing") 

    def detect_stops(self, eps_meters: float = 20.0, min_samples: int = 10) -> None:
        """ Wykrywa postoje używając klasteryzacji DBSCAN"""
        valid_indices = [i for i, d in enumerate(self.data) if not d['is_anomaly'] and 'Smooth_Lat' in d]
        if not valid_indices: return

        coords = np.radians(np.array([[self.data[i]['Smooth_Lat'], self.data[i]['Smooth_Lon']] for i in valid_indices]))

        # algorytm klasteryzacji oparty na gęstości, który grupuje punkty znajdujące się blisko siebie
        dbscan = DBSCAN(eps=eps_meters/6371000.0, min_samples=min_samples, algorithm='ball_tree', metric='haversine')
        labels = dbscan.fit_predict(coords)

        stops_count = 0
        for idx, label in zip(valid_indices, labels):
            if label != -1:
                self.data[idx]['is_stop'] = True
                stops_count += 1
        print(f"Zakończono detekcję postojów. Oznaczono {stops_count} punktów jako postój")

    def export_clean_csv(self, output_filename: str) -> None:
        """ Eksportuje odfiltrowane dane do pliku CSV"""
        clean_data = [d for d in self.data if not d.get('is_anomaly', False)]
        if not clean_data: return

        fieldnames = list(clean_data[0].keys())
        with open(output_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(clean_data)
        print(f"Pomyślnie wyeksportowano {len(clean_data)} punktów do: {output_filename}")

    def plot_results(self) -> None:
        """ Generuje wykresy i zapisuje do pliku PNG """
        traj_lons, traj_lats = [], []
        stop_lons, stop_lats = [], []
        anom_lons, anom_lats = [], []

        for d in self.data:
            if d['is_anomaly']:
                anom_lons.append(d['GPS_Lon'])
                anom_lats.append(d['GPS_Lat'])
            elif 'Smooth_Lon' in d:
                traj_lons.append(d['Smooth_Lon'])
                traj_lats.append(d['Smooth_Lat'])
                if d.get('is_stop'):
                    stop_lons.append(d['Smooth_Lon'])
                    stop_lats.append(d['Smooth_Lat'])

        plt.figure(figsize=(12, 8))
        if traj_lons: plt.plot(traj_lons, traj_lats, color='blue', linewidth=2, label='Trajektoria', alpha=0.7)
        if stop_lons: plt.scatter(stop_lons, stop_lats, color='red', s=30, label='Postoje', zorder=5)
        if anom_lons: plt.scatter(anom_lons, anom_lats, color='black', marker='x', s=50, label='Anomalie', zorder=6)

        plt.title('Analiza Danych GPS', fontsize=16)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.legend(loc='best')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.gca().set_aspect('equal', adjustable='datalim')
        plt.tight_layout()
        
        output_file = 'wynik_analizy.png'
        plt.savefig(output_file)
        print(f"Wykres zapisano do: {output_file}")
        plt.close()


class CSVAnalyzer(BaseGPSAnalyzer):
    """ Analizator dla plików w formacie CSV """

    def _parse_time(self, time_str: str) -> float:
        """ Zamienia tekstowy czas na sekundy"""
        time_str = time_str.strip()
        if not time_str: return 0.0
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            return dt.timestamp()
        except ValueError:
            try:
                parts = time_str.split(':')
                if len(parts) == 3:
                    return int(parts[0]) * 3600.0 + int(parts[1]) * 60.0 + float(parts[2])
            except (ValueError, TypeError, IndexError): pass
        return 0.0

    def _safe_float(self, val: Any) -> Optional[float]:
        """ Konwersja na float """
        try: return float(val)
        except (ValueError, TypeError): return None

    def load_and_clean_data(self) -> None:
        """ Wczytuje i czyści dane z pliku csv """
        try:
            with open(self.file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                raw_data = list(reader)

            parsed_data = map(lambda row: {
                'Time_ts': self._parse_time(row.get('Time', '')),
                'GPS_Lat': self._safe_float(row.get('GPS_Lat')),
                'GPS_Lon': self._safe_float(row.get('GPS_Lon')),
                'GPS_Alt': self._safe_float(row.get('GPS_Alt'))
            }, raw_data)

            filtered_data = filter(lambda row: 
                row['GPS_Lat'] is not None and row['GPS_Lon'] is not None and 
                row['GPS_Lat'] != 0.0 and row['GPS_Lon'] != 0.0, parsed_data)

            final_data = map(lambda row: {**row, 'is_stop': False, 'is_anomaly': False}, filtered_data)
            self.data = list(final_data)

            print(f"Wczytano dane CSV - Poprawnych punktów: {len(self.data)}")
        except FileNotFoundError:
            print(f"Błąd: Nie znaleziono pliku {self.file_path}")
            raise
from gps_analyzer import CSVAnalyzer

def main():
    """
    Główna funkcja uruchomieniowa aplikacji.
    """
    # Ścieżka do pliku CSV
    csv_file_path = 'dane/gps_test.csv' 

    print("--- Rozpoczęcie analizy GPS ---")
    
    # 1. Inicjalizacja analizatora CSV
    analyzer = CSVAnalyzer(file_path=csv_file_path)

    # 2. Wczytywanie i czyszczenie danych
    try:
        analyzer.load_and_clean_data()
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku {csv_file_path}. Utwórz plik testowy i spróbuj ponownie.")
        return

    # 3. Obliczenia kinematyczne i wygładzanie
    # Parametr max_speed_kmh określa czułość na spoofing
    analyzer.calculate_kinematics_and_smooth(max_speed_kmh=150.0)

    # 4. Wykrywanie postojów
    # eps_meters: jak bardzo sygnał może pływać na postoju
    # min_samples: ile minimalnie punktów musi być w tym promieniu, by uznać to za postój
    analyzer.detect_stops(eps_meters=25.0, min_samples=5)

    # 5. Wizualizacja wyników
    print("Generowanie wykresu...")
    analyzer.plot_results()
    analyzer.export_clean_csv(output_filename='czyste_dane_gps.csv')

    print("--- Zakończono analizę ---")

if __name__ == "__main__":
    main()
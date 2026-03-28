import csv
import random
import math
from datetime import datetime, timedelta

def generuj_realistyczna_trase(nazwa_pliku):
    # Współrzędne krańcowe
    start_lat, start_lon = 53.0137, 18.5984  # Toruń
    end_lat, end_lon = 54.3520, 18.6466    # Gdańsk
    
    # Obszar spoofingu (Kaliningrad)
    spoof_center_lat, spoof_center_lon = 54.7104, 20.4522
    
    liczba_punktow = 250
    start_time = datetime.strptime('10:00:00', '%H:%M:%S')
    obecny_czas = start_time
    dane_csv = []
    
    # Funkcja symulująca szum (niedokładność GPS)
    def dodaj_szum(lat, lon, poziom_szumu=0.0003):
        # Rozrzut losowy z równomiernego rozkładu
        return lat + random.uniform(-poziom_szumu, poziom_szumu), lon + random.uniform(-poziom_szumu, poziom_szumu)
    
    # Symulacja zakrzywionej trajektorii drogi
    def punkt_na_krzywej(postep):
        # Najpierw zwykła prosta interpolacja (od A do B)
        base_lat = start_lat + (end_lat - start_lat) * postep
        base_lon = start_lon + (end_lon - start_lon) * postep
        
        # Dodajemy wybrzuszenie (łuk) na wschód/zachód używając sinusa
        magnituda_krzywizny = 0.08  # Jak bardzo trasa odstaje od linii prostej
        zakrzywiony_lon = base_lon + math.sin(postep * math.pi) * magnituda_krzywizny
        
        return base_lat, zakrzywiony_lon

    aktualny_lat, aktualny_lon = start_lat, start_lon
    
    # Inicjalizacja postępu drogi
    ilosc_krokow_jazdy = 160  # Punkty, w których faktycznie się poruszamy
    krok_postepu = 1.0 / ilosc_krokow_jazdy
    obecny_postep = 0.0

    print(f"Generowanie wysoce realistycznej trajektorii ({liczba_punktow} punktów)...")

    for i in range(liczba_punktow):
        # Domyślna lekko zmieniająca się wysokość
        alt = 50.0 + random.uniform(-5.0, 5.0) 
        
        # 1. Postój 1 (Korek na bramkach autostradowych)
        if 40 <= i <= 55:
            # Duży szum stacjonarny - obiekt stoi, GPS pływa
            lat, lon = dodaj_szum(aktualny_lat, aktualny_lon, 0.0004)
            
        # 2. Postój 2 (MOP - Stacja Benzynowa)
        elif 100 <= i <= 120:
            lat, lon = dodaj_szum(aktualny_lat, aktualny_lon, 0.0003)
            
        # 3. Postój 3 (Światła przed wjazdem do Gdańska)
        elif 210 <= i <= 220:
            lat, lon = dodaj_szum(aktualny_lat, aktualny_lon, 0.0005)
            
        # 4. Agresywny Spoofing (Kaliningrad + ogromny szum)
        elif 160 <= i <= 175:
            # Rozrzut rzędu kilku kilometrów w różnych miejscach w okolicach Kaliningradu
            lat, lon = dodaj_szum(spoof_center_lat, spoof_center_lon, 0.05) 
            alt = random.uniform(-200, 8000) # Nierealne skoki wysokości (wariujący wysokościomierz GPS)
            
        # 5. Normalna jazda po łuku
        else:
            bazowy_lat, bazowy_lon = punkt_na_krzywej(obecny_postep)
            # Bardzo mały szum podczas jazdy (lepsze śledzenie wektora przez moduł GPS)
            lat, lon = dodaj_szum(bazowy_lat, bazowy_lon, 0.0001) 
            
            # Zapamiętujemy pozycję na wypadek zatrzymania
            aktualny_lat, aktualny_lon = lat, lon
            # Posuwamy się do przodu na trasie
            obecny_postep += krok_postepu

        # Format czasu 
        czas_str = obecny_czas.strftime('%H:%M:%S')
        dane_csv.append([czas_str, round(lat, 6), round(lon, 6), round(alt, 1)])
        
        # Realistyczny interwał zapisu logów: od 4 do 6 sekund odstępu
        obecny_czas += timedelta(seconds=random.randint(30, 60))

    with open('torun_gdansk_realistic.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Time', 'GPS_Lat', 'GPS_Lon', 'GPS_Alt'])
        writer.writerows(dane_csv)
        
    print(f"Zakończono! Zapisano plik: {nazwa_pliku}")

# Uruchomienie skryptu
if __name__ == "__main__":
    generuj_realistyczna_trase('torun_gdansk_realistic.csv')
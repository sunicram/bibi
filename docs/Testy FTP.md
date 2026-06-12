# Najprostsze Testy do Oszacowania FTP
*Metody wyznaczania Functional Threshold Power możliwe do wykonania na trenażerze lub w terenie*

---

## 1. Test Rampy (Ramp Test) - *Najprostszy i najkrótszy*
Jest to standard w aplikacjach takich jak Zwift, TrainerRoad czy Rouvy. Nie wymaga wcześniejszego planowania tempa (pacingu). Jedziesz po prostu do momentu, w którym nie dasz rady obrócić korbą.

*   **Zastosowanie:** Najlepszy wybór po chorobie, ponieważ maksymalny wysiłek trwa tylko kilkadziesiąt sekund na samym końcu, a nie przez kilkanaście minut.
*   **Przebieg:**
    1. Rozgrzewka (ok. 5-10 minut lekkiej jazdy).
    2. Start testu z niskiej mocy (np. 100W).
    3. Moc rośnie automatycznie (w trybie ERG) lub zmieniasz ją ręcznie o **15-20W co każdą minutę**.
    4. Kręcisz z równą kadencją tak długo, aż nastąpi odmowa mięśniowa (nie będziesz w stanie utrzymać kadencji).
*   **Wzór na FTP:**
    $$\text{FTP} = \text{Moc z ostatniej ukończonej minuty} \times 0.75$$
    *(Aplikacje automatycznie doliczają też sekundy z niepełnej, ostatniej minuty)*.
    
    Jak wygląda idealny protokół Testu Rampy (Standard)Jeśli Twoje dotychczasowe FTP wynosiło np. 250W, test zaczyna się bardzo nisko, a progi rosną zazwyczaj o 15W lub 20W co 1 minutę:Rozgrzewka: 5 minut na poziomie 100-130W (czysta krew w mięśniach).Krok 1: Start testu od 150W (60% dotychczasowego FTP).Kolejne kroki: Co dokładnie 60 sekund opór rośnie o 15W.Punkt przełomowy: Mniej więcej w okolicach 11-12 minuty zrównasz się ze swoim starym FTP. Każda kolejna minuta to już wchodzenie na wyższe obroty (VO2 Max).Koniec: Test kończy się w ułamku sekundy, gdy kadencja spada poniżej np. 60 RPM i nie jesteś w stanie przepchnąć korby.Dlaczego warto na stałe przejść na Ramp Test?Powtarzalność: Test eliminuje czynnik ludzki. Nie da się go "źle pojechać". Wynik zależy wyłącznie od Twojej aktualnej formy fizycznej, a nie od strategii.Mniejszy koszt regeneracyjny: Po teście 20-minutowym jesteś "zajechany" na 2 dni. Po teście rampy, ze względu na bardzo krótki czas trwania maksymalnego długu tlenowego, możesz zrobić normalny, mocny trening już następnego dnia.Idealny pod trenażery SMART: Włączasz tryb ERG, patrzysz przed siebie i po prostu kręcisz. Trenażer sam dba o to, żeby waty się zgadzały, niezależnie od Twojej kadencji.Na co musisz uważać? (Wada Testu Rampy)Test rampy faworyzuje zawodników z bardzo mocnym "beztlenem" (generujących wysokie waty w krótkim czasie).Jeśli jesteś typem sprintera, test rampy może lekko zawyżyć Twoje realne FTP (bo uciągniesz końcówkę na długu beztlenowym).Jeśli jesteś typem diesel / maratończyk, test rampy może minimalnie zaniżyć Twoje FTP, bo Twoje serce i płuca mogą znieść godzinę ciężkiej jazdy, ale nogi "odetnie" przy nagłym skoku watów.

---

## 2. Klasyczny Test 20-minutowy - *Standard drogowy*
Wymaga dobrego rozłożenia sił (pacingu) – musisz jechać na granicy swoich możliwości przez równe 20 minut.

*   **Zastosowanie:** Bardziej miarodajny dla kolarzy długodystansowych, ale bardzo obciążający psychicznie i fizycznie.
*   **Przebieg:**
    1. Solidna rozgrzewka (15 minut).
    2. Odpalenie (tzw. czyszczenie przedtestowe): 5 minut bardzo mocnej jazdy (w strefie VO2 Max), aby usunąć zapasy energii beztlenowej.
    3. Odpoczynek: 10 minut luźnego kręcenia.
    4. **Główna część:** 20 minut jazdy na absolutnie maksymalną, równą średnią moc, jaką jesteś w stanie utrzymać.
*   **Wzór na FTP:**
    $$\text{FTP} = \text{Średnia moc z 20 minut} \times 0.95$$

---

## 3. Estymacja z "Jazdy z życia" (Garmin / Wahoo / Strava)
Jeśli nie chcesz robić dedykowanego testu po chorobie, nowoczesne komputery rowerowe i aplikacje (np. Strava, Intervals.icu) automatycznie szacują Twoje FTP.

*   **Jak to działa:** Algorytmy analizują Twoją krzywą mocy (Power Curve) z ostatnich 6-90 dni.
*   **Wzór matematyczny:** Szukają Twojego maksymalnego wysiłku z odcinka **od 30 do 50 minut** i przyjmują tę średnią moc jako Twoje aktualne FTP.

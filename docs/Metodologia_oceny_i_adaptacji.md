# Metodologia Oceny Treningu i Adaptacji w Bibi AI Coach

Ten dokument definiuje uzgodnione założenia dotyczące pozyskiwania informacji zwrotnych od użytkownika, dostępnych metodologii adaptacyjnych oraz obliczania jakości wykonania jednostek treningowych (TEQ), które stanowią fundament silnika adaptacyjnego platformy Bibi.

---

## 1. Trzy Metodologie Adaptacyjne do Wyboru Użytkownika

Przed wygenerowaniem planu użytkownik wybiera jedną z trzech metodologii sprzężenia zwrotnego i adaptacji planu (która współgra z wybranym modelem dystrybucji obciążeń, np. Polarized czy Sweet Spot):

### Metodologia A: Samopoczucie i RPE (Subiektywna / "No-Gear")
*   **Dla kolarzy bez specjalistycznego sprzętu** (brak mierników mocy/tętna).
*   **Główna cecha:** Oparta wyłącznie na odczuciach. Jakość wykonania (TEQ) jest szacowana na podstawie czasu trwania jazdy w relacji do planu.
*   **Adaptacja:** Opiera się głównie na analizie trendów z 3 pytań feedbackowych. Jeśli wskaźnik samopoczucia przed treningiem spada (< 3), system skraca i ułatwia kolejne zaplanowane jazdy.

### Metodologia B: Pomiar Mocy + Tętno + RPE (Precyzyjna / "Naukowa")
*   **Dla kolarzy trenujących z miernikiem mocy i paskiem tętna (HR).**
*   **Główna cecha:** Maksymalna naukowa kontrola obciążeń. Jakość wykonania (TEQ) wyliczana jest precyzyjnie za pomocą 10-sekundowego wygładzania mocy (10s SMA).
*   **Adaptacja:** Analizuje korelację mocy, tętna (np. dryf tętna/decoupling) oraz RPE. Wykrywa niedoszacowane FTP (gdy moc jest wysoka, a tętno i RPE niskie) lub kumulację zmęczenia chronicznego (spadek HRV i wysokie HR przy niskiej mocy).

### Metodologia C: Autonomiczne Przerwy + RPE (Elastyczna / "Autoregulacja")
*   **Dla kolarzy ceniących elastyczność i autonomię w sesjach interwałowych (HIIT).**
*   **Główna cecha:** Użytkownik sam decyduje o długości przerw wypoczynkowych w trakcie trwania interwałów na podstawie odczuć.
*   **Adaptacja:** System monitoruje czas trwania przerw dobieranych przez użytkownika. Jeśli kolarz drastycznie wydłuża przerwy, system odczytuje to jako oznakę zmęczenia i w kolejnych sesjach zmniejsza liczbę interwałów lub skraca ich czas. Średnia moc interwału jest porównywana z celem jako pojedynczy blok.

---

## 2. Minimalistyczny Wywiad Po-Treningowy (Feedback)

Aby zminimalizować wysiłek użytkownika, informacje zwrotne są pozyskiwane bezpośrednio z **opisu (notatek) aktywności** synchronizowanej z licznika/zegarka (Garmin Connect, Strava itp.) do platformy **Intervals.icu**.

### Format wpisu (notatki):
Użytkownik na końcu opisu dodaje tag o strukturze:
`bb: [samopoczucie przed]/[trudność po]/[zapas sił]`

Dopuszczalne separatory: ukośniki `/`, spacje, myślniki `-` lub przecinki `,` (np. `bb: 4/2/2` lub `bb 4 2 2`).

### Definicje pytań i wartości:
1. **Samopoczucie przed treningiem (Skala 1-5):**
   * `1` – Niezdolny (trening nie został wykonany ze względu na chorobę, kontuzję lub brak czasu)
   * `2` – Słabe
   * `3` – Średnie
   * `4` – Dobre
   * `5` – Bardzo dobre
2. **Ocena trudności treningu po jego zakończeniu (Skala 1-3):**
   * `1` – Za ciężki
   * `2` – Optymalny
   * `3` – Za lekki
3. **Zapas sił po treningu (Skala 1-2):**
   * `1` – Nie (brak zapasu, jazda "do odcięcia")
   * `2` – Tak (został zapas sił)

*Uwaga dot. wartości `1` (Niezdolny): Ze względu na brak wykonania treningu i tym samym brak pliku FIT, wartość ta jest przekazywana do systemu alternatywnym kanałem (kliknięcie przycisku na Telegramie lub w kalendarzu Web UI).*

---

## 3. Wskaźnik Jakości Wykonania (TEQ — Training Execution Quality)

Bibi ocenia jakość wykonania na podstawie precyzji trzymania się zadanej mocy. **Nie premiuje się jazdy mocniejszej ani słabszej niż zalecona.** Każde odchylenie obniża wynik TEQ (0-100%).

### Sposób kalkulacji mocy docelowej:

#### A. Dla etapów o długości $\ge$ 1 minuty (np. interwały VO2max/SST, rozjazdy, tlen):
* **Wygładzanie:** Dane mocy z pliku FIT są wygładzane za pomocą **10-sekundowej średniej kroczącej (10s SMA)** w celu wyeliminowania chwilowych zakłóceń (zmiany biegów, zrywy, dropy sygnału ANT+).
* **Bufor przejścia (Transition Buffer):** Pierwsze **10 sekund** każdego nowego etapu interwału jest wyłączone z naliczania kar. Pozwala to kolarzowi na ustabilizowanie kadencji i watów po zmianie intensywności.
* **Obliczanie błędu:** Odchylenia procentowe powyżej $P_{max}$ i poniżej $P_{min}$ sumują się w sekundowy wskaźnik błędu, który proporcjonalnie obniża całkowity wynik TEQ dla danej sesji.

#### B. Dla etapów o długości < 1 minuty (np. sprinty 15s, mikro-interwały 30/30s):
* Ze względu na opóźnienie (lag) średniej kroczącej, sekundy przejściowe nie są analizowane pojedynczo.
* Jakość etapu jest oceniana na podstawie **średniej mocy z całego czasu trwania interwału** – jeśli średnia mieści się w zadanym oknie tolerancji, interwał jest zaliczany jako w pełni poprawny (100% TEQ).

---

## 4. Logika Adaptacji (Silnik Decyzyjny)

Wartości TEQ oraz trójstopniowy kod `bb: X/Y/Z` są w ML Core kojarzone z obiektywną telemetrią (TSS, dryf tętna, zmęczenie chroniczne CTL/ATL/TSB):

* **FTP Underestimation (Wzrost formy):** Zgłoszenie kodu `X/3/2` (za lekko + zapas sił) przy niskim tętnie i poprawnym wykonaniu (TEQ > 90%) sugeruje potrzebę podniesienia FTP o 2-3%.
* **Accumulated Fatigue (Przetrenowanie):** Zgłoszenie kodu `2/1/1` (słabe przed + za ciężki + brak zapasu) skorelowane ze spadkiem HRV z nocy lub wysokim dryfem tętna (decoupling) automatycznie zamienia następne mocne jednostki na regenerację (Z1) lub wolne.
* **Overtraining Check (Ego-biking):** Niski wskaźnik TEQ wynikający z jazdy powyżej wyznaczonych watów (np. na treningu regeneracyjnym) skutkuje ostrzeżeniem od AI Coach i podwyższeniem szacowanego obciążenia ATL na kolejne dni w celu ochrony przed przeciążeniem.

---

## 5. Model Danych w PostgreSQL (Koncepcja Schematu)

W celu obsługi powyższych funkcjonalności, tabela `activities` w bazie danych PostgreSQL zostanie docelowo rozszerzona o następujące kolumny (odzwierciedlone w modelu SQLAlchemy w `app/models/plan.py`):

| Nazwa Kolumny | Typ Danych | Opis |
| :--- | :--- | :--- |
| `activity_notes` | `TEXT` / `VARCHAR` | Przechowuje pełną, surową notatkę/komentarz z pliku lub pobraną przez API z zewnętrznych serwisów (Garmin, Strava, Intervals.icu). |
| `feeling_before` | `INTEGER` (Nullable) | Wyekstrahowana wartość (1-5) określająca samopoczucie użytkownika przed rozpoczęciem treningu. |
| `difficulty_after` | `INTEGER` (Nullable) | Wyekstrahowana wartość (1-3) oceniająca trudność ukończonego treningu. |
| `reserve_forces` | `INTEGER` (Nullable) | Wyekstrahowana wartość (1-2) oznaczająca, czy po treningu kolarzowi pozostały zapasy sił (1: Nie, 2: Tak). |
| `teq_score` | `DOUBLE PRECISION` / `FLOAT` | Wyliczony wskaźnik Jakości Wykonania Treningu (0.0 - 100.0) na podstawie 10s SMA i średnich mocy w mikro-interwałach. |

---

## 6. Integracja Protokołu Powrotu po Chorobie (Illness Recovery Protocol)

Gdy w kalendarzu treningowym zostanie odnotowane zdarzenie **"Choroba" (Illness)** o czasie trwania $D$ dni, silnik adaptacyjny Bibi automatycznie wdraża program powrotu oparty na pliku `trening_kolarski_adaptacja_po_chorobie.md`.

### A. Zasady wdrożenia i ograniczenia obciążeń:
* **Czas trwania protokołu:** Trwa przez $2 \times D$ dni od momentu zakończenia infekcji (zasada "2 dni lżejszych za 1 dzień choroby").
* **Ograniczenie tygodniowego TSS:** W pierwszym tygodniu powrotu łączny cel stress score wynosi maksymalnie:
  $$TSS_{docelowy} \le TSS_{normalny} \times 0.40$$
* **Ograniczenie intensywności (Intensity Factor):** Wskaźnik IF dla pojedynczych jednostek nie może przekroczyć **0.65**.
* **Blokada stref:** Usunięcie wszystkich interwałów i kroków w strefach Z3, Z4, Z5 i wyższych. Dopuszczalna jest wyłącznie jazda w strefach Z1 (tlen/regeneracja) oraz Z2 (wytrzymałość).
* **Model Couzensa:** Wdrażanie objętości zaczyna się od maksymalnie 50% normalnego kilometrażu w pierwszym tygodniu, z przyrostem o 10-20% w kolejnych tygodniach.

### B. Weryfikacja telemetryczna w locie (Real-time & Post-activity Checks):
Podczas treningów w fazie powrotu, ML Core stale monitoruje dwa parametry bezpieczeństwa:
1. **Cardiac Drift (Pw:HR):** Obliczanie dryfu tętna do mocy pomiędzy pierwszą a drugą połową jazdy. Jeśli dryf wynosi **> 8-10%**, system oznacza to jako anomalię regeneracyjną, a AI Coach zaleca skrócenie lub ułatwienie kolejnej jazdy.
2. **Zasada 10 uderzeń:** Porównanie średniego tętna w strefie Z2 z historyczną średnią użytkownika (baseline). Jeśli tętno przy danej mocy Z2 wzrosło o **$\ge$ 10 uderzeń/min**, system w kolejnych zaplanowanych sesjach automatycznie obniża docelową moc o 20-30W w celu zabezpieczenia mięśnia sercowego przed nadmiernym obciążeniem.

### C. Przepływ kalendarza i przesuwanie tygodni (Calendar Shift):
W przypadku zachorowania w trakcie trwania bloku treningowego, silnik adaptacyjny reorganizuje kalendarz według następującego algorytmu:
1. **Wstrzymanie tygodnia:** Tydzień, w którym wystąpiła choroba, zostaje oznaczony jako przerwany/niekompletny.
2. **Powrót w środku tygodnia:** Jeśli kolarz wrazi do zdrowia w środku trwającego tygodnia kalendarzowego (np. w czwartek):
   * Do końca tego tygodnia (do niedzieli) system planuje wyłącznie **lekkie jazdy regeneracyjne (Z1/Z2)** zgodnie z limitem obciążeń protokołu.
3. **Powtórzenie i przesunięcie planu:** Od najbliższego poniedziałku system **powtarza w całości tydzień, na którym trening został przerwany**.
   * Wszystkie kolejne tygodnie planu zostają przesunięte w przyszłość o odpowiednią liczbę tygodni.
   * Jeśli czas trwania protokołu powrotu ($2 \times D$ dni) nakłada się na powtarzany tydzień, jego jednostki są odpowiednio modyfikowane (Z1/Z2, limit TSS/IF) przez silnik adaptacji tak długo, jak aktywny jest protokół.

---

## 7. Elastyczne Przesuwanie Treningów w Tygodniu (Dynamic Weekly Rescheduling & Discarding - DWRD)

Bibi pozwala na elastyczne przesunięcia jednostek wewnątrz jednego tygodnia treningowego (od poniedziałku do niedzieli), reagując na opuszczone sesje bez przesuwania całego planu o tydzień, o ile to możliwe.

### A. Parametry wejściowe z Onboardingu:
1. **Liczba jazd w tygodniu:** np. 4 jazdy.
2. **Domyślne dni treningowe:** np. poniedziałek, środa, sobota, niedziela.
3. **Dzień długiej jazdy (Baza):** np. niedziela.

### B. Algorytm Automatycznego Przesunięcia:
W przypadku niewykonania treningu w zadeklarowanym dniu (brak aktywności do końca dnia):
1. **Automatyczna migracja:** Niewykonany trening zostaje automatycznie przesunięty na kolejny dzień tygodnia.
2. **Kaskadowe przesunięcie:** Pozostałe zaplanowane treningi w tym tygodniu również przesuwają się o 1 dzień w przód, aby zachować odpowiednie odstępy i porządek.

### C. Redukcja jednostek w przypadku braku miejsca (Kolejka Priorytetów):
Jeśli opóźnienie sprawi, że w pozostałej części tygodnia nie ma fizycznej możliwości wykonania wszystkich zaplanowanych jazd (np. zostały 3 dni, a do zrobienia są 4 treningi), system **redukuje liczbę treningów** w danym tygodniu zgodnie z następującymi priorytetami (od najważniejszego):

1. **Priorytet 1 (Najwyższy) – Długa jazda tlenowa (Baza):**
   * Trening budujący bazę wytrzymałościową (zazwyczaj w niedzielę) **nigdy nie podlega usunięciu**. Jest to fundament objętościowy kolarza.
2. **Priorytet 2 (Średni) – Kluczowy bodziec (Key Stimulus):**
   * Przynajmniej jedna sesja interwałowa stymulująca wiodący aspekt fizjologiczny w danym mikrocyklu (np. interwały VO2max w fazie Build, Sweet Spot w fazie Base). Aspekt ten jest wiodącym celem danej fazy planu i musi zostać wykonany.
3. **Priorytet 3 (Najniższy) – Treningi uzupełniające:**
   * Jazdy regeneracyjne (Z1), standardowe jazdy tlenowe (Z2) lub tempo (Z3). W przypadku braku miejsca w tygodniu, są one usuwane jako pierwsze.

#### Przykład działania:
Plan zakłada: Pon (Interwały VO2max), Śr (Tempo), Sob (Z2), Niedz (Długa jazda) – faza *Build*.
* Użytkownik opuszcza trening w poniedziałek, wtorek i środę. Pierwszą jazdę realizuje dopiero w czwartek.
* Zostają 4 dni (Czw-Niedz) na zmieszczenie 4 treningów. Silnik uznaje to za konflikt regeneracyjny (brak dni wolnych) i redukuje plan do 3 jednostek.
* **Wynik redukcji:**
  * Usunięty zostaje trening uzupełniający: *Środa (Tempo)*.
  * Zostają zachowane: *Długa jazda* (Priorytet 1) oraz *Interwały VO2max* (Priorytet 2), a także *Jazda Z2* w sobotę.
  * Zaktualizowany tydzień: Czw (Interwały VO2max), Sob (Z2), Niedz (Długa jazda).

---

## 8. Standardy Stref Treningowych (Moc i Tętno)

W celu zachowania spójności analitycznej, platforma Bibi stosuje znormalizowany podział na strefy intensywności oparty na uznanych standardach naukowych:

### A. Strefy Mocy (Standard Andrew Coggana):
Wszystkie przedziały procentowe są liczone od aktualnego wskaźnika **FTP** (*Functional Threshold Power*):
*   **Z1 (Active Recovery / Regeneracja):** `< 55%` FTP
*   **Z2 (Endurance / Wytrzymałość tlenowa):** `56% – 75%` FTP
*   **Z3 (Tempo / Tempo):** `76% – 90%` FTP
*   **Z4 (Lactate Threshold / Próg mleczanowy):** `91% – 105%` FTP
*   **Z5 (VO2 Max / Pułap tlenowy):** `106% – 120%` FTP
*   **Z6 (Anaerobic Capacity / Beztlenowa):** `121% – 150%` FTP
*   **Z7 (Neuromuscular Power / Neuromięśniowa):** `> 150%` FTP

### B. Strefy Tętna (Standard Joe Friela):
Wszystkie przedziały procentowe są liczone od tętna na progu mleczanowym **LTHR** (*Lactate Threshold Heart Rate*):
*   **Z1 (Recovery / Regeneracja):** `< 85%` LTHR
*   **Z2 (Aerobic / Wytrzymałość):** `85% – 89%` LTHR
*   **Z3 (Tempo / Tempo):** `90% – 94%` LTHR
*   **Z4 (Threshold / Próg):** `95% – 102%` LTHR
*   **Z5 (Super-Threshold / Beztlenowa):** `> 102%` LTHR

### C. Zasada Nadrzędności Tętna w Anomalii Fizjologicznej:
*   **Moc** to obciążenie zewnętrzne (wykonana praca fizyczna).
*   **Tętno** to koszt wewnętrzny (reakcja układu krążenia).
*   *Reguła bezpieczeństwa:* W sytuacjach zaburzeń fizjologicznych (np. w fazie powrotu po chorobie lub głębokiego niedotrenowania/przemęczenia), **tętno staje się parametrem nadrzędnym**. Jeśli moc wskazuje na strefę wytrzymałości (Z2), a tętno ucieka do strefy progowej (Z3/Z4), system nakazuje kolarzowi obniżyć moc tak, aby utrzymać tętno w bezpiecznej, zaleconej strefie tlenowej (Z1/Z2).

---

## 9. Trzy Poziomy Decyzyjne AI i ML (Architektura Hierarchiczna)

Podejmowanie decyzji o modyfikacjach planów treningowych w Bibi opiera się na trójpoziomowej strukturze logicznej, łączącej silnik analityczny ML Core z dwoma modelami LLM (Trener i Recenzent):

```
+--------------------------------------------------------------+
| POZIOM 1: Decyzja o gotowości i kierunku obciążenia          |
| (Dane: ranny pomiar HRV, Resting HR, Wellness, Obciążenie)  |
| Wynik: Klasa Dnia (Zielony / Żółty / Czerwony)              |
+------------------------------+-------------------------------+
                               |
                               v
+--------------------------------------------------------------+
| POZIOM 2: Generowanie i parametryzacja konkretnej sesji       |
| (Moc, Tętno, RPE, warunki zewnętrzne, uciekający kalendarz) |
| Wynik: Plan jednostki (Waty docelowe, interwały, czas)       |
+------------------------------+-------------------------------+
                               |
                               v
+--------------------------------------------------------------+
| POZIOM 3: Weryfikacja bezpieczeństwa i spójności planu        |
| (AI Recenzent + ML Core, ocena trendów i ryzyka kontuzji)    |
| Wynik: Zatwierdzenie (Approve) / Modyfikacja / Odrzucenie   |
+--------------------------------------------------------------+
```

### 1. Poziom 1 – Gotowość do Wysiłku (Zdolność)
*   **Analiza:** Ranny pomiar HRV (Z-score delta), tętno spoczynkowe, ankieta wellness oraz historia obciążeń (7-28 dni).
*   **Decyzja:** Klasyfikacja dnia na zielony (pełne obciążenie), żółty/bursztynowy (redukcja) lub czerwony (regeneracja/rest).

### 2. Poziom 2 – Parametryzacja Jednostki (Wykonanie)
*   **Analiza:** Wyniki poprzednich treningów (wskaźnik TEQ, dryf tętna, tempo rozładowania baterii W'), a także warunki środowiskowe (temperatura, wilgotność, upał – które podnoszą fizjologiczny koszt pracy).
*   **Decyzja:** Model AI Trener generuje lub dostosowuje dzisiejszy trening (np. modyfikuje czas trwania przerw, zmienia moc docelową o kilka procent lub zamienia typ sesji).

### 3. Poziom 3 – Nadzór Bezpieczeństwa (Audyt)
*   **Analiza:** Ocena trendów fizjologicznego kosztu, ryzyka kontuzji, kumulacji monotonii oraz weryfikacja z deterministycznymi regułami bezpieczeństwa (Policy Engine).
*   **Decyzja:** Model AI Recenzent zatwierdza lub modyfikuje propozycje Trenera. Dba o to, by przy gorszych trendach regeneracyjnych nie narzucać kolarzowi sztywnych, ciężkich obciążeń.

---

## 10. Protokoły Wyznaczania FTP (Functional Threshold Power)

Do wyznaczania progu FTP na potrzeby stref intensywności, Bibi wykorzystuje trzy metody opisane w pliku `Testy FTP.md`:

### A. Test Rampy (Ramp Test) - Domyślny i Rekomendowany (Pierwszego Wyboru):
*   **Status w aplikacji:** Rekomendowany jako **podstawowy test pierwszego wyboru** dla wszystkich użytkowników (zarówno podczas onboardingu, jak i po chorobie/przerwie).
*   **Zastosowanie:** Optymalny na trenażerach interaktywnych (tryb ERG). Ma niski koszt regeneracyjny i nie wymaga planowania tempa (pacingu).
*   **Zaleta wdrożeniowa:** Eliminacja błędu ludzkiego (złego pacingu) oraz znacznie mniejsze obciążenie psychiczne kolarza. Klasyczny test 20-minutowy jest dla wielu amatorów zbyt trudny do poprawnego wykonania i bardzo wyczerpujący.
*   **Przebieg:** Po krótkiej rozgrzewce opór rośnie liniowo o **15-20W co minutę** aż do odmowy mięśniowej (spadek kadencji).
*   **Obliczenie FTP:**
    $$\text{FTP} = \text{Moc z ostatniej ukończonej minuty} \times 0.75$$
    *(silnik uwzględnia też sekundy z niepełnej ostatniej minuty)*.

### B. Klasyczny Test 20-minutowy (Standard drogowy / Zaawansowany):
*   **Status w aplikacji:** Opcjonalny (dla zaawansowanych kolarzy potrafiących idealnie rozłożyć siły).
*   **Zastosowanie:** Bardziej miarodajny dla kolarzy o profilu długodystansowym (diesel). Wymaga precyzyjnego pacingu.
*   **Przebieg:** Solidna rozgrzewka + 5 minut "czyszczenia beztlenowego" (max wysiłek VO2max) + 10 min odpoczynku + 20 minut jazdy na maksa.
*   **Obliczenie FTP:**
    $$\text{FTP} = \text{Średnia moc z 20 minut} \times 0.95$$

### C. Estymacja z Krzywej Mocy ("Jazda z życia"):
*   **Zastosowanie:** Pasywne monitorowanie poziomu FTP bez konieczności robienia testów.
*   **Algorytm (ML Core):** Analiza krzywej mocy (Power Curve) z ostatnich 6-90 dni w poszukiwaniu maksymalnego, stabilnego wysiłku trwającego **od 30 do 50 minut**. Średnia moc z tego przedziału jest przyjmowana jako estymowane FTP.

---

## 11. Zarządzanie Wagą i Składem Masy Ciała

W kolarstwie (szczególnie w terenie górzystym) **ostatecznym parametrem wydajności kolarza jest moc względna liczona w watach na kilogram masy ciała (W/kg)**. Cały proces optymalizacji treningowej w Bibi dąży do poprawy tego stosunku. W związku z tym, platforma ściśle monitoruje wagę kolarza oraz skład jego masy ciała w celu precyzyjniejszego modelowania stref, regeneracji i progresu.


### A. Wymagane Parametry i Pola w Modelu Danych:
W tabeli `profiles` (dane stałe) oraz w tabeli historycznych wpisów codziennych/tygodniowych (np. `wellness_daily`) system przechowuje:
*   `weight_kg` (`FLOAT`) – waga ciała kolarza.
*   `body_fat_pct` (`FLOAT`, Nullable) – zawartość tkanki tłuszczowej w %.
*   `muscle_mass_pct` (`FLOAT`, Nullable) – zawartość tkanki mięśniowej w %.
*   `water_pct` (`FLOAT`, Nullable) – zawartość wody w %.

### B. Metody Wprowadzania i Aktualizacji Danych:
1.  **Onboarding (Dane startowe):** Kolarz wprowadza swoją aktualną wagę (wymagane) oraz opcjonalnie skład ciała podczas ankiety początkowej.
2.  **Aktualizacja manualna (Raz w tygodniu):** System przypomina użytkownikowi raz w tygodniu (np. w poniedziałek rano za pośrednictwem Telegrama / powiadomienia w Web UI) o konieczności wejścia na wagę i zaktualizowania parametrów w profilu.
3.  **Dwukierunkowa Integracja z Intervals.icu (Automatyczna synchronizacja):**
    *   **Automatyczny Import:** Przy każdym pobieraniu danych wellness z Intervals.icu, Bibi odczytuje parametry wagi (`weight`) i zawartości tłuszczu (`fatPercent`). Pozwala to na automatyczne pobieranie odczytów, np. gdy użytkownik posiada inteligentną wagę (Garmin Index, Withings itp.) zintegrowaną ze swoim ekosystemem rowerowym.
    *   **Automatyczny Eksport:** Jeśli użytkownik zaktualizuje dane o swojej wadze ręcznie w aplikacji Bibi (Web UI / Telegram), silnik automatycznie wysyła zaktualizowane wartości z powrotem do Intervals.icu poprzez żądanie API (`POST /api/v1/athlete/{id}/wellness`), co gwarantuje pełną spójność danych w obu kierunkach.

---

## 12. Koncepcja Dwutygodniowych Mikrocykli Ukierunkowanych

Dotychczasowe pliki PRD opisywały tradycyjną periodyzację opartą na długich fazach (Base/Build/Peak). Wprowadzamy do koncepcji Bibi bardziej elastyczny podział: **dwutygodniowe mikrocykle tematyczne (skupione na jednej wiodącej zdolności)**. Podejście to jest uniwersalne i można je wdrożyć zarówno w dystrybucji spolaryzowanej (Polarized), jak i piramidalnej (Pyramidal).

### A. Struktura 2-tygodniowego bloku:
Każdy dwutygodniowy mikrocykl posiada ściśle określony cel fizjologiczny. W tym czasie kolarz wykonuje łącznie **4 kluczowe jednostki bodźcujące** (po 2 na tydzień) ukierunkowane na daną strefę. 

### B. Typy Mikrocykli Tematycznych (Zdolności):
1.  **Mikrocykl VO2 Max (Wydolność tlenowa):**
    *   *Cel:* Stymulacja pułapu tlenowego (Z5).
    *   *Główny trening:* Interwały np. 4x4 min na 110-120% FTP, przerwa 4 min.
2.  **Mikrocykl Threshold / SST (Próg mleczanowy / Sweet Spot):**
    *   *Cel:* Przesunięcie progu beztlenowego i budowanie wytrzymałości siłowej (Z3/Z4).
    *   *Główny trening:* Interwały np. 2x20 min na 90-95% FTP (Sweet Spot) lub 3x10 min na 100% FTP.
3.  **Mikrocykl Anaerobic (Moc beztlenowa):**
    *   *Cel:* Budowanie glikolizy beztlenowej i tolerancji na kwas mlekowy (Z6).
    *   *Główny trening:* Sesje typu 30/30s lub krótkie, maksymalne interwały 1-minutowe na 130-140% FTP.
4.  **Mikrocykl Base / Endurance (Wytrzymałość tlenowa / Baza):**
    *   *Cel:* Budowanie gęstości mitochondrialnej i sprawności metabolizmu tłuszczów (Z2).
    *   *Główny trening:* Długie jazdy tlenowe bez akcentów interwałowych o podwyższonej objętości.

### C. Kompatybilność z modelami dystrybucji obciążeń:

#### 1. W treningu spolaryzowanym (Polarized - 80/20):
*   **Zasada:** ~80% czasu treningu to strefa niska (Z1/Z2), a ~20% to strefa wysoka.
*   **Zastosowanie mikrocyklu:** Przez dwa tygodnie wspomniane 20% czasu wysokiej intensywności (akcenty) jest przeznaczane *wyłącznie* na strefę docelową danego mikrocyklu (np. w mikrocyklu VO2 Max robimy tylko interwały Z5, a w mikrocyklu Anaerobic – tylko interwały Z6). Pozostałe jazdy to wyłącznie tlen (Z2) i regeneracja (Z1).

#### 2. W treningu piramidalnym (Pyramidal):
*   **Zasada:** Rozkład obciążeń w kształcie piramidy (najwięcej Z2, mniej Z3/Z4, najmniej Z5).
*   **Zastosowanie mikrocyklu:** Akcenty jakościowe skupiają się na strefie wiodącej oraz strefach sąsiadujących (np. w mikrocyklu Threshold/SST kładziemy nacisk na Z3 i Z4, a w mikrocyklu VO2 Max – na Z4 i Z5). Pozwala to na bardziej płynne przechodzenie stref.

### D. Zastosowanie w algorytmie redukcji (DWRD):
Wprowadzenie dwutygodniowych bloków tematycznych jednoznacznie definiuje **Priorytet 2 (Kluczowy bodziec - Key Stimulus)** w logice DWRD (Rozdział 7):
*   Jeśli aktywny jest *Mikrocykl VO2 Max*, to kluczową jednostką bodźcującą, której **nie wolno usunąć** przy redukcji tygodnia, jest zaplanowany trening **VO2 Max (Z5)**.
*   Jeśli aktywny jest *Mikrocykl Threshold/SST*, kluczowym bodźcem jest trening **Z4 / Sweet Spot**.
*   Wszelkie inne jazdy jakościowe niezgodne z tematem mikrocyklu spadają do kategorii treningów uzupełniających (Priorytet 3) i są kasowane w pierwszej kolejności w razie braku dni treningowych.

### E. Algorytm Automatycznej Identyfikacji Bodźca (Scoring WS):
W celu automatycznego wyznaczenia, która sesja w danym tygodniu jest kluczowym bodźcem (gdy w kalendarzu nałoży się kilka jednostek o wyższej intensywności), ML Core oblicza dla każdego treningu **Wskaźnik Wagi Bodźca (WS)**:
$$WS = (T_{target\_zone} \times W_{intensity}) + (TSS \times 0.2)$$

Gdzie:
*   $T_{target\_zone}$ – czas planowany/spędzony w strefie docelowej dla danej fazy (w minutach).
*   $W_{intensity}$ – waga intensywności strefy docelowej:
    *   Dla strefy VO2 Max / Anaerobic (Z5+) = `2.0`
    *   Dla strefy Sweet Spot / Threshold (Z3/Z4) = `1.5`
    *   Dla strefy wytrzymałości tlenowej (Z2) = `0.5`

Trening o najwyższym wskaźniku $WS$ w skali tygodnia otrzymuje flagę `is_key_stimulus = True`. Jeśli silnik DWRD musi skrócić tydzień, jednostka z tą flagą zostaje zachowana za wszelką cenę.

---

## 13. Obsługa Degradacji przy Braku Danych (Graceful Degradation)

W przypadku problemów technicznych lub braku urządzeń typu wearable (brak pomiaru HRV, resting HR i snu), silnik Bibi płynnie przełącza się w alternatywne tryby szacowania gotowości:

### A. Uproszczony ReadyScore (Poziom 2 - Brak Wearables):
Jeśli system nie ma dostępu do danych fizjologicznych z nocy, wskaźnik gotowości do treningu jest obliczany na podstawie danych subiektywnych oraz historii RPE:
$$ReadyScore = (RPE_{trend} \times 0.4) + (Samopoczucie_{poranek} \times 0.4) + (Zapas\_Sil \times 0.2)$$

Gdzie:
*   $RPE_{trend}$ (skala 0-100) – odwrócona średnia ważona RPE z ostatnich 3 treningów względem RPE planowanego. Jeśli kolarz jeździł znacznie ciężej niż zakładał plan (np. RPE 9 przy planowanym 6), wskaźnik ten drastycznie spada.
*   $Samopoczucie_{poranek}$ (skala 0-100) – poranna deklaracja użytkownika w bocie (skala 1-5 z pytania nr 1, przemnożona przez 20).
*   $Zapas\_Sil$ (skala 0-100) – subiektywne poczucie "paliwa w baku" deklarowane po ostatnim treningu (skala 1-2 z pytania nr 3, zmapowana na 0-100).

### B. Matryca Fallbacku Technologicznego:

| Stan Danych | Poziom Algorytmu | Akcje i Ograniczenia Systemu |
| :--- | :--- | :--- |
| **Pełne dane** (HRV + Sen + RPE + Moc) | **Poziom 1 (Pełny dynamiczny)** | Pełna automatyzacja adaptacji, predykcja zmęczenia chronicznego, korekty stref na bazie dryfu tętna. |
| **Brak Wearables** (Tylko Moc/HR + RPE + Bot) | **Poziom 2 (Model Uproszczony)** | Blokada dynamicznych korekt na bazie tętna spoczynkowego i HRV. Gotowość oparta na ankiecie porannej, historii RPE i telemetrycznym wskaźniku TEQ. |
| **Blackout danych** (Brak danych z ostatnich 48h) | **Poziom 3 (Tryb Konserwatywny)** | System zamraża progresję obciążeń. Wstrzymana zostaje adaptacja – system utrzymuje obciążenia na poziomie zeszłotygodniowego plateau, traktując sesje jako "utrzymujące". |

---

## 14. Przepływ Interakcji z Botem Telegram

Bot Telegram jest głównym, asynchronicznym kanałem komunikacji z kolarzem, działającym w oparciu o orkiestrację n8n.

### Scenariusz A: Brak tagu feedbackowego (bb: X/Y/Z) po treningu
*   **Wyzwalacz (Trigger):** Minęło 12 godzin od wykrycia nowej aktywności w Intervals.icu, a pole notatek (`notes`) nie zawiera tagu zgodnego z regexem `bb: X/Y/Z`.
*   **Akcja bota:** Bot wysyła do użytkownika ciche powiadomienie push:
    > *"Cześć! Widzę Twój wczorajszy trening. Jak się czułeś? Kliknij poniżej, aby szybko uzupełnić dane."*
*   **Interfejs:** Bot generuje klawiaturę inline z szybkimi odpowiedziami podzielonymi na 3 kroki (RPE / Samopoczucie / Zapas).
*   **Wynik:** Po kliknięciu ostatniego przycisku, bot automatycznie wysyła żądanie `POST` do API Intervals.icu, dopisując string `bb: X/Y/Z` do opisu treningu, co zapewnia automatyczny import telemetryczny przy kolejnym odczycie.

### Scenariusz B: Analiza notatki głosowej (Voice-to-Text)
*   Użytkownik, zamiast klikać lub pisać, wysyła do bota krótką notatkę głosową (np. *"noga kręciła dobrze, ale pod koniec bolało mnie kolano"*).
*   n8n przesyła plik audio (`.ogg`) do API transkrypcji (OpenAI Whisper).
*   Otrzymany tekst jest analizowany przez LLM ze specjalnym promptem systemowym, który zwraca ustrukturyzowany plik JSON:
    ```json
    {
      "perceived_exertion": "good",
      "fatigue_localization": "legs_ok",
      "injury_flag": true,
      "injury_description": "knee pain at the end of workout",
      "recommended_action": "flag_coach_or_check_bikefit"
    }
    ```
*   **Logika biznesowa:** Jeśli `injury_flag == true`, system automatycznie dodaje ostrzeżenie do kalendarza na kolejny dzień. Jeśli flaga powtórzy się w kolejnej sesji, silnik automatycznie obniża poziom trudności najbliższego mikrocyklu (np. zamienia interwały SST na spokojną jazdę Z2).

---

## 15. Detekcja Przetrenowania i Anomalie Długoterminowe

Aby odróżnić planowane, kontrolowane zmęczenie (overreaching) od niebezpiecznego przetrenowania (overtraining), ML Core analizuje wskaźniki w dwóch horyzontach czasowych.

### A. Algorytm Automatycznej Regeneracji Wymuszonej (Wymuszony Deload):
Procedura automatycznego deloadu (redukcja objętości o 40% w bieżącym tygodniu) zostaje wyzwolona, gdy spełniony jest następujący warunek:
```
JEŚLI (Liczba_Treningów_Z_Rzędu(TEQ < 80%) >= 3)
   AND (Deklaracja_Trudności == "Za ciężki" OR RPE >= RPE_Planowane + 2)
   AND (Zapas_Sił <= 2 w skali 1-5 LUB ReadyScore < 30)
WTEDY -> Aktywuj AUTOMATYCZNY DELOAD
```

### B. Długoterminowy Monitoring Stresu (Zasada TSB):
*   **Analiza TSB (Stress Balance):** Jeśli wskaźnik TSB utrzymuje się na poziomie **poniżej -30 punktów przez ponad 14 dni z rzędu**, a wskaźnik gotowości (ReadyScore) wykazuje stały trend spadkowy:
    *   System nakłada twardą blokadę na jednostki powyżej strefy **Z3 (Tempo)**.
    *   Do kalendarza dodawany jest automatyczny komunikat: *"Wykryto kumulację zmęczenia chronicznego. Bieżący mikrocykl zostaje skrócony o 40% objętości w celu ochrony przed przetrenowaniem."*

---

## 16. Zasada Bezpiecznika Konserwatywnego (Conservative Default)

Fundamentalną filozofią Bibi AI Coach jest ochrona zdrowia kolarza amatora. Ponieważ amatorzy mają tendencję do trenowania zbyt ciężko i niedoceniania zmęczenia pozasportowego, w przypadku wszelkich wątpliwości decyzyjnych lub wyników "granicznych" (borderline), **silnik adaptacyjny oraz modele LLM zawsze wybierają wariant bezpieczniejszy (konserwatywny)**.

### A. Wdrożenie Zasady w Decyzjach Algorytmu:
1.  **Długość przerw w interwałach:** W przypadku wahań algorytmu przy parametryzacji sesji (np. czy zastosować 3-minutową czy 4-minutową przerwę wypoczynkową między powtórzeniami VO2max) – **zawsze wybierana jest przerwa dłuższa**, gwarantująca wyższą jakość kolejnego powtórzenia.
2.  **Odstępy między treningami:** Jeśli system analizuje przesunięcia kalendarza (DWRD) i ma do wyboru skumulowanie mocnych jednostek dzień po dniu vs. rozdzielenie ich dodatkowym dniem wolnym/regeneracyjnym (nawet kosztem konieczności redukcji liczby treningów w tygodniu) – **zawsze wybiera opcję z dłuższą przerwą i regeneracją**.
3.  **Liczba i trudność ciężkich jednostek:** W przypadku granicznych wyników gotowości (ReadyScore na granicy strefy zielonej i bursztynowej / bursztynowej i czerwonej) – system **zawsze profilaktycznie obniża stopień trudności** (np. redukuje liczbę powtórzeń interwałów lub zamienia trening na tlen Z2).
4.  **Enforcement na Poziomie 3 (AI Reviewer):** Rola modelu AI Recenzent (Critic) polega w dużej mierze na egzekwowaniu Bezpiecznika Konserwatywnego. Jeśli propozycja Trenera (Actor) jest agresywna, a dane fizjologiczne lub subiektywne wykazują najmniejsze wahania – Recenzent ma zakodowany obowiązek odrzucić zmianę lub zmodyfikować ją na bezpieczniejszą (np. nakazać deload).

---

## 17. Złota Zasada Bibi: Skupione Wykonanie (Hard is Hard, Easy is Easy)

Naczelnym mottem i przewodnią filozofią wszystkich planów treningowych generowanych przez Bibi jest zasada:

> **"W dni z akcentami – wykonuj akcenty w 100%, a w dni i etapy odpoczynku – naprawdę odpoczywaj."**

### Wytyczne dla Silnika i Modeli LLM:
1.  **Dni z akcentami (High Intensity):** Kolarz ma wejść na zaplanowany trening w pełni zregenerowany, aby móc zrealizować założone waty na 100% (np. interwały VO2max lub SST). Jeśli gotowość na to nie pozwala – trening jest przekładany lub łagodzony (zgodnie z Bezpiecznikiem Konserwatywnym), zamiast realizowania go "na pół gwizdka".
2.  **Dni i etapy odpoczynku (Recovery/Rest):** Treningi regeneracyjne (Z1) oraz etapy przerw wypoczynkowych między interwałami muszą być realizowane na bardzo niskiej intensywności. System surowo ocenia wskaźnik TEQ za jazdę zbyt mocną w trakcie tych faz. Prawdziwa regeneracja jest warunkiem koniecznym do wywołania adaptacji superkompensacji z ciężkich sesji.

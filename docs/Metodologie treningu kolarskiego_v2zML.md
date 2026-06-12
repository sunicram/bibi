# Trzy koncepcje treningu adaptacyjnego dla kolarza amatora (3–4 sesje/tydz.)

Dokument do wykorzystania jako baza wiedzy w aplikacji z dwoma modelami LLM (Trener + Recenzent) oraz warstwą Machine Learning.

---

## Koncepcja 1: Trening sterowany subiektywnym obciążeniem (RPE + well-being)

### Podstawa naukowa

- Systematyczne przeglądy monitorowania sportowców pokazują, że proste, subiektywne miary samopoczucia (zmęczenie, sen, DOMS, nastrój) są często bardziej czułe na zmiany obciążenia i ryzyko przetrenowania niż wiele obiektywnych testów spoczynkowych (HR, biochemia itp.) [web:46][web:47].
- Session‑RPE (RPE × czas trwania) dobrze odzwierciedla obciążenie wewnętrzne w różnych dyscyplinach i koreluje z sumą bodźców treningowych [web:46].

### Dane wejściowe (dla aplikacji)

**Po każdej sesji:**
- `session_rpe` – odczuwany wysiłek (np. skala 0–10).

**Raz dziennie (rano lub przed treningiem):**
- `sleep_quality` (0–10).
- `fatigue` – ogólne zmęczenie (0–10).
- `muscle_soreness` (0–10).
- `stress_mood` (0–10).
- `motivation_readiness` (0–10).

Z tych pięciu ostatnich pól można liczyć `wellbeing_sum` (0–50).

### Logika adaptacyjna (reguły bazowe)

1. **Klasyfikacja dnia na podstawie `wellbeing_sum`:**
   - `>= 35` → dzień **zielony** (pełna realizacja planu).
   - `25–34` → dzień **bursztynowy** (realizacja planu z redukcją intensywności/objętości).
   - `< 25` → dzień **czerwony** (trening regeneracyjny lub dzień wolny).

2. **Dostosowanie sesji:**
   - Zielony: wykonaj zaplanowany trening (np. interwały w pełnej liczbie serii/powtórzeń).
   - Bursztynowy: obniż intensywność lub objętość o 10–20% (mniej serii, krótsze interwały, zamiana części pracy jakościowej na tlenową).
   - Czerwony: lekka jazda 20–40 min w Z1–Z2 albo pełny rest.

3. **Użycie `session_rpe × duration` jako obciążenia wewnętrznego:**
   - Suma kilku dni o wysokim obciążeniu + niskie `wellbeing_sum` → wymuszony dzień bursztynowy/czerwony.
   - Długie okresy niskiego obciążenia przy wysokim `wellbeing_sum` → stopniowe zwiększanie trudności przez Trenera.

### Rola LLM

**Model Trener:**
- Wczytuje dane wellness + `session_rpe`.
- Klasyfikuje dzień (zielony/bursztynowy/czerwony).
- Generuje konkretną sesję (czas, typ, intensywność) zgodnie z klasą dnia i długoterminowym celem.

**Model Recenzent:**
- Sprawdza, czy Trener nie ignoruje sygnałów zmęczenia (zbyt wiele ciężkich dni przy niskim `wellbeing_sum`).
- Proponuje korekty (np. zamiana interwałów na jazdę tlenową).

### Rola Machine Learning

- Uczy się, jakie kombinacje wellness + `session_rpe` + typów sesji prowadzą do najlepszych wyników (np. wzrost FTP, poprawa czasu na stałej trasie, subiektywna satysfakcja).
- Personalizuje progi (np. zamiast globalnego 35 jako próg dnia „zielonego”, dostosowuje próg do konkretnego użytkownika).

---

## Koncepcja 2: Trening wielosygnałowy (moc + tętno + RPE + warunki)

### Podstawa naukowa

- System FuCycling pokazuje, jak zbudować hierarchiczny system oceny sesji z użyciem stref treningowych, tętna, mocy i RPE, aby uzyskać końcowy wskaźnik „jakości sesji” dla kolarza [web:21].
- Badanie HIIT z przerwami stałymi vs samodzielnie dobieranymi wskazuje, że przy kontrolowanej sumarycznej długości odpoczynku, wyniki mocy i odpowiedzi fizjologicznej są zbliżone, ale samodzielne przerwy poprawiają poczucie autonomii [web:5].
- Przedłużony wysiłek obniża moc na przejściu z intensywności umiarkowanej do ciężkiej (tzw. durability), co podkreśla rolę zmęczenia kumulacyjnego w interpretacji danych z treningu [web:18].

### Dane wejściowe

Z każdej sesji:
- `avg_power`, `max_power`, rozkład czasu w strefach mocy (np. Z1–Z5).
- `avg_hr`, `max_hr`, rozkład czasu w strefach tętna.
- `session_rpe`.
- Warunki środowiskowe: `temperature`, `humidity`, opcjonalnie `wind_speed` (z API lub sensora).

Z historii:
- `training_load_history` (np. 7–28 dni zsumowanego obciążenia, bazującego na mocy/HR i RPE).

### Logika adaptacyjna – idea „session quality”

1. **Faza 1 – ocena fizjologiczna (performance-score):**
   - Wejścia: docelowa strefa mocy vs osiągnięta, relacja mocy do tętna (np. czy HR nie jest „nadmiernie wysokie” przy danej mocy), czas w strefach.
   - Wyjście: `performance_score` (0–100) – na ile sesja zrealizowała założony bodziec.

2. **Faza 2 – integracja z RPE i warunkami:**
   - Wejścia: `performance_score`, `session_rpe`, `temperature`, `humidity`.
   - Wyjście: `session_quality` (0–100) oraz `physiological_cost` (0–100).
   - Przykład: wysoka temperatura/wilgotność → przy tym samym `performance_score` rośnie `physiological_cost`.

3. **Reguły dla Trenera:**
   - `session_quality` wysokie, `physiological_cost` umiarkowane → w kolejnym mikrocyklu można lekko zwiększyć intensywność (np. +3–5% mocy w interwałach) lub objętość.
   - `session_quality` niskie + wysoki `physiological_cost` przy normalnych warunkach → sygnał przeciążenia; następna sesja lżejsza (np. tlen zamiast interwałów).
   - `session_quality` niskie, `physiological_cost` średnie/wysokie, ale warunki ekstremalne (upał, wysoka wilgotność) → uwzględnić warunki przy interpretacji, nie „karać” zawodnika zbyt mocnym obniżeniem obciążeń.

### Rola LLM

**Model Trener:**
- Ocenia wyniki sesji (performance_score, session_quality, physiological_cost).
- Na tej podstawie decyduje, czy w kolejnym treningu:
  - zwiększyć/utrzymać/zmniejszyć intensywność,
  - zmienić typ sesji (np. HIIT → tempo → tlen),
  - zmodyfikować długość przerw (zwłaszcza przy interwałach).

**Model Recenzent:**
- Sprawdza trendy `physiological_cost` na przestrzeni dni/tygodni.
- Pilnuje, by nie kumulować zbyt wielu dni z wysokim kosztem bez bloków regeneracyjnych.

### Rola Machine Learning

- Zastępuje ręcznie wymyślone membership functions / progi (jak w FuCycling) dopasowanymi do konkretnego użytkownika.
- Uczy się wag: jak ważne są moc, tętno, RPE i warunki w przewidywaniu realnego progresu (np. poprawa czasu na stałej trasie).
- Może przewidywać oczekiwaną `session_quality` dla zaplanowanej sesji i ostrzegać, gdy plan jest zbyt agresywny przy aktualnym stanie zawodnika.

---

## Koncepcja 3: Trening sterowany regeneracją (HRV + stres/odzysk + historia obciążeń)

### Podstawa naukowa

- Protokół HRV‑guided training dla sportowców wytrzymałościowych zakłada codzienny poranny pomiar HRV i dopasowanie obciążeń; oczekuje się, że HRV‑guided może dać lepszą indywidualizację niż klasyczny plan [web:57].
- W rehabilitacji i kardiologii HRV jest używane do kontroli indywidualnej odpowiedzi na HIIT i inne formy treningu, ze względu na silny związek HRV z równowagą współczulno–przywspółczulną [web:58][web:59].
- Badania nad różnymi konfiguracjami interwałów pokazują, że proporcja praca:odpoczynek wpływa na subiektywny stres i markery uszkodzenia mięśni, co wiąże się z potrzebą różnicowania dni „quality” i dni regeneracyjnych [web:61].

### Dane wejściowe

**Codziennie rano:**
- `hrv_morning` – np. rMSSD lub ln rMSSD, mierzone po przebudzeniu (1–5 min).
- `resting_hr` – spoczynkowe tętno.

**Z historii:**
- `training_load_history` – ostatnie 7–28 dni sumarycznego obciążenia.
- `wellbeing_sum` – z Koncepcji 1.

### Logika adaptacyjna HRV + wellness

1. **Wyznaczenie stref HRV na podstawie historii:**
   - `hrv_baseline` = średnia z ostatnich 7–14 dni.
   - `hrv_today_delta` = (dzisiejsza HRV – baseline) / SD.
   - Klasy:
     - `hrv_normal` (delta w przedziale np. −0,5 do +0,5 SD).
     - `hrv_low` (delta < −0,5 SD).
     - `hrv_high` (delta > +0,5 SD).

2. **Połączenie z wellness:**
   - `hrv_normal` + wysokie `wellbeing_sum` → dzień **zielony**.
   - `hrv_low` + niskie `wellbeing_sum` → dzień **czerwony** (regeneracja, brak ciężkich interwałów).
   - `hrv_low` + dobre `wellbeing_sum` → dzień **bursztynowy** (ostrożne trenowanie, skrócone lub łagodniejsze interwały).
   - `hrv_high` + wysokie `wellbeing_sum` → potencjalnie dobry dzień na sesję kluczową, ale interpretacja indywidualna (tu mocno wchodzi ML).

3. **Wpływ na plan tygodniowy:**
   - Zielony: można realizować kluczowe sesje (np. dłuższe interwały w Z3–Z4, próby czasowe).
   - Bursztynowy: sesje jakościowe skrócone lub zamiana części pracy na tlen; nacisk na technikę, kadencję.
   - Czerwony: jazda lekka lub pełny odpoczynek + komunikat edukacyjny od Trenera (sen, żywienie, stres).

### Rola LLM

**Model Trener:**
- Łączy `hrv_morning`, `resting_hr`, `wellbeing_sum` i `training_load_history` w jedną zmienną „gotowość do intensywności”.
- Na tej podstawie decyduje, czy danego dnia w ogóle pojawia się trening jakościowy, czy tylko tlenowy / regeneracja.

**Model Recenzent:**
- Pilnuje, by seria dni z obniżoną HRV nie była ignorowana.
- Może generować ostrzeżenia długoterminowe („spadek HRV utrzymuje się > 7 dni – sprawdź sen, stres, żywienie, ewentualnie skonsultuj się z lekarzem”).

### Rola Machine Learning

- Uczy się, jak u konkretnego użytkownika zmiany HRV korelują z realną wydolnością i samopoczuciem.
- Personalizuje progi dla `hrv_low`, `hrv_normal`, `hrv_high`.
- Pomaga odróżnić „szum” (np. jednorazowy spadek HRV) od trendu wymagającego reakcji.

---

## Integracja trzech koncepcji w aplikacji

1. **Warstwa podstawowa (wszyscy użytkownicy):**
   - Koncepcja 1 – RPE + well‑being jako minimalny standard adaptacji.

2. **Warstwa rozszerzona (użytkownicy z miernikiem mocy/tętna):**
   - Koncepcja 2 – analiza sesji na podstawie mocy, tętna, RPE i warunków, generowanie `session_quality` i `physiological_cost`.

3. **Warstwa regeneracyjna:**
   - Koncepcja 3 – HRV + wellness + obciążenie z ostatnich dni decydują, czy w danym dniu w ogóle wolno „wejść” w ciężkie jednostki.

Dla LLM oznacza to trzy poziomy decyzji:
- **Poziom 1:** Czy dzisiaj trenować lekko/średnio/ciężko? (Koncepcja 1 + 3).
- **Poziom 2:** Jaki dokładnie typ sesji (tlen, tempo, interwały, technika) i z jaką intensywnością? (Koncepcja 2 + 1).
- **Poziom 3:** Czy plan wygenerowany przez Trenera jest bezpieczny i spójny z długoterminowym trendem regeneracji i zmęczenia? (Recenzent + ML na bazie wszystkich trzech koncepcji).

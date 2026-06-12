# Final version with all fixes
output_content_final = """# 3 Metodologie Treningu Adaptacyjnego dla Kolarza Amatora (3-4 razy w tygodniu)

## Wprowadzenie
Te metody zostaly przygotowane do uzycia w aplikacji do planowania i monitorowania treningu kolarskiego, gdzie:
- **2 modele LLM** (trener oraz recenzent) dzialaja jako wirtualni trenerzy, dopasowujac trening na biezaco
- **Machine Learning** doskonali reakcje modeli na podstawie danych historycznych
- Trening jest dostosowany do potrzeb, potencjalu, wieku, plyci, stylu zycia i odzywiania kolarza

---

## Tabela: 5 Metodologii Treningu Adaptacyjnego

| Metodologia | Co mierzy | Kiedy stosowac | Plusy | Minusy |
|---|---|---|---|---|
| Session-RPE + well-being | RPE po sesji + codzienna ankieta (sen, zmeczenie, motywacja, bol) | Codziennie, dla kazdego amatora, zwlaszcza przy nieregularnym stylu zycia | Bardzo proste, tanie, czule na przetrenowanie, latwo wdrozyc | Subiektywne, brak precyzji bez mocy/tetna |
| Power-based z korektą tetna i RPE | Moc, tetno, RPE, czas w strefach | Gdy masz miernik mocy i tetna, chcesz precyzyjnego sterowania intensywnoscia | Precyzyjne, jasne cele, dobre do HIIT i interwalow | Wymaga sprzetu, bywa sztywne bez feedbacku |
| Self-selected recovery (autoregulacja przerw) | Subiektywne zmeczenie, gotowosc, samodzielny wybor przerw w interwalach | HIIT, interwaly, gdy chcesz zachowac qualitę przy zmiennym zmeczeniu | Wzmacnia autonomie, lepsza akceptacja treningu | Trudniej porownac sesje, wymaga samodyscypliny |
| HRV-guided trening | HRV w spoczynku (rano), tetno, moc, RPE | Gdy masz stabilny pomiar HRV i chcesz lepszej prognozy regeneracji | Obiektywny wskaznik regeneracji, moze zmniejszyc ryzyko przetrenowania | Wymaga codziennych pomiarow, interpretacja trudna, nie zawsze transferuje sie na wynik |
| Fuzzy / algorytmy adaptacyjne | Moc, tetno, RPE, well-being, temperatura, wilgotnosc, jakosc snu | Gdy chcesz laczy kilka sygnalow i automatycznie decydowac o kolejnym treningu | Laczy dane obiektywne i subiektywne, redukuje decyzje | Zlozone, wymaga narzedzia/aplikacji |

---

## 3 Metodologie Treningu Adaptacyjnego dla Kolarza Amatora (3-4 razy w tygodniu)

### 1. Session-RPE + Mini-ankieta Samopoczucia (Najprostsza i Najbardziej Uniwersalna)

**Co robisz:**

**Po kazdej sesji:**
- Oceniasz RPE (1-10) lub FLOW/effort (1-10)

**Przed treningiem (lub w nocy), odpowiadasz na 3-5 pytan:**
1. Jak spedzles? (1-10)
2. Jakie jest ogolne zmeczenie? (1-10)
3. Czy czujesz bol/miesnie? (1-10)
4. Czy masz motywacje? (1-10)
5. Czy czujesz sie gotowy na trening? (1-10)

**Jak dostosowac:**

| Suma samopoczucia | Dostosowanie treningu |
|---|---|
| < 25 (przy skali 1-10, 5 pytan) | Trening lzejszy: 30-40% nizszej intensywnosci, krotszy czas, brak interwalow |
| >= 35 | Wykonaj planowany trening w pelnej intensywnosci |
| < 20 | Odpusc trening lub zamien na jazde rekreacyjna (20-30 min, bardzo lekko) |

**Dlaczego dla Kolarza Amatora:**
- Nie wymaga sprzetu poza zegarkiem/telefonem
- Idealne dla amatora, ktory ma ograniczony czas i nieregularny styl zycia
- Badan

cia pokazuja, ze subiektywne ankiety sa czesto bardziej czule na zmeczenie niz wiele testow laboratoryjnych [web:46][web:47]

**Implementacja w aplikacji LLM:**
- Model Trener: Pyta o RPE po sesji, analizuje ankiete samopoczucia, generuje dostosowany plan
- Model Recenzent: Sprawdzaj, czy plan jest bezpieczny, czy nie ma przetrenowania, sugeruj alternatywy
- Machine Learning: Ucz sie na danych historycznych (RPE, samopoczucie, wynik), optymalizuj dostosowania

---

### 2. Power-based Trening z Korektą Tetna i RPE (Metoda Precyzyjna)

**Co robisz:**

**Planowanie:**
- Planujesz trening na podstawie stref mocy (np. 20-minutowy test, strefy 1-5)
- Mierzysz moc i tetno w czasie rzeczywistym
- Po sesji oceniasz RPE (1-10)

**Jak dostosowac:**

| Sygnal | Dostosowanie treningu |
|---|---|
| Tetno przy danej mocy wyzsze niz zwykle (+5-10 bpm) | Zmniejsz intensywnosc 10-20%, krotszy czas |
| RPE > 7 przy planowanej intensywnosci | Trening lzejszy, wiecej odpoczynku, mniej interwalow |
| Tetno i RPE w normie | Wykonaj plan w pelnej intensywnosci |

**Przyklad Tygodnia (3-4 Jazdy):**

| Jazda | Czas | Trening |
|---|---|---|
| Jazda 1 | 20 min | 2 x 8 min w strefie 3, 2 min odpoczynku |
| Jazda 2 | 25 min | 3 x 5 min w strefie 4, 2 min odpoczynku |
| Jazda 3 | 30 min | interwaly self-selected: 6 x 3 min w strefie 4, przerwa dobierana samodzielnie |
| Jazda 4 | 40 min | jazda lekka w strefie 1-2, bez interwalow |

**Dlaczego dla Kolarza Amatora:**
- Jeśli masz miernik mocy i tetna, to daje precyzje
- Badanie HIIT na kolarzach pokazyalo, ze samo-dobor przerw nie daje straty jakości, ale zwieksza autonomie [web:5]
- System laczacy moc, tetno i RPE jest obecnie jednym z najbardziej uzasadnionych naukowo [web:21]

**Implementacja w aplikacji LLM:**
- Model Trener: Analizuje moc i tetno w czasie rzeczywistym, sugeruje dostosowania podczas sesji
- Model Recenzent: Sprawdzaj, czy intensywnosc jest bezpieczna, czy nie ma ryzyka przetrenowania
- Machine Learning: Ucz sie na danych historycznych (moc, tetno, RPE, wynik), optymalizuj dostosowania stref mocy

---

### 3. Self-selected Recovery + Session-RPE (Metoda Autonomiczna)

**Co robisz:**

**W interwalach:**
- Dobierasz przerwy samodzielnie na podstawie odczuc zmeczenia

**Po kazdej sesji:**
- Oceniasz RPE (1-10)

**Przed treningiem:**
- Robisz mini-ankieta samopoczucia (taki jak w metodzie 1)

**Jak dostosowac:**

| Sygnal | Dostosowanie treningu |
|---|---|
| Suma samopoczucia < 25 | Interwaly krotsze, przerwy dluzsze, mniej powtóĺĺĺ |
| Suma >= 35 | Interwaly w pelnej intensywnosci, przerwy dobierasz swobodnie |
| RPE po interwalach > 8 | W następnej sesji zmniejsz intensywnosc 10-15% |

**Przyklad Tygodnia (3-4 Jazdy):**

| Jazda | Czas | Trening |
|---|---|---|
| Jazda 1 | 20 min | 4 x 5 min w strefie 3, przerwa dobierana samodzielnie |
| Jazda 2 | 25 min | 5 x 4 min w strefie 4, przerwa dobierana samodzielnie |
| Jazda 3 | 30 min | 6 x 3 min w strefie 4, przerwa dobierana samodzielnie |
| Jazda 4 | 40 min | jazda lekka, bez interwalow |

**Dlaczego dla Kolarza Amatora:**
- Nie wymaga precyzyjnych pomiarow tetna/mocy, ale daje autonomie
- Badanie HIIT na kolarzach pokazyalo, ze samo-dobor przerw daje podobne wyniki do stalych, ale lepsą akceptację treningu [web:5]
- Idealne dla amatora, ktory chce uniknac przetrenowania i zachowac motywacje

**Implementacja w aplikacji LLM:**
- Model Trener: Pyta o samopoczucie, analizuje RPE, sugeruje dobieranie przerw podczas sesji
- Model Recenzent: Sprawdzaj, czy dobieranie przerw jest bezpieczne, czy nie ma ryzyka przetrenowania
- Machine Learning: Ucz sie na danych historycznych (RPE, samopoczucie, przerwy, wynik), optymalizuj dlugosc i czestotliwosc przerw

---

## Podsumowanie: Co Wybrac?

| Twuj Profil | Najlepsza Metoda |
|---|---|
| Nie masz sprzetu, nieregularny styl zycia | Session-RPE + mini-ankieta (metoda 1) |
| Masz miernik mocy i tetna, chcesz precyzji | Power-based z korektą tetna i RPE (metoda 2) |
| Chcesz autonomii, nie chcesz sztywnego planu | Self-selected recovery + Session-RPE (metoda 3) |

---

## Architektura Aplikacji LLM + Machine Learning

### Rola Modeli LLM

**Model Trener:**
- Generuje plan treningowy na podstawie danych kolarza (wiek, plyc, styl zycia, odzywianie, dostępne dni)
- Analizuje feedback po sesji (RPE, samopoczucie, moc, tetno, HRV)
- Dostosowuje intensywnosc, czas, typ treningu na biezaco
- Podtrzymuje motywacje, sugeruje alternatywy

**Model Recenzent:**
- Sprawdzaj, czy plan jest bezpieczny
- Analizuj ryzyko przetrenowania, kontuzji
- Sugeruje alternatywy,jeśli model Trener jest zbyt agresywny
- Dba o rownosc między treningiem i regeneracja

### Rola Machine Learning

- Uczenie na danych historycznych: RPE, samopoczucie, moc, tetno, HRV, wynik treningowy
- Optymalizacja dostosowan: ML uczy sie, jakie dostosowania prowadzą do najlepszych rezultatow
- Personalizacja: ML dostosowuje sie do indywidualnego profilu kolarza (wiek, plyc, styl zycia)
- Predykcja: ML przewiduje, jak kolarz zareaguje na dany trening

### Integracja z Metodologiami

| Metodologia | Integracja z LLM + ML |
|---|---|
| Session-RPE + well-being | LLM pyta o RPE i samopoczucie, ML optymalizuje dostosowania na podstawie danych historycznych |
| Power-based z korektą | LLM analizuje moc i tetno w czasie rzeczywistym, ML optymalizuje strefy mocy |
| Self-selected recovery | LLM sugeruje dobieranie przerw, ML optymalizuje dlugosc i czestotliwosc przerw |

---

## Wnioski

Najbardziej naukowo uzasadnione dziś podejscie to adaptacyjne monitorowanie obciazenia i regeneracji, w którym plan kolejnych jednostek koryguje sie na podstawie mocy, tetna, RPE, samopoczucia, snu i gotowosci do wysilku, zamiast trzymac sie sztywnego planu [web:21][web:46][web:47]. W praktyce najlepiej dzialaja nie pojedyncze wskazniki, tylko ich polaczenie: obiektywne dane o treningu plus subiektywny feedback sportowca [web:21].\n"""

# Fix remaining issues
output_content_final = output_content_final.replace("zachowac qualitę", "zachowac jakość").replace("powtóĺĺĺ", "powtórzeń").replace("Badan\n\ncia", "Badania")

with open("/home/user/output/metodologie_trening_adaptacyjny_kolarski.md", "w", encoding="utf-8") as f:
    f.write(output_content_final)

print(f"Final file created successfully, size: {len(output_content_final)} bytes")
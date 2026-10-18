# Gwent Beta Classic 0.8.1 — Polski

> Wersja 0.8.1 dla Next-Gen 5.0+ została przetestowana w grze. Classic 1.32 jest poprawiana i sprawdzana osobno; obecne archiwum jest wersją testową.

## Ważne

Przed instalacją i przed każdą aktualizacją zrób kopię zapasową zapisów. Mod jest w aktywnym rozwoju, więc do pierwszych partii użyj osobnego zapisu.

Tłumaczenia nadal są wersją testową: teksty kart pochodzą z oficjalnej lokalizacji bety, a interfejs przetłumaczono za pomocą AI i może zawierać błędy. Nowe podpowiedzi dodane od wersji 0.6.6 są na razie tylko po angielsku i rosyjsku; w pozostałych językach wyświetlają się po angielsku. Zgłaszaj wszystko, co brzmi źle.

## O modzie

Gwent Beta Classic zastępuje gwinta z Wiedźmina 3 kartami, zasadami i planszą samodzielnej wersji Gwent Beta 0.9.24. Partie pozostają częścią świata Wiedźmina: graj z NPC, wykonuj zadania, kupuj beczki i buduj własne talie.

## Funkcje

- 479 kart kolekcjonerskich, w tym 21 dowódców, wszystkie pięć frakcji
- Plansza, interfejs, czcionki, ramki kart, pogoda i efekty z bety; animowani dowódcy
- Edytor talii: pięć edytowalnych talii startowych i osiem własnych miejsc, filtry i wyszukiwanie
- Przeciwnicy z 46 archetypami talii z bety i trzy poziomy trudności SI
- Beczki za 200 koron u wszystkich karczmarzy, otwierane jak w becie
- Skrawki: twórz karty za 30 / 80 / 200 / 800 zależnie od rzadkości; nadmiarowe kopie są mielone automatycznie
- Samouczek, mulligan, podgląd cmentarzy i talii, szczegółowy podgląd kart
- Mysz, klawiatura i kontroler

## Zmiany od 0.7.3a

- Każdy pakiet zawiera pięć wersji głosowych i wszystkie 13 języków tekstu. Osobne pobieranie według języka głosów nie jest już potrzebne.
- Dwa sąsiednie przyciski Tekst i Głosy w menu moda, z niezależnym wyborem automatycznym lub ręcznym.
- Osobne wykrywanie języka tekstu i mowy gry. Nieobsługiwane języki są zastępowane angielskim.
- Preferencje są przechowywane w zapisie gry. Poprzedni ręczny wybór języka tekstu pozostaje po aktualizacji.
- Poprawiono definicje beczek i odzyskiwanie zapasów w Nowej Grze +. Nieudane dodanie nie jest oznaczane jako wykonane; sprzedane beczki nie wracają przy każdym otwarciu sklepu.
- Dopracowano trzy pociski Jotunna, Kambi/Hemdalla, Ragh Nar Roog, Golden Froth, statusy, liczniki i efekty pancerza.
- Zasoby interfejsu przepakowano do budżetu kompilacji 63 MiB bez obniżania rozdzielczości tekstur. Uruchamianie menu i stabilność nadal podlegają testom.

## Języki

Tekst: angielski, rosyjski, niemiecki, francuski, włoski, polski, hiszpański (Hiszpania), hiszpański (Ameryka Łacińska), portugalski (Brazylia), japoński, koreański, chiński uproszczony i chiński tradycyjny. Język zmienisz w każdej chwili przyciskiem języka tekstu w lewym górnym rogu menu talii i kolekcji lub w ustawieniach bitwy; wybór jest zapisywany.

Każdy pakiet zawiera głosy RU, EN, DE, IT i PT-BR. Tekst i głosy wybierasz niezależnie dwoma sąsiednimi przyciskami w menu talii/kolekcji moda lub w ustawieniach partii. Zmiana nie wymaga ponownej instalacji. Automatycznie śledzi osobno bieżący język tekstu i mowy gry; brakujący język zastępuje angielskim. Po wyborze zapisz grę normalnie: ustawienia należą do tego zapisu i pozostają po aktualizacji plików moda. Poprzedni ręczny wybór tekstu jest zachowany. Niektóre kwestie trolla od beczek w DE/IT zachowują rosyjskie nagranie zastępcze. Natywne nazwy przedmiotów zależą od języka gry; część komunikatów poza interfejsem pozostaje RU/EN.

## Instalacja

1. Zamknij grę i wykonaj kopię zapisów. Pobierz pakiet dla 1.32 lub Next-Gen (5.0+). Instaluj tylko jedną wersję Beta Gwent.

2. Przy aktualizacji najpierw przenieś poprzedni folder moda Beta Gwent poza Mods. Nie usuwaj całego Mods ani nie mieszaj plików wersji.

3. Skopiuj Mods z archiwum do katalogu gry, obok bin i content. Ścieżka docelowa: Mods/modBetaGwentClassic132/content dla 1.32 lub Mods/modBetaGwent0924/content dla Next-Gen.

4. Wczytaj zapis. Zwykłe menu talii Gwinta otwiera edytor i wybór języków; rozmowa z grającym NPC rozpoczyna partię. Zapisz grę, aby zachować wybór.

## Wymagania

The Witcher 3 na PC. Wybierz osobną kompilację Classic 1.32 albo Next-Gen (pakiet oznaczony 5.0+). Do gry nie są potrzebne REDkit, Wwise ani instalator EXE.

## Kompatybilność

Usuń stary folder modBetaGwentReduxCompat: osobna warstwa zgodności nie jest już dołączana. Zgodność z Redux/Redo Expansion nie została osobno potwierdzona. Inne przeróbki gwinta oraz mody zmieniające jego menu, handel kartami lub nagrody mogą powodować konflikty. Po zmianie zestawu modów ponownie scal skrypty w Script Merger.

## Zgłaszanie błędów

Problem? Podaj wersję moda i dokładną wersję gry, wybrany tekst i głosy (także Automatycznie), informację o Nowej Grze +, inne mody, karty/dowódców i kroki odtworzenia. Pomogą zrzut ekranu i zapis sprzed problemu. Przy błędach tłumaczenia podaj język, ekran i propozycję poprawki.

### Włączanie dziennika

1. Dodaj -debugscripts po końcowym cudzysłowie w polu celu skrótu do witcher3.exe. Steam: Właściwości → Ogólne → Opcje uruchamiania. W GOG możesz użyć bezpośredniego skrótu do witcher3.exe.

2. Uruchom grę, odtwórz błąd i zamknij ją. Od razu skopiuj scriptslog.txt: następny start nadpisze plik. Jeśli zawiera tylko nagłówek, zgłoś to; może być potrzebna dodatkowa konfiguracja.

3. Jeżeli Windows utworzył zrzut awarii, dołącz też najnowszy pasujący plik .dmp.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Podziękowania

Dziękujemy CD Projekt za Wiedźmina i Gwinta, LegacyGwent DIY za materiały kart i planszy, społeczności Beta Gwent za zachowanie archiwalnych materiałów i pomysły na archetypy oraz wszystkim, którzy testują moda i przysyłają szczegółowe zgłoszenia.

Nieoficjalny projekt fanowski. Oryginalny kod moda jest udostępniony na licencji GPL-3.0-only; oryginalne materiały z gry należą do ich właścicieli.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)

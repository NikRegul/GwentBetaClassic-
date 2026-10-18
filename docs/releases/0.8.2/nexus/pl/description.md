# Gwent Beta Classic 0.8.2 — Polski

> Wersja 0.8.2 — osobne paczki dla Classic 1.32 i Next-Gen 5.0+.

## Ważne

Przed instalacją i przed każdą aktualizacją zrób kopię zapasową zapisów. Mod jest w aktywnym rozwoju, więc do pierwszych partii użyj osobnego zapisu.

Teksty kart pochodzą z oficjalnej lokalizacji bety. Interfejs przetłumaczono z pomocą AI i może zawierać błędy językowe. Komunikaty wymiany talii są dostępne we wszystkich 13 językach; część starszych wskazówek nadal korzysta z angielskiego. Propozycje poprawek są mile widziane.

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

## Nowości w 0.8.2

- Import i eksport talii przez schowek jako kody BG1, z listą brakujących kart i osobnym poleceniem ich wytworzenia.
- Polecenia konsoli dla zasobów kolekcji, wyszukiwania kart, kolekcji frakcji i zapasu beczek u karczmarzy.
- Karty trafiające na cmentarz lecą do właściwego cmentarza; karty specjalne robią to po rozpatrzeniu efektu. Efekty wygnania i rozpuszczania pozostają.
- Wbudowane definicje dawnych przedmiotów Redux pomagają zapobiegać utracie ekwipunku i ciała przy wczytywaniu zapisu po zmianie moda. Nie odzyskują danych już utraconych i zapisanych.
- Poprawione odstępy menu, stan talii i przyciski; kontroler pozwala przejść z widocznej półki kart do zapisu i z powrotem.
- Portrety dowódców poruszają się dalej po wejściu na ekranie VS. Wejście królowej krabopająków zaczyna się wraz z jej głosem. Classic 1.32 zawiera poprawki mrozu i efektów ataków.

## Udostępnianie talii

Eksport w edytorze kopiuje kod BG1, który można udostępnić jako tekst. Import jest dostępny na liście talii i w edytorze. Wklej cały kod; błędny kod niczego nie zmienia. Jeśli bezpośredni dostęp do schowka nie działa, użyj Ctrl+C/Ctrl+V w polu tekstowym. BG1 jest formatem tego moda i nie zależy od języka interfejsu.

Brakujące karty, w tym dowódca, są wyświetlane z łącznym kosztem we fragmentach. Wytworzenie wymaga osobnego potwierdzenia i odpowiedniej liczby fragmentów. Import tworzy szkic: następnie zapisz talię. Import z listy wykorzystuje wolne własne miejsce, nie nadpisując zajętych. Trening korzysta z istniejącej nieograniczonej kolekcji.

## Polecenia konsoli

bg_help() pokazuje pomoc, a bg_status() kolekcję, beczki i fragmenty. bg_find('Imlerith') wyszukuje nazwy i ID; bg_card(132102,1) daje kartę, bg_faction('monsters') frakcję. bg_leaders() / bg_allcards() uzupełniają dowódców lub całą kolekcję do zwykłych limitów kopii. bg_kegs(10) i bg_scraps(1000) dodają zasoby. Wymaga to wczytanego zapisu, poza menu i partią; potem normalnie zapisz grę. W otwartym sklepie karczmarza bg_shopcheck() sprawdza beczki, a bg_shoprefill(5) uzupełnia zapas do pięciu, zamiast dodawać pięć za każdym razem. Konsola gry musi być wcześniej włączona.

```text
bg_help()
bg_status()
bg_find('Imlerith')
bg_card(132102,1)
bg_faction('monsters')
bg_leaders()
bg_allcards()
bg_kegs(10)
bg_scraps(1000)
bg_shopcheck()
bg_shoprefill(5)
```

## Języki

Tekst: angielski, rosyjski, niemiecki, francuski, włoski, polski, hiszpański (Hiszpania), hiszpański (Ameryka Łacińska), portugalski (Brazylia), japoński, koreański, chiński uproszczony i chiński tradycyjny. Język zmienisz w każdej chwili przyciskiem języka tekstu w lewym górnym rogu menu talii i kolekcji lub w ustawieniach bitwy; wybór jest zapisywany.

Każdy pakiet zawiera głosy RU, EN, DE, IT i PT-BR. Tekst i głosy wybierasz niezależnie dwoma sąsiednimi przyciskami w menu talii/kolekcji moda lub w ustawieniach partii. Zmiana nie wymaga ponownej instalacji. Automatycznie śledzi osobno bieżący język tekstu i mowy gry; brakujący język zastępuje angielskim. Po wyborze zapisz grę normalnie: ustawienia należą do tego zapisu i pozostają po aktualizacji plików moda. Poprzedni ręczny wybór tekstu jest zachowany. Niektóre kwestie trolla od beczek w DE/IT zachowują rosyjskie nagranie zastępcze. Natywne nazwy przedmiotów zależą od języka gry; część komunikatów poza interfejsem pozostaje RU/EN.

## Instalacja

1. Zamknij grę i wykonaj kopię zapisów. Pobierz pakiet dla 1.32 lub Next-Gen (5.0+). Instaluj tylko jedną wersję Beta Gwent.

2. Przy aktualizacji najpierw przenieś poprzedni folder moda Beta Gwent poza Mods. Nie usuwaj całego Mods ani nie mieszaj plików wersji.

3. Skopiuj Mods z archiwum do katalogu gry obok bin i content. Dla Classic 1.32 skopiuj też dołączony katalog DLC. Ścieżki: Mods/modBetaGwentClassic132/content i DLC/dlcBetaGwentClassic132Assets dla 1.32; Mods/modBetaGwent0924/content dla Next-Gen. Zastąp tylko poprzednie katalogi tego moda, zachowując inne mody i DLC.

4. Wczytaj zapis. Zwykłe menu talii Gwinta otwiera edytor i wybór języków; rozmowa z grającym NPC rozpoczyna partię. Zapisz grę, aby zachować wybór.

## Wymagania

The Witcher 3 na PC. Wybierz osobną kompilację Classic 1.32 albo Next-Gen (pakiet oznaczony 5.0+). Do gry nie są potrzebne REDkit, Wwise ani instalator EXE.

## Kompatybilność

Definicje dawnych przedmiotów Redux są wbudowane na potrzeby wczytywania zapisów; usuń przestarzały katalog modBetaGwentReduxCompat. Przy przejściu z Redux użyj kopii zapisu sprzed utraty ekwipunku lub ciała: utracone dane nie zostaną odzyskane. Karty Redux nie są zamieniane na kolekcję Beta; nie gwarantujemy zgodności ze wszystkimi funkcjami Redux/Redo Expansion. Inne przebudowy Gwinta oraz zmiany jego menu, handlu lub nagród mogą powodować konflikty. Po zmianie modów ponownie scal kolidujące skrypty w Script Merger.

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

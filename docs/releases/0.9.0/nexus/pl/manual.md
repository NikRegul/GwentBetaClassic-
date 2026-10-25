# Gwent Beta Classic 0.9.0 — Polski

> Wersja 0.9.0 — osobne paczki dla Classic 1.32 i Next-Gen 5.0+.

## Ważne

Przed instalacją i przed każdą aktualizacją zrób kopię zapasową zapisów. Mod jest w aktywnym rozwoju, więc do pierwszych partii użyj osobnego zapisu.

Teksty kart pochodzą z oficjalnej lokalizacji bety. Interfejs przetłumaczono z pomocą AI i może zawierać błędy językowe. Komunikaty wymiany talii są dostępne we wszystkich 13 językach; część starszych wskazówek nadal korzysta z angielskiego. Propozycje poprawek są mile widziane.

**Steam Deck:** mod działa na Steam Decku (sprawdzone przez autora).

## Nowości w 0.9.0

- Eksport wyświetla kod BG1.
- Polecenia konsoli dla zasobów kolekcji, wyszukiwania kart, kolekcji frakcji i zapasu beczek u karczmarzy.
- Karty trafiające na cmentarz lecą do właściwego cmentarza; karty specjalne robią to po rozpatrzeniu efektu. Efekty wygnania i rozpuszczania pozostają.
- Wbudowane definicje dawnych przedmiotów Redux pomagają zapobiegać utracie ekwipunku i ciała przy wczytywaniu zapisu po zmianie moda. Nie odzyskują danych już utraconych i zapisanych.
- Poprawione odstępy menu, stan talii i przyciski; kontroler pozwala przejść z widocznej półki kart do zapisu i z powrotem.
- Portrety dowódców poruszają się dalej po wejściu na ekranie VS. Wejście królowej krabopająków zaczyna się wraz z jej głosem. Classic 1.32 zawiera poprawki mrozu i efektów ataków.
- Pełny podgląd karty w stylu bety: duża karta z oryginalnym sztandarem frakcji z bety 0.9.24 (frakcje, karty neutralne i dowódcy), siła bazowa, czytelny cytat, wyróżnione słowa kluczowe i przewijanie ←/→.
- Wklejanie kodu talii ze schowka Windows na ekranie importu (przycisk Wklej lub Ctrl+V; wymaga Optional-CopyButton).
- Samouczek rozszerzony do 10 stron: mulligan i dobieranie, rzędy i sąsiedzi, statusy kart.
- Poprawione karty zgodnie z betą: Myrgtabrakke zadaje 2 obrażenia trzy razy, zdolność Haralda Kaleki trafia dziesięć razy.
- Ulepszono obsługę kopii zapasowych kolekcji i talii. Może to pomóc w niektórych przypadkach utraty postępów; przywrócenie zależy od danych dostępnych w kopii zapasowej.


## SI i interfejs

Poprawiono ocenę Igni, Yrdena, pogody Birny i zdolności pancerza redańskiego rycerza, elity oraz giermka. Po pasie pościg uwzględnia rzeczywiste zagrania i granice tur; ostatni pas nie dodaje kolejnego efektu. W pierwszej rundzie jedna karta straty bywa opłacalna, dwie wymagają oceny, a trzech unika się przy opcjonalnym pościgu. Ratowanie meczu ma pierwszeństwo. Poprawiono dopasowanie tłumaczonych przycisków i odstępy.

Isengrim: Wygnaniec porównuje teraz kartę specjalną i tworzenie elfa, także po Dekrecie królewskim. SI unika Manekina bez prawidłowego sojuszniczego celu brązowego lub srebrnego i ocenia losową ofertę trzech kart bez podglądania przyszłych wyników.

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

## Udostępnianie talii

Eksport wyświetla kod BG1 niezależny od języka. Kopiuj umieszcza go bezpośrednio w schowku Windows; wklej go gdziekolwiek przez Ctrl+V. Potrzebny jest opcjonalny folder Optional-CopyButton: skopiuj jego folder bin do katalogu gry (dinput8.dll i plugins/GwentBetaClipboard.asi obok witcher3.exe). Sam mod działa również bez niego. Jeśli inny mod ma już własny dinput8.dll, zostaw go i wczytaj GwentBetaClipboard.asi jego loaderem ASI. Bez tych plików przyciski Import i Eksport są ukryte. Import przyjmuje cały kod BG1 w polu tekstowym.

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

3. Skopiuj Mods z archiwum do katalogu gry obok bin i content. Dla Classic 1.32 skopiuj też dołączony katalog DLC. Ścieżki: Mods/modBetaGwentClassic132/content i DLC/dlcBetaGwentClassic132Assets + DLC/dlcBetaGwentClassic132Items dla 1.32; Mods/modBetaGwent0924/content dla Next-Gen. Zastąp tylko poprzednie katalogi tego moda, zachowując inne mody i DLC.

4. Wczytaj zapis. Zwykłe menu talii Gwinta otwiera edytor i wybór języków; rozmowa z grającym NPC rozpoczyna partię. Zapisz grę, aby zachować wybór.

## Classic 1.32: rozmiar i DLC

Classic zajmuje około 623 MB, Next-Gen 448 MB, przy tych samych kartach i zasadach. Starszy format i limit około 32 MiB na asynchronicznie ładowany zasób wymagają osobnych stron grafiki. W Classic należy skopiować Mods oraz DLC. DLC/dlcBetaGwentClassic132Assets + DLC/dlcBetaGwentClassic132Items zawiera niezbędną grafikę i rejestrację zasobów, bez nowej fabuły. Około 105 MB pobieranego archiwum przypada na ten folder; reszta różnicy wynika z przygotowania zasobów dla starego silnika.

## Wymagania

The Witcher 3 na PC. Wybierz osobną kompilację Classic 1.32 albo Next-Gen (pakiet oznaczony 5.0+). Do gry nie są potrzebne REDkit, Wwise ani instalator EXE.

## Kompatybilność

Definicje dawnych przedmiotów Redux są wbudowane na potrzeby wczytywania zapisów; usuń przestarzały katalog modBetaGwentReduxCompat. Przy przejściu z Redux użyj kopii zapisu sprzed utraty ekwipunku lub ciała: utracone dane nie zostaną odzyskane. Karty Redux nie są zamieniane na kolekcję Beta; nie gwarantujemy zgodności ze wszystkimi funkcjami Redux/Redo Expansion. Inne przebudowy Gwinta oraz zmiany jego menu, handlu lub nagród mogą powodować konflikty. Po zmianie modów ponownie scal kolidujące skrypty w Script Merger.

## Redux

Spośród 400 sprawdzonych nazw starych przedmiotów 197 zachowuje definicje gry, a 203 otrzymują nieaktywne definicje w zwykłej grze i NG+. Są ukryte, nic nie ważą i nie mają wartości. Utracony ekwipunek nie jest odzyskiwany. Przy odinstalowaniu pozostałe przedmioty Redux ponownie potrzebują pierwotnego dostawcy definicji.

## Wbudowane czyszczenie przed odinstalowaniem

Osobny mod czyszczący nie jest potrzebny. Zrób kopię zapisu, zakończ partię, wyjdź z walki i zamknij menu. bg_clean_preview() tylko wyświetla pomoc. Przy nadal zainstalowanym modzie potwierdź:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Usuwane są kolekcja, talie, zasoby, ustawienia, znane nagrody, kopie zapasowe i przedmioty betagwent_* z ekwipunku gracza. Zapisana blokada zapobiega odtworzeniu danych także po ponownym wczytaniu. Zapisz w NOWYM slocie, zamknij grę, usuń mod i jego DLC Classic, zaktualizuj Script Merger, wczytaj nowy slot i zapisz ponownie. Zadania, osiągnięcia i wydane korony pozostają. Niewczytani kupcy, schowek i pojemniki świata nie są przeszukiwane. Osierocone fakty nagród mogą wymagać save_fact_index.py i bg_clean_keys('…') po potwierdzeniu. Fizyczne usunięcie wszystkich historycznych śladów nie jest gwarantowane. Jeśli części przedmiotów Beta nie da się usunąć, zamiast sukcesu pojawi się INCOMPLETE: wyrzuć je lub sprzedaj i powtórz polecenie. Przy odinstalowaniu usuń też pliki Optional-CopyButton, jeśli je instalowano: bin\…\plugins\GwentBetaClipboard.asi oraz dinput8.dll z tego moda (nie z innego).

**Po odinstalowaniu:** skopiuj folder z folderu After-Uninstall archiwum do katalogu gry (Next-Gen: Mods/modBetaGwentKeepItems; 1.32: DLC/dlcBetaGwentClassic132KeepItems). Zawiera ukryte definicje przedmiotów moda, dzięki czemu kupcy, skrytka i pojemniki, w których wciąż są karty lub beczki bety, nie tracą całego ekwipunku. Nie instaluj go razem z modem.

## Do wersji 1.0

Do 1.0 priorytetem będą poprawki tłumaczeń i błędów oraz dalsze ulepszanie SI i interfejsu. Testy automatyczne nie zastępują prób w grze ani rzeczywistego zapisu i wczytania po czyszczeniu.

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

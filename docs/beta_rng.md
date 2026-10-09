# RNG оригинальной Beta 0.9.24

Обновлено: 2026-10-02. Прочитан `GwentCore.MersenneTwisterRandom` из
оригинальной Assembly-CSharp.dll. [Исходный IL](D:/w3mod/docs/evidence/beta-cancel-rng-il.txt),
[manifest извлечения](D:/w3mod/docs/evidence/beta-rng-extraction.json),
[исполненные fixtures](D:/w3mod/docs/evidence/beta-rng-fixtures.json).

## Что проверено исполнением

В отдельную сборку скопированы23 метода с совпадающим текстом инструкций.
Четыре decoder-функции строк исключений заменены явными stub-методами:
проверяются типы исключений, их оригинальные сообщения не проверяются.
Конструктор с seed от часов исключён. Выделенная сборка не ссылается на
Assembly-CSharp или Unity. **37/37 checks прошли**: повторяемость восьми seeds,
счётчик вызовов, границы диапазонов, copy, rewind, две границы twist и
численные особенности overloads. Это oracle отдельных методов, а не
исполненный shuffle/timeout/rollback trace всего матча.

| Операция | Прочитанная и проверенная семантика |
|---|---|
| Seed | Начальное состояние использует `(uint)seed \| 1`; recurrence multiplier69069 |
| Состояние | Массив625 uint; граница twist624; копируются seed, счётчик и состояние |
| NextUnsigned | Один draw увеличивает NumTimesCalledSinceCreation на один |
| Next() | Absolute value signed reinterpretation uint; Int32.MinValue заменяется Int32.MaxValue |
| Next(max) | Next()%max; при max0 возвращает0 без расходования RNG |
| Next(min,max) | При равных границах возвращает min без draw; обычный диапазон Next(max-min)+min |
| NextDouble | Single-precision промежуточное `(float)Next()*4.6566128730773926e-10f`, затем double |
| NextFloat(min,max) | Границы умножаются на1000, приводятся к int с truncation; результат делится на1000f |
| NextBytes | NextDouble **%256**, затем byte conversion; fixture seed101 дал16 нулевых bytes при16 draws |
| Copy / copy ctor | Сохраняют продолжение последовательности, InitialSeed и счётчик |
| SetToNewSeededPosition | Воспроизводит позицию указанного seed, включая rewind того же seed |

Seeds0/1,2/3,−2/−1 дают попарно одинаковые последовательности; InitialSeed
сохраняет исходный аргумент. `Next()` не является маскированием старшего бита.
Full signed range min=Int32.MinValue/max=Int32.MaxValue переполняет разность
и даёт ArgumentOutOfRangeException. Float-округление NextDouble не даёт
оснований обещать строгий результат меньше1 для всех состояний.

Контрольный префикс seed0 (первые восемь NextUnsigned):

```text
3796174982, 2915266716, 2911072271, 2915266718,
2927982288, 2932176449, 2927982290, 2932176451
```

Полные16-элементные векторы восьми seeds записаны в fixtures JSON. Название
класса не позволяет подменить его современной стандартной реализацией MT.

## Воспроизведение

```powershell
powershell -NoProfile -File D:\w3mod\tools\oracle\extract_beta_rng.ps1
dotnet run --project D:\w3mod\tools\oracle\beta-rng-ref -- D:\w3mod
```

Используется установленный .NET7 SDK, NuGet sources очищены. Extractor читает
оригинальную DLL как metadata; harness запускает только выделенную сборку,
проверяет hashes и точность копирования до исполнения.

## Следующий перенос

WitcherScript integer RNG написан и скомпилирован в37:
BetaGwent/scripts/game/betagwent/randomGenerator.ws. Signed storage хранит uint32
bit patterns; логический right shift выражен через положительное division и
отдельный sign bit, left shifts — умножениями с32-bit overflow. WScript не
поддерживает << / >>, literal Int32.Min записан выражением (-2147483647 - 1).
NextBounded покрывает нужные shuffle/mulligan bounds; invalid negative bound
локально возвращает0, CLR exception semantics не заявлены перенесёнными.
Float/bytes/copy/rewind/state serialization ещё не переносились.
Native integer overflow и последовательность пока не сверены с vectors. После этого проверить расход draws на timeout
requests: повторный случайный candidate тоже расходует RNG. Shuffle,
mulligan, rollback и card effects должны получить отдельные исходные traces;
37 fixtures не закрывают эти цепочки.


## Использование в закрытой дуэли37

Source-derived ListExt.Shuffle тратит draws с bounds25..2 на каждую колоду
(48 на две колоды). Один RandRange выбирает seed среды разработки; остальные
deck operations используют CBetaGwentRandomGenerator. После twist оригинальный
IL записывает cursor=words[1] ДО мутации массива, а обычные NextUnsigned
темперируют scalar cursor++, не successive array entries. Twist возвращает
темперированное words[0]; эту необычную последовательность перенос сохраняет.
Источники shuffle/MoveAction: docs/evidence/beta-shuffle-location-il.txt.

Mulligan берёт NextBounded(deckCount) до incoming move. Incoming занимает
старый hand index outgoing, outgoing вставляется в случайный deck index;
порядок добора теперь читается по locationIndex. Blacklist, reservation и
fallback прочитаны из RequestMulliganAction. Никакого whole-game scheduler
trace или native acceptance новой цепочки на этом этапе не добавлено.

# Classic: файл найден, объект не создан

Сбор пользователя: classic132-resource-feedback/20261016-150602-989959.
Exit 0, timeout false, установленный fix8 не изменился. На 156.066 секунде
DEPOT_LOOKUP для gameplay/gui_new/swf/gwint/deck_builder.redswf получил
fileFound=true, тип CBundleDiskFile. RESOURCE_LOAD_RESULT: resourceObject=0,
loaded=false. Затем Loader failed to open. Заголовка нашего большого SWF
среди 54 CR2W_HEADER нет; изменённый CMenuResource прочитан успешно.
FileState: byte +0x28=0x28, +0x40=26654 (глобальный file ID).

GetOrLoad (RVA 0x921f0) отказывает при flag bit 8. Он также ставит этот флаг,
если класс ресурса не получен. Значит, искать ошибку AS3 по этому результату
преждевременно. Код открытия bundle исследован без запуска exe; выводы
сохранены в classic081-complete-audit/bundle-*.txt.

CBundleReader::CreateReader, RVA 0xc8060, имеет отдельную ветку для packed
больше 0x400000 (4 МиБ). Runtime entry +0xc — packed bytes, +0x10 — memory
bytes, +0x14 — compression. Большой несжатый ресурс допускается при равных
размерах, затем открывается отдельным raw reader физического bundle. Для
сжатого packed>4 МиБ этот синхронный reader возвращает null. Следовательно,
сам порог не доказывает запрет больших файлов: рабочая raw-ветка предусмотрена.
Неизвестны фактические размеры/compression после merge metadata и результат
Open физического файла. Конфигурация 30/70 МиБ не объявлена причиной.

Подготовлен bundle-профиль capture_scaleform.py и ручной
BetaGwent/release/Classic132-Capture-Bundle.cmd. Точки:

| RVA | Чтение |
| --- | --- |
| 0xc8060 | Runtime entry и физический путь bundle до выбора ветки |
| 0xc80ad | Результат открытия большого raw reader |
| 0xe5241 | Путь физического файла, результат Open, TEB LastErrorValue |
| 0x68b14c | Скрытые сообщения GFx |

Логируются крупные запросы, ID 26654 даже при неожиданном малом размере и
запросы modBetaGwent. LastErrorValue читается из TEB+0x68; адрес TEB взят из
CREATE_PROCESS/CREATE_THREAD. Ошибка трактуется только в контексте Open=false.
Сигнатуры и SHA exe сохранены в bundle-trace-points.json. Hardware self-test
четырёх точек, двух потоков, выхода и safe detach прошёл; Python compile
прошёл. Игра агентом не запускалась, установка после fix8 не менялась.
Это диагностическая работа, не новый fix и не подтверждение работоспособности.

## Результат bundle-профиля

Сбор пользователя classic132-bundle-feedback/20261016-151957-618681:
exit 0, timeout false, установленная сборка прежняя. Физический mod bundle
открыт успешно в 5.473 секунды; малые ресурсы мода читаются. Два больших
native raw-reader (28.99 и 28.96 MB) также открыты. На попытке меню в
131.643 секунды снова Loader failed to open, но запроса нужного файла в
CBundleReader::CreateReader нет. Поэтому ветка >4 МиБ не подтверждается
как место текущего отказа; она не объявляется причиной. Ненулевой LastError
при Open=true является неактуальным остатком и не трактуется как ошибка.

Подготовлен gate-профиль и Classic132-Capture-ResourceGate.cmd:
GetOrLoad (0x921f0), получение класса (0x93130), получение reader (0x98950)
и GFx message. Для целевого файла аппаратная точка временно переносится
на фактический return address того же потока, затем возвращается на entry.
Это позволяет за один запуск снять вход и результат всех трёх этапов.
Сохраняются флаги файла, class pointer/abstract flag/сравнение с CSWF class,
а при вызове bundle manager — merged FileInfo, entry chain и active bitmap.
Проверены исходные сигнатуры exe. Self-test дополнен наблюдением настоящего
return address в тестовом Python на двух потоках; normal exit/safe detach
успешны. Игра и mod-файлы после пользовательского сбора не изменялись.

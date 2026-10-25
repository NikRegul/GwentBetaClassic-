# Classic 1.32: отказ асинхронного чтения ресурсов свыше 32 МиБ

Полный сбор пользователя `classic132-full-feedback/20261016-161717-471138`
успешно завершился: 4341 событие, exit 0, timeout false, исходные инструкции
восстановлены, файлы игры/мода не изменились сборщиком. Снимок памяти
`failure-26654.dmp` размером 6576819465 байт остаётся локально.

## Подтверждённый отказ

На 15.950 секунде metadata выбрала правильную запись deck_builder.redswf:
fileId=26654, bundleId=86, bundleActive=true, offset=66060288,
packedBytes=memoryBytes=65938311, compression=0. Метод CDiskBundle по vtable+8
имеет RVA 0xc82c0. Он сразу вернул status=2, task=null; далее RESOURCE_FAILED,
resource=null и GFx Loader failed to open. До десериализации этого меню
выполнение не дошло. Попытка NPC в этом запуске также попала в уже отказавший
deck_builder: предматчевый выбор колоды не загрузился.

Код установленного exe (SHA 5112253787fbd927ecb979207efb91b99bcc9c7b041106b51285136bab41e1f7):

```
0xc82c6  cmp word ptr [rdx+4], 0        ; bundleId
0xc82d0  cmp dword ptr [rdx], 0         ; fileId
0xc82d5  mov r10d, [rdx+0x10]           ; memoryBytes
0xc82d9  cmp r10d, 0x2000000            ; 32 MiB
0xc82e0  jbe 0xc82ed                    ; proceed with async request
0xc82e2  mov eax, 2                     ; failure
```

Оба ID ненулевые, поэтому именно проверка размера отклонила запрос.
Это ограничение размера после распаковки: сжатие bundle его не устраняет.
Ресурсы остальных трёх больших меню тоже превышали эту границу.
Полный disassembly: `classic081-complete-audit/async-disk-reader-full.txt`.

## Fix9

Генератор `tools/universal/build_classic_streaming_fix.py` берёт проверенный fix8.
Четыре CSwfResource сохраняют native GFx побайтово, включая ABC, SymbolClass,
image IDs, ImageInfo и все имена изображений. Их 122 CSwfTexture вынесены в
отдельные cooked v163 .redswfx; исходный texture chunk целиком сохранён,
включая свойства, linkageName, размеры, формат, resident mip и пиксели.
Каждый внешний root имеет parent=0, cooked flags=8192.

Массив textures теперь содержит отрицательные индексы hard imports
CSwfTexture flags=0. Формат сверён с первичными исходниками
[CHandle](https://github.com/WolvenKit/WolvenKit-7/blob/main/WolvenKit.CR2W/Types/Generic/CHandle.cs)
и [CR2WImport](https://github.com/WolvenKit/WolvenKit-7/blob/main/WolvenKit.CR2W/CR2W/CR2WImport.cs).
Метод CSwfResource RVA 0x56cc30 обходит handles и строит карту по linkageName,
без ограничения на inline экспорт; disassembly сохранён в
`swf-texture-load-details.txt`.

Исторический stage96 открывал меню без текстур. В нём переписывались имена
изображений/texture linkage на общий digest. Fix9 сохраняет эти имена и
точные cooked chunks; заново регистрирует все новые пути, GUID и hard deps.
Причина старого отсутствия изображений окончательно не установлена, поэтому
рендеринг внешних текстур всё ещё требует игрового подтверждения пользователя.

Bundle v3 остаётся без сжатия. Metadata v6 содержит все новые записи, пути,
directory init, положительные int64 hash IDs и актуальные размеры/offsets.
SPED v2 сохраняет исходные GUID и добавляет детерминированные GUID страниц;
first содержит проверенные zero-terminated списки индексов hard dependencies.
Имена/linkage внешних страниц различаются по меню, дедупликации нет.

474 записи bundle, 467 CR2W, 339 фильмов и прежние 444 текстуры. 348 прочих
payloads совпадают с fix8 побайтово. Максимальная запись — 8160172 байт
(7.782 МиБ), все запросы ниже 32 МиБ. Четыре главных фильма теперь около 0.5 МиБ.
Скрипты, звук, AS-исходники, эффекты, механика и сохранения этой правкой не менялись.

39 тестов Classic прошли, включая hard-handle roundtrip, сохранность текстур/
фильма и отказ неверных ссылок. Все 16 проверок кандидата прошли: CRC, имена,
размеры, GUID, пути, все inline/external image bindings, покрытие hard deps,
maxima metadata и нативный предел async reader. Это структурная проверка,
не игровая приёмка.

Архив: `GwentBetaClassic-0.8.1-1.32-fix9-StreamingPatch.zip`,
SHA256 `9b684526ee2e4a0c6007b54b61ba6f6816d4b33b0b856e17f7c5c898362b7ec0`.
Установлены четыре файла поверх fix8; исходные копии и installation.json в
`classic081-streaming-fix9`. Игра агентом не запускалась, Computer Use не применялся.
Пользователь проверяет колоды/редактор/выход и NPC в одном запуске сборщика,
подключив диагностику через Enter после загрузки сохранения.

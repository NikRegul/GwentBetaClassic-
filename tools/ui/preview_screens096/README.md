Превью экранов 0.9.6 по реальному коду интерфейса (не снимок игры).

`harness.cjs` выполняет production-функции `BetaGwentBoard.as` (drawBetaDeckEditor, drawBetaMatchSetup, drawBetaCatalog и их помощники) в Node с записывающим списком отображения; `render.py` рисует записанные вызовы атласами HDArt/Elements и шрифтом PF Din. Не воспроизводятся: фильтры свечения, маски Scaleform, большие баннеры карт, точная метрика шрифтов.

    set ROOT=D:\w3mod
    node scenes.cjs ops.json
    python render.py ops.json out

`keywords.cjs` добавляет полный просмотр карты с отдельной колонкой пояснений и общую раскладку подсказок Xbox/PlayStation:

    node keywords.cjs keywords-ops.json
    python render.py keywords-ops.json out

Прямоугольные маски и перенос текста приближённо учитываются при записи; точные метрики, растеризация баннеров и 9-slice остаются ограничениями превью. Это проверка компоновки, а не снимок Scaleform.

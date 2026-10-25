# Classic 0.8.1: повторная проверка запуска меню

Пользователь сообщил: fix3 не устранил зависание. Установлены именно ресурсы
`0.8.1-classic-fix3-language-layout`: SHA-256 bundle и metadata совпали с
результатами сборки. Свежий scriptslog сохранён отдельно в
`BetaGwent/build/classic081-fix3-feedback/scriptslog.txt` (717933 байта).
Строк MENU_CONFIG_BEGIN и BetaGwent в этой копии нет. Это не доказывает
конкретную причину остановки GFx. Исправление cooked-текстур нельзя считать
решением пользовательского зависания.

В извлечённом из штатного `deck_builder.redswf` 1.32 байткоде:

* CoreMenu.registerMenu вызывает ExternalInterface.call("registerMenu", имя,
  this) без проверки ExternalInterface.available.
* GameAdapter.callGameEvent передаёт this как получателя прямого вызова
  _NATIVE_callGameEvent: getlocal0 / event / args / callpropvoid.

В нашем меню до fix4:

* первая отрисовка выполнялась в конструкторе до регистрации;
* контроллер и все обработчики ввода привязывались до registerMenu;
* registerMenu зависел от ExternalInterface.available;
* sender использовал Function.call, а не прямой вызов свойства объекта.

Fix4 регистрирует меню перед вводом и отрисовкой, убирает нестандартный для
штатного Classic протокола availability-gate и явно вызывает native-метод
на this. Добавлена защита от повторного ADDED_TO_STAGE и запуск при уже
прикреплённом stage. Ошибки инициализации перехватываются; при доступном мосте
передаются в существующий WS-лог и закрывают меню вместо оставленной паузы.

Для диагностической отметки используется существующий, не зависящий от
configured обработчик OnBetaGwentControllerTrace. В логе ожидается:

```text
CONTROLLER_INPUT code=0 action=AS_BRIDGE_READY mode=classic_boot_fix4 focus=
MENU_CONFIG_BEGIN menu=DeckBuilder
```

Если инициализация выбросила Error, focus содержит его текст, затем вызывается
OnBetaGwentBoardClose. Пустой focus означает, что перехваченной ошибки ввода/
первой отрисовки нет; наличие отметки подтверждает достижение native-bridge,
а не успешный полный игровой цикл.

Проверены 19 условий на настоящих методах AS, исполняемых с моделью native
моста: порядок регистрации/ввода/отрисовки, однократный handshake, отложенная
инъекция callback, ошибка ввода, логирование и закрытие. Это модельные проверки,
не запуск игры. Четыре меню скомпилированы; фактический send в каждом ABC
содержит прямой получатель getlocal0 без глобального получателя и Function.call.
Пять копий Board сохраняют UTF-8 BOM/CRLF. Скрипты WS и звук не меняются.

Сборка: `BetaGwent/build/classic081-boot-fix4`.
Генераторы: `tools/universal/prepare_classic_boot.py`, `build_classic_boot.py`.
Тест: `node tools/universal/test_classic_boot.js`.
Пакет: `BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix4-AllLanguages.zip`.
Результат открытия колод, редактора и выхода ожидается от пользователя.
Next-Gen-пакет и публичные тексты не менялись в этом исправлении.

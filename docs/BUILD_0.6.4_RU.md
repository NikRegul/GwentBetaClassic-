# Сборка 0.6.4 / Stage 140

Исходники ИИ заморожены в `BetaGwent/build/audit140/candidate-v3`, fingerprint `181cabb7921e031201fc148d594e65292b7305326d756eb2878bc009613211f1`. Относительно 0.6.3 изменены только `duelSession.ws` и `duelArchetypeAI.ws`; четыре меню собираются из текущего `BetaGwentBoard.as`. Банки голосов, 13 языков текста и ресурсы иллюстраций повторно используются без изменений.

```powershell
node tools/ai/check_strategy140.js BetaGwent/build/audit140/candidate-v3
node tools/ui/check_effects140.js
python tools/check_work140.py
./tools/Build-0.6.4.ps1 -Language ru
```

Для окружения без Python в PATH передайте `-Python` с полным путём к интерпретатору. В текущем рабочем окружении используется `C:/Users/NikR/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.

Сборку можно выполнять по шагам: `-Step scripts`, `menus`, `package`, `verify`. Уже выпущенный ZIP не перезаписывается. Повторная проверка готового пакета:

```powershell
./tools/Build-0.6.4.ps1 -Step verify -Language ru
```

Архивы 0.6.3 проверяются по SHA-256 и остаются неизменными. Нативная компиляция и проверка ресурсов не считаются игровой приёмкой. Изменения, разбор пользовательского лога и ручные сценарии описаны в [AI_ANIMATIONS_0.6.4_RU.md](AI_ANIMATIONS_0.6.4_RU.md).

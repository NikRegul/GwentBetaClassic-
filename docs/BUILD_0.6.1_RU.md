# Сборка 0.6.1 из PowerShell

Все пять полных пакетов (EN, RU, DE, IT, PT-BR), каждый с 13 языками текста:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-0.6.1.ps1
```

Только русский пакет:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-0.6.1.ps1 -Language ru
```

По умолчанию Step=full, Language=all: подготовка текущих исходников, регрессии (включая check_fixes061), нативная компиляция, четыре меню, упаковка и проверка фактических ZIP. Полная сборка всегда собирает заново: прежние архивы переносятся в BetaGwent/release/quarantine/0.6.1-<дата>, замороженные проекты — в BetaGwent/build/history137/<дата>. Ключ -RebuildExisting больше не обязателен (он нужен только для отдельного Step package). Старые версии 0.5.4 и 0.6.0 не затрагиваются. Не запускайте две сборки одновременно: общий замок остановит второй процесс.

Результат — BetaGwent/release/GwentBetaClassic-0.6.1-<ЯЗЫК>.zip и .zip.sha256; в конце скрипт печатает список архивов. Проверка: docs/evidence/validation137.json. Логи: BetaGwent/build/stage137/logs137. Скрипт не устанавливает мод и не публикует его.

Смена Step предназначена для диагностики. После любых изменений исходников запускайте full.

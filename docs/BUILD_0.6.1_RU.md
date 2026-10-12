# Сборка 0.6.1 из PowerShell

Все пять полных пакетов (EN, RU, DE, IT, PT-BR), каждый с 13 языками текста:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-0.6.1.ps1 -Language all -RebuildExisting
```

Только русский пакет:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-0.6.1.ps1 -Language ru -RebuildExisting
```

По умолчанию Step=full: подготовка текущих исходников, проверки, нативная компиляция, четыре меню, упаковка выбранных языков и проверка фактических ZIP. Не запускайте две сборки одновременно: общий замок остановит второй процесс.

RebuildExisting сохраняет прежние выбранные архивы в BetaGwent/release/quarantine/0.6.1-<дата>, а замороженные сборочные проекты — в BetaGwent/build/history137/<дата>. Он нужен для пересборки той же версии; без него скрипт откажется заменять существующий архив. Старые версии 0.5.4 и 0.6.0 не затрагиваются. При сборке all будет заново собран и RU.

Результат — BetaGwent/release/GwentBetaClassic-0.6.1-<ЯЗЫК>.zip и соседний .zip.sha256. Проверка: docs/evidence/validation137.json. Логи: BetaGwent/build/stage137/logs137. Скрипт не устанавливает мод и не публикует его.

Смена Step предназначена для диагностики. После любых изменений исходников запускайте full, чтобы не использовать устаревшую замороженную копию. Перед распространением исправления падения 0.6.1 нужна повторная проверка представления лидеров в игре.

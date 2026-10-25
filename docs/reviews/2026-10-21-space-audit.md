# Аудит места — 21 октября 2026

Ничего не удалено. Проверены D:\, профиль C:\Users\NikR и доступная часть C:\ProgramData. На F: измерено только свободное место. Системные и недоступные каталоги полностью не обследованы.

Свободно в начале: C: 214,31 ГиБ; D: 227,48 ГиБ; F: 393,58 ГиБ.

Первая группа кандидатов: **79.97 ГиБ логически**. Фактическая экономия может быть меньше из-за жёстких ссылок, сжатия и занятых файлов. Удаление диагностик и старых архивов имеет условия, перечисленные ниже.

| Кандидаты | Диск | ГиБ |
|---|---|---:|
| Кэши шейдеров NVIDIA | C: | 39.75 |
| Кэш Python uv | C: | 7.68 |
| Дампы WSL | C: | 3.53 |
| Дампы Witcher 3 | D: | 13.32 |
| Архивы прежних кандидатов 0.9.1 | D: | 15.70 |
| Дополнительно: старые резервные копии | D: | 11.81 |

## Кэши шейдеров NVIDIA

Очищать содержимое при закрытых играх и графических приложениях; занятые файлы пропускать. Кэш будет создан заново, первый запуск может сопровождаться компиляцией шейдеров. MiniConda не включена.

- `C:\Users\NikR\AppData\Local\NVIDIA\DXCache` — 39.715 ГиБ
- `C:\Users\NikR\AppData\Local\NVIDIA\GLCache` — 0.034 ГиБ

## Кэш Python uv

Кэш загрузок и сборок Python. Очищать штатной командой uv cache clean при отсутствии установки/сборки пакетов; впоследствии возможна повторная загрузка. Жёсткие ссылки могут уменьшить фактическую экономию.

- `C:\Users\NikR\AppData\Local\uv\cache` — 7.683 ГиБ

## Дампы WSL

Дампы падения WSL. Удаление лишает возможности повторного анализа этих состояний; рабочая файловая система WSL сюда не входит.

- `C:\Users\NikR\AppData\Local\Temp\wsl-crashes` — 3.527 ГиБ

## Дампы Witcher 3

Два дампа от 20 октября, суммарно 13,32 ГиБ. Удалять, если повторный анализ этих падений не нужен. Остальные файлы data сохранять.

- `D:\w3mod\data\witcher3.DMP` — 6.657 ГиБ
- `D:\w3mod\data\witcher3 (2).DMP` — 6.663 ГиБ

## Архивы прежних кандидатов 0.9.1

Только подкаталоги archives старых кандидатов: утрачивается установка/откат из соответствующих ZIP. Снимки исходников, компиляции и отчёты сохраняются. Текущий release091g-final2 и предыдущий release091f-final исключены. Базовые ZIP release090-final17-release не включены.

- `D:\w3mod\BetaGwent\build\release091-candidate11\archives` — 1.298 ГиБ
- `D:\w3mod\BetaGwent\build\release091-candidate12\archives` — 1.298 ГиБ
- `D:\w3mod\BetaGwent\build\release091-candidate4\archives` — 1.001 ГиБ
- `D:\w3mod\BetaGwent\build\release091-candidate5\archives` — 1.001 ГиБ
- `D:\w3mod\BetaGwent\build\release091-candidate6\archives` — 1.001 ГиБ
- `D:\w3mod\BetaGwent\build\release091-candidate7\archives` — 1.002 ГиБ
- `D:\w3mod\BetaGwent\build\release091-candidate8\archives` — 1.298 ГиБ
- `D:\w3mod\BetaGwent\build\release091-candidate9\archives` — 1.298 ГиБ
- `D:\w3mod\BetaGwent\build\release091a\archives` — 1.298 ГиБ
- `D:\w3mod\BetaGwent\build\release091b\archives` — 1.298 ГиБ
- `D:\w3mod\BetaGwent\build\release091d\archives` — 1.298 ГиБ
- `D:\w3mod\BetaGwent\build\release091e\archives` — 1.304 ГиБ
- `D:\w3mod\BetaGwent\build\release091f\archives` — 1.304 ГиБ

## Дополнительно: старые резервные копии

Дополнительная экономия только после отказа от этих точек отката. В частности install091-backup-20261020-172354 отмечена в отчётах как полная резервная копия установки до 0.9.1. Это не обычный кэш.

- `D:\w3mod\tmp\install091-backup-20261020-172320` — 1.307 ГиБ
- `D:\w3mod\tmp\install091-backup-20261020-172354` — 1.917 ГиБ
- `D:\w3mod\tmp\install091-backup-20261020-190945` — 1.784 ГиБ
- `D:\w3mod\tmp\install091-backup-20261020-194053` — 1.784 ГиБ
- `D:\w3mod\tmp\release-0.9.0-before-final11` — 1.003 ГиБ
- `D:\w3mod\tmp\release-0.9.0-before-final12` — 1.003 ГиБ
- `D:\w3mod\tmp\release-0.9.0-before-final13` — 1.003 ГиБ
- `D:\w3mod\tmp\release-0.9.0-before-final16` — 1.003 ГиБ
- `D:\w3mod\tmp\release-0.9.0-before-final17` — 1.003 ГиБ

## Где основной объём

`D:\w3mod` занимает 928,26 ГиБ, из них `BetaGwent\build` — 775,42 ГиБ. Старые сборки часто содержат копии ресурсов; возраст имени каталога не доказывает, что его можно удалить.

Крупные каталоги для отдельного разбора зависимостей, в предложенную очистку не включены:

- `BetaGwent\build\classic132-0.8.0-stage202-recovery-282e70b6ecd0` — 39,84 ГиБ.
- `BetaGwent\build\history137` — 22,59 ГиБ.
- `BetaGwent\build\release139` — 13,20 ГиБ.
- `BetaGwent\build\release185` и `release190` — по 11,59 ГиБ.

## Что сохранять

- `.git`, исходники и принятые эффекты, `depot`, оригинальные материалы, рабочие Wwise-проекты, подготовленные языковые ресурсы, `CleanBuild` и его ZIP.
- `BetaGwent\build\release091g-final2` — текущий build согласно release091-latest.json, версия 0.9.1g; release.json не подтверждает игровую приёмку.
- `release090-final12`, `release090-final17-release`, `release090-ui12`, `universal081` и другие входы, которые используют текущие инструменты. Полностью удалять build нельзя.
- `C:\Users\NikR\AppData\Local\wsl\{07db5c30-cc0d-4b51-9d29-5cfdfd0bb6bc}\ext4.vhdx` — 80,94 ГиБ: диск Linux, его удаление означает потерю среды и данных.
- `C:\Users\NikR\AppData\Local\Docker\wsl\disk\docker_data.vhdx` — 11,04 ГиБ: данные Docker.
- `C:\Users\NikR\AppData\Roaming\krita\ai_diffusion\server\models` — 33,78 ГиБ: модели Krita AI, не временные файлы.
- `C:\Users\NikR\AppData\Local\NVIDIA\MiniConda` — 6,42 ГиБ: не включать в очистку кэшей шейдеров.

Замечание: NVIDIA целиком занимает 46,17 ГиБ; собственно DXCache + GLCache — 39,75 ГиБ.

Точный перечень целей: `2026-10-21-cleanup-candidates.json`. Исходный инвентарь: `D:\w3mod\tmp\disk_cleanup_audit.json`. Перед удалением повторно проверить размеры, активные процессы, ссылки в путях и границы целевого каталога.

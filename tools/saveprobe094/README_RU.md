# Зонд вместимости сейва (Next-Gen)

Проверяет, сколько данных в полях игрока и в facts переживает цикл «сохранить → загрузить» без модов Beta Gwent.

- `mod/modBetaGwentSaveProbe`: скрипт зонда (генерируется `gen_probe.py`). Пишет 64 мелких int, затем 16 массивов, маркер, 16 строк, конечный маркер и facts `bgsp_f_*`. Объём растёт по этапам: 1024 / 4096 / 16384 / 65536 / 262144 int.
- `mod/modBetaGwentKeepItems`: копия из After-Uninstall 0.9.3, чтобы без мода не пропал инвентарь торговцев.
- `SaveProbe-Install.cmd [папка игры]`: временно переносит `modBetaGwent0924` в `Mods.saveprobe-off`, ставит зонд и KeepItems.
- `SaveProbe-Show.cmd`: собирает строки `SAVEPROBE` из scriptslog в `last_result.txt`.
- `SaveProbe-Restore.cmd`: возвращает мод, зонд переносит в `Mods.saveprobe-off\used-*`. Ничего не удаляет.

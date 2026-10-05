# Числовой oracle

2026-10-02:18 методов с точным IL match;40/40 fixtures прошли.
Evidence: beta-power-numeric-extraction.json и beta-power-numeric-fixtures.json.
Ранний комментарий Program.cs про pending execution относится к моменту
написания; текущий статус брать из executed evidence.

```powershell
powershell -NoProfile -File D:\w3mod\tools\oracle\extract_beta_power_numeric.ps1
dotnet run --project D:\w3mod\tools\oracle\beta-power-numeric-ref -- D:\w3mod
```

SetPowerAndArmor заменён одним raw Action<int,int> seam. Он наблюдает args/fields,
не выполняет clamp/events/death. Клиент/Unity не загружаются. Hashes/exact IL
проверяются до исполнения.40 cases: requested delta, fields before callback,
restore/no-op/negative, overflow, float rounding, throw/mutation callback.

Raw seam не обновляет current/armor; base/permanent writes исполняются.
Это boundary, не live handler. Out-of-range float conv.i4 исключён.
Native POWER55 скомпилирован28, пока не исполнен:
[BOARD_CHECK](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md).

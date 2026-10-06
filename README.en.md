[ 🇨🇱 [Español](README.md) ] | [ 🇺🇸 English ]

# Fuel-efficiency consolidation for a bus fleet

[![tests](https://github.com/Rxyxs/Trabajo-Vule/actions/workflows/tests.yml/badge.svg)](https://github.com/Rxyxs/Trabajo-Vule/actions/workflows/tests.yml)

A tool I built on the job for a bus company. Each depot logged its fuel loads in its own Excel sheet. This script merges all of those sheets into one report, computes the fuel efficiency (km per litre) of every load, and flags the loads that fall outside the expected range for each bus's model and emissions standard.

The repository contains none of the company's data. `generar_ejemplo.py` creates fictitious sheets with the same structure so it can be run.

## The problem

- **Many sheets, one analysis.** Every depot had its own file, with a `B.D` sheet. Reviewing fleet efficiency meant combining them by hand.
- **Hand-typed data.** Times came in as `830`, `8:30`, `22.40` or `23:05:00`, and licence plates with stray spaces and mixed case.
- **Efficiency depends on the previous reading.** The km driven for a load is the current odometer minus the one at the previous load **of the same bus**, which may have refuelled at another depot. So all loads have to be sorted together, by plate, date and time.
- **Every bus has its own normal range.** Expected efficiency depends on the model and the emissions standard (Euro 5, Euro 6…), which come in a separate ranges file.

## What it does

```
entrada_consolidados/*.xlsx  ─┐
  (one sheet per depot)       │   clean times and plates
                              ├─► sort by plate, date and time ─► KMACC and efficiency ─► Salida/REPORTE_RENDIMIENTO.xlsx
entrada_rangos/Rangos.xlsx   ─┘   join with the range for its model and standard                 (live formulas and colours)
  ("detalle" and "rango" sheets)
```

1. Reads every sheet in `entrada_consolidados/` and skips, with a warning, any that lacks the 13 required columns.
2. Normalizes times to `HH:MM` and plates to upper case with no spaces.
3. Sorts by plate, actual date and time, and computes `KMACC` (km since the same bus's previous load) and `RENDIMIENTO` (`KMACC / LITROS`).
4. Joins each bus with its range (`DESDE`–`HASTA`) by model and standard.
5. Fills the `REV` column: `BR` when efficiency is below the range, `CI` when it is above, and `0` when it is within range or is the bus's first load (no previous reading to compare against).
6. Writes the Excel report with `KMACC` and `RENDIMIENTO` as **formulas**, so anyone who corrects an odometer by hand sees it recalculate, and colour-coded: red below range, yellow above range, blue when there are no km to compute.

## Bugs found while reviewing it

- **Date sorting was wrong across months.** The date was turned into `dd-mm-yyyy` text before sorting. Sorted as text, `02-01-2025` comes before `15-12-2024`, so whenever loads crossed a month boundary each load's km were computed against the wrong reading. It now sorts on the real date and formats the text at the end. The test `test_kmacc_respeta_el_orden_cronologico_entre_meses` reproduces the case.
- **Every bus's first load was flagged `BR`.** With no previous reading, `KMACC` is 0, efficiency is 0 and it fell below the range. That row is no longer flagged: the Excel report already colours it blue as "no data".

## How to run it

```bash
pip install -r requirements.txt
python generar_ejemplo.py   # fictitious sheets in entrada_rangos/ and entrada_consolidados/
python main.py              # creates Salida/REPORTE_RENDIMIENTO.xlsx
pytest -q                   # 3 tests
```

With real data, put `Rangos.xlsx` in `entrada_rangos/` and each depot's sheet in `entrada_consolidados/`. All three folders and any `.xlsx` file are git-ignored, so operational data can't be committed by mistake.

**Required columns in each sheet (`B.D`):** `NUMERO INTERNO`, `PATENTE`, `ODOMETRO`, `LITROS`, `TERMINAL`, `FOLIO`, `FECHA PLANILLA`, `FECHA REAL`, `ROL`, `HORA`, `BOMBERO`, `TURNO`, `AD BLUE`.

**`Rangos.xlsx`:** a `detalle` sheet (`PATENTE`, `N INTERNO`, `MODELO`, `NORMA`) and a `rango` sheet (`MODELO`, `NORMA`, `RANGO_MIN`, `RANGO_MAX`).

## Stack

Python · pandas · openpyxl (formulas and conditional formatting) · pytest · GitHub Actions

## License

MIT — see [LICENSE](LICENSE).

## Author

**Pablo Reyes** — [github.com/Rxyxs](https://github.com/Rxyxs)

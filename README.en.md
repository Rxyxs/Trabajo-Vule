[Español](README.md) · **English**

# Fuel control for a bus fleet

[![tests](https://github.com/Rxyxs/bus-fleet-fuel-efficiency/actions/workflows/tests.yml/badge.svg)](https://github.com/Rxyxs/bus-fleet-fuel-efficiency/actions/workflows/tests.yml)

Real work for a bus company with 17 depots. Fuel was tracked in Excel sheets that each depot filled in separately: nobody could see the whole fleet's efficiency or reconcile what left the tanks with what went into the buses. The work had two stages:

1. **Consolidation and efficiency (Python).** Merges every depot's sheets into a daily consolidated file (`consolidar_planillas.py`), computes each load's efficiency in km per litre and flags the ones outside the range for the bus's model and emissions standard (`main.py`). It started as a VBA macro and then Jupyter notebooks that processed one file at a time; it ended up as scripts that process a whole folder.
2. **Data-capture app (AppSheet).** A mobile app that replaced the sheets: the operator records each load, the pump readings and the tank stock, and the app computes consumption, theoretical stock, AdBlue, KMACC and REV. The app lives in AppSheet with the company's data and is not in this repository; `control_estanques.py` reimplements its tank logic in Python so it can be tested.

The repository contains none of the company's data. `generar_ejemplo.py` creates fictitious data with the same structure.

## Stage 1: consolidation and efficiency

```
entrada_planillas/*.xlsm ─► consolidar_planillas.py ─► entrada_consolidados/YYYY-MM-DD.xlsx ─┐
  (one per depot and day)     one file per day,          (all depots)                         ├─► main.py ─► Salida/REPORTE_RENDIMIENTO.xlsx
                              all depots                 entrada_rangos/Rangos.xlsx ──────────┘             (live formulas and colours)
```

- **Sheets built for printing, not analysis.** Each depot fills in an `.xlsm` with 15 rows of decorative header, checklist columns nobody uses and formatted empty rows down to the bottom. `consolidar_planillas.py` reads the actual table, cleans it and writes one consolidated file per day with every depot; sheets missing columns are skipped with a warning.
- **The file name sets the date.** Each sheet covers one day. If the date typed inside doesn't match the file name, the load goes to the right day and a warning is printed, because that mistyped date also scrambles the km calculation.
- **Hand-typed data.** Times came in as `830`, `8:30`, `22.40` or `23:05:00`; they end up as `HH:MM`. Plates, upper case with no spaces.
- **Efficiency depends on the same bus's previous load**, which may have been at another depot. So all loads are sorted together to compute `KMACC` (km since the previous load) and `RENDIMIENTO` (`KMACC / LITROS`).
- **Each model has its own normal range** (for example 1.5–2.2 km/L for one model and 1.9–3.8 for another). The `REV` column marks `BR` below the range and `CI` above it.
- **The report is an Excel file with live formulas**: if someone fixes an odometer by hand, `KMACC` and `RENDIMIENTO` recalculate. Red below range, yellow above range, blue when there are no km to compute.

## Stage 2: the AppSheet capture app

The app replaced sheet entry with phone forms, with validations and automatic calculations.

| Part | What it does |
|---|---|
| **Bus form** | The operator enters the bus's internal number and the app fills in the plate; then they record mileage and litres. No retyping what is already in the database, and no bus with inconsistent data. |
| **Pickup-truck form** | A different flow, because pickups are identified by plate rather than internal number. |
| **Conditional logic** | The form shows only the fields that apply to the vehicle and record type. |
| **Tanks** | One opening and one closing reading per shift: pumps, AdBlue and measured stock. |
| **Pumps** | `TOTAL N 1 = PUMP 1 CLOSING − PUMP 1 OPENING` (same for pump 2). |
| **Theoretical stock** | `OPENING STOCK + DELIVERIES − CONSUMPTION`, to compare with the physical measurement. |
| **AdBlue** | `ADBLUE CLOSING − ADBLUE OPENING`. |
| **Indicators** | Efficiency, KMACC and REV computed from what was recorded, without a separate spreadsheet. |

**The bug that had to be fixed in the app:** at first, looking up a shift's opening reading could return **another** shift's. The result was negative consumption, huge consumption and meaningless theoretical stock. It was fixed by tying the opening and closing readings together by **folio, depot and date** at once.

### `control_estanques.py`: the same logic, with tests

```
entrada_estanques/Estanques.xlsx  ─►  pair OPENING and CLOSING  ─►  TOTAL N, AdBlue,      ─►  Salida/CONTROL_ESTANQUES.xlsx
  ("lecturas" and "recepciones")       by depot, date and folio       theoretical stock, gap
```

- Pairs each shift only by **depot + date + folio**, like the fixed app. Shifts missing an opening or closing reading, or with two readings of the same type, are not computed: they are listed separately.
- Computes `TOTAL N 1`, `TOTAL N 2`, `TOTAL ADBLUE`, theoretical stock and the **gap** against the measured tank level.
- Flags shifts with a negative total or a consumption impossible for one shift, the fingerprints of a wrong pairing or an extra digit.

## Tested on real sheets

The repository only ships fictitious data, but the pipeline was run locally on 26 real sheets from two days (1,754 loads from 17 depots). That run found two data problems the fictitious data didn't have, which the code now handles:

- **A whole sheet with the wrong month** (November instead of December, in both date columns). Those loads sorted a month early and produced **28 negative mileages**: the odometer seemed to go backwards.
- **Rows holding only the row number** at the end or start of the table, which slipped in as empty loads.

## Bugs found while reviewing the code

- **Date sorting was wrong across months.** The date was turned into `dd-mm-yyyy` text before sorting, and as text `02-01-2025` comes before `15-12-2024`. Whenever loads crossed a month boundary, km were computed against the wrong reading. It now sorts on the real date.
- **Buses with no range because of how the standard was written.** In the real ranges sheet, the same standard appears as `Euro V` and `EURO V`, or `Euro III Plus` and `EURO III PLUS`. The exact join left those buses without a range, so `REV` never flagged them: the report said "all fine" precisely where the data was miswritten. Model and standard are now normalized before the join, and any bus still left without a range is reported on screen (for example, a standard written as `O 500 EURO ELEC`, with the model inside it).
- **Every bus's first load was flagged `BR`.** With no previous load, `KMACC` is 0 and so is efficiency. That row is no longer flagged.

Each one has a test that reproduces it.

## How to run it

```bash
pip install -r requirements.txt
python generar_ejemplo.py       # fictitious data in entrada_planillas/, entrada_rangos/ and entrada_estanques/
python consolidar_planillas.py  # entrada_consolidados/YYYY-MM-DD.xlsx
python main.py                  # Salida/REPORTE_RENDIMIENTO.xlsx
python control_estanques.py     # Salida/CONTROL_ESTANQUES.xlsx
pytest -q                       # 13 tests
```

With real data, the files go in the same folders. Every input and output folder, and any `.xlsx`, is git-ignored so operational data can't be committed by mistake.

<details>
<summary>Input file formats</summary>

**Each depot's sheet:** a `Carga` sheet with the header on row 16 (the one with `KILOMETROS`). **Daily consolidated file (`B.D` sheet, written by `consolidar_planillas.py`):** `NUMERO INTERNO`, `PATENTE`, `ODOMETRO`, `LITROS`, `TERMINAL`, `FOLIO`, `FECHA PLANILLA`, `FECHA REAL`, `ROL`, `HORA`, `BOMBERO`, `TURNO`, `AD BLUE`.

**`Rangos.xlsx`:** a `detalle` sheet (`PATENTE`, `N INTERNO`, `MODELO`, `NORMA`) and a `rango` sheet (`MODELO`, `NORMA`, `RANGO_MIN`, `RANGO_MAX`).

**`Estanques.xlsx`:** a `lecturas` sheet (`TERMINAL`, `FECHA`, `FOLIO`, `TIPO` = INICIAL or FINAL, `PISTOLA 1`, `PISTOLA 2`, `ADBLUE`, `STOCK`) and a `recepciones` sheet (`TERMINAL`, `FECHA`, `FOLIO`, `LITROS`).

</details>

## Stack

Python · pandas · openpyxl (formulas and conditional formatting) · pytest · GitHub Actions · AppSheet

## License

MIT — see [LICENSE](LICENSE).

## Author

**Pablo Reyes** — [github.com/Rxyxs](https://github.com/Rxyxs)

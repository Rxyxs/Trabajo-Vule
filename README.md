[ 🇨🇱 Español ] | [ 🇺🇸 [English](README.en.md) ]

# Consolidación de rendimiento de combustible para una flota de buses

[![tests](https://github.com/Rxyxs/bus-fleet-fuel-efficiency/actions/workflows/tests.yml/badge.svg)](https://github.com/Rxyxs/bus-fleet-fuel-efficiency/actions/workflows/tests.yml)

Herramienta que hice en un trabajo para una empresa de buses. Cada terminal registraba las cargas de combustible en su propia planilla Excel. Este script une todas esas planillas en un solo reporte, calcula el rendimiento (km por litro) de cada carga y marca las que quedan fuera del rango esperado para el modelo y la norma de emisiones de cada bus.

El repositorio no trae datos de la empresa. `generar_ejemplo.py` crea planillas ficticias con la misma estructura para poder correrlo.

## El problema

- **Muchas planillas, un solo análisis.** Cada terminal tenía su propio archivo, con la hoja `B.D`. Para revisar el rendimiento de la flota había que juntarlos a mano.
- **Datos digitados a mano.** Las horas venían como `830`, `8:30`, `22.40` o `23:05:00`, y las patentes con espacios y minúsculas distintas.
- **El rendimiento depende de la lectura anterior.** Los km recorridos de una carga son el odómetro actual menos el de la carga anterior **del mismo bus**, que puede haber cargado en otro terminal. Por eso hay que ordenar todas las cargas juntas, por patente, fecha y hora.
- **Cada bus tiene su propio rango normal.** El rendimiento esperado depende del modelo y de la norma (Euro 5, Euro 6…), que vienen en un archivo de rangos aparte.

## Qué hace

```
entrada_consolidados/*.xlsx  ─┐
  (una planilla por terminal) │   limpiar horas y patentes
                              ├─► ordenar por patente, fecha y hora ─► KMACC y rendimiento ─► Salida/REPORTE_RENDIMIENTO.xlsx
entrada_rangos/Rangos.xlsx   ─┘   cruzar con el rango de su modelo y norma                       (fórmulas vivas y colores)
  (hojas "detalle" y "rango")
```

1. Lee todas las planillas de `entrada_consolidados/` y deja fuera, con un aviso, las que no traen las 13 columnas requeridas.
2. Deja las horas en `HH:MM` y las patentes en mayúsculas sin espacios.
3. Ordena por patente, fecha real y hora, y calcula `KMACC` (km desde la carga anterior del mismo bus) y `RENDIMIENTO` (`KMACC / LITROS`).
4. Cruza cada bus con su rango (`DESDE`–`HASTA`) según su modelo y norma.
5. Marca la columna `REV`: `BR` si el rendimiento queda bajo el rango, `CI` si queda sobre el rango, y `0` si está dentro o si es la primera carga del bus (no hay lectura anterior con qué comparar).
6. Escribe el reporte en Excel con `KMACC` y `RENDIMIENTO` como **fórmulas**, para que quien corrija un odómetro a mano vea el recálculo, y con colores: rojo bajo el rango, amarillo sobre el rango, azul cuando no hay km para calcular.

## Errores encontrados al revisarlo

- **El orden por fecha estaba mal entre meses.** La fecha se convertía a texto `dd-mm-aaaa` antes de ordenar. Ordenado como texto, el `02-01-2025` queda antes que el `15-12-2024`, así que cuando las cargas cruzaban un cambio de mes, los km de cada carga se calculaban contra la lectura equivocada. Ahora se ordena con la fecha real y el formato de texto se aplica al final. El test `test_kmacc_respeta_el_orden_cronologico_entre_meses` reproduce el caso.
- **La primera carga de cada bus salía marcada como `BR`.** Sin lectura anterior, `KMACC` vale 0, el rendimiento da 0 y caía bajo el rango. Ahora esa fila no se marca: el Excel ya la pinta azul como "sin dato".

## Cómo correrlo

```bash
pip install -r requirements.txt
python generar_ejemplo.py   # planillas ficticias en entrada_rangos/ y entrada_consolidados/
python main.py              # crea Salida/REPORTE_RENDIMIENTO.xlsx
pytest -q                   # 3 tests
```

Con datos reales, se ponen `Rangos.xlsx` en `entrada_rangos/` y las planillas de cada terminal en `entrada_consolidados/`. Las tres carpetas y cualquier `.xlsx` quedan fuera de git (`.gitignore`), para no subir datos operativos por error.

**Columnas requeridas en cada planilla (hoja `B.D`):** `NUMERO INTERNO`, `PATENTE`, `ODOMETRO`, `LITROS`, `TERMINAL`, `FOLIO`, `FECHA PLANILLA`, `FECHA REAL`, `ROL`, `HORA`, `BOMBERO`, `TURNO`, `AD BLUE`.

**`Rangos.xlsx`:** hoja `detalle` (`PATENTE`, `N INTERNO`, `MODELO`, `NORMA`) y hoja `rango` (`MODELO`, `NORMA`, `RANGO_MIN`, `RANGO_MAX`).

## Stack

Python · pandas · openpyxl (fórmulas y formato condicional) · pytest · GitHub Actions

## Licencia

MIT — ver [LICENSE](LICENSE).

## Autor

**Pablo Reyes** — [github.com/Rxyxs](https://github.com/Rxyxs)

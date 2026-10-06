**Español** · [English](README.en.md)

# Control de combustible para una flota de buses

[![tests](https://github.com/Rxyxs/bus-fleet-fuel-efficiency/actions/workflows/tests.yml/badge.svg)](https://github.com/Rxyxs/bus-fleet-fuel-efficiency/actions/workflows/tests.yml)

Trabajo real para una empresa de buses con 17 terminales. El combustible se controlaba con planillas Excel que llenaba cada terminal por separado: nadie podía ver el rendimiento de la flota completa ni cuadrar lo que salía de los estanques con lo que se cargaba a los buses. El trabajo tuvo dos etapas:

1. **Consolidación y rendimiento (Python).** Une las planillas de todos los terminales en un consolidado diario (`consolidar_planillas.py`), calcula el rendimiento de cada carga en km por litro y marca las que quedan fuera del rango de su modelo y norma (`main.py`). Empezó como una macro VBA y luego notebooks de Jupyter que procesaban un archivo a la vez; quedó en scripts que procesan una carpeta completa.
2. **App de captura (AppSheet).** Una aplicación móvil que reemplazó las planillas: el operador registra cada carga, las lecturas de las pistolas y el stock de los estanques, y la app calcula consumos, stock teórico, AdBlue, KMACC y REV. La app vive en AppSheet con los datos de la empresa y no está en este repositorio; `control_estanques.py` reimplementa su lógica de estanques en Python para poder probarla.

El repositorio no trae datos de la empresa. `generar_ejemplo.py` crea datos ficticios con la misma estructura.

## Etapa 1: consolidación y rendimiento

```
entrada_planillas/*.xlsm ─► consolidar_planillas.py ─► entrada_consolidados/AAAA-MM-DD.xlsx ─┐
  (una por terminal y día)    un archivo por día,        (todas las sedes)                    ├─► main.py ─► Salida/REPORTE_RENDIMIENTO.xlsx
                              todas las sedes            entrada_rangos/Rangos.xlsx ──────────┘             (fórmulas vivas y colores)
```

- **Planillas pensadas para imprimir, no para analizar.** Cada terminal llena un `.xlsm` con 15 filas de encabezado decorativo, columnas de checklist que no se usan y filas vacías con formato hasta el final. `consolidar_planillas.py` lee la tabla real, la limpia y escribe un consolidado por día con todas las sedes; deja fuera, con un aviso, las planillas a las que les faltan columnas.
- **La fecha la manda el nombre del archivo.** Cada planilla es de un día. Si la fecha digitada adentro no coincide con la del nombre, el consolidado va al día correcto y se avisa, porque esa fecha mal escrita también desordena el cálculo de km.
- **Datos digitados a mano.** Las horas venían como `830`, `8:30`, `22.40` o `23:05:00`; quedan en `HH:MM`. Las patentes, en mayúsculas y sin espacios.
- **El rendimiento depende de la carga anterior del mismo bus**, que puede haber sido en otro terminal. Por eso se ordenan todas las cargas juntas y se calcula `KMACC` (km desde la carga anterior) y `RENDIMIENTO` (`KMACC / LITROS`).
- **Cada modelo tiene su rango normal** (por ejemplo, 1,5–2,2 km/L para un modelo y 1,9–3,8 para otro). La columna `REV` marca `BR` bajo el rango y `CI` sobre él.
- **El reporte es un Excel con fórmulas vivas**: si alguien corrige un odómetro a mano, `KMACC` y `RENDIMIENTO` se recalculan. Rojo bajo el rango, amarillo sobre el rango, azul cuando no hay km para calcular.

## Etapa 2: la app de captura en AppSheet

La app reemplazó el registro en planillas por formularios en el celular, con validaciones y cálculos automáticos.

| Parte | Qué hace |
|---|---|
| **Formulario de buses** | El operador ingresa el número interno y la app trae la patente sola; luego registra kilometraje y litros. Evita digitar dos veces lo que ya está en la base y que un bus quede con datos inconsistentes. |
| **Formulario de camionetas** | Flujo distinto, porque las camionetas se identifican por patente y no por número interno. |
| **Lógica condicional** | El formulario muestra solo los campos que corresponden según el tipo de vehículo y de registro. |
| **Estanques** | Una lectura inicial y una final por turno: pistolas, AdBlue y stock medido. |
| **Pistolas** | `TOTAL N 1 = PISTOLA 1 FINAL − PISTOLA 1 INICIAL` (lo mismo para la pistola 2). |
| **Stock teórico** | `STOCK INICIAL + RECEPCIONES − CONSUMO`, para compararlo con la medición física. |
| **AdBlue** | `ADBLUE FINAL − ADBLUE INICIAL`. |
| **Indicadores** | Rendimiento, KMACC y REV calculados desde lo registrado, sin pasar por una planilla aparte. |

**El error que hubo que corregir en la app:** al principio, la búsqueda de la lectura inicial de un turno podía traer la de **otro** turno. El resultado eran consumos negativos, consumos enormes y stocks teóricos sin sentido. Se corrigió amarrando la lectura inicial y la final por **folio, terminal y fecha** a la vez.

### `control_estanques.py`: la misma lógica, con tests

```
entrada_estanques/Estanques.xlsx  ─►  emparejar INICIAL y FINAL  ─►  TOTAL N, AdBlue,  ─►  Salida/CONTROL_ESTANQUES.xlsx
  (hojas "lecturas" y "recepciones")    por terminal, fecha y folio     stock teórico, diferencia
```

- Empareja cada turno solo por **terminal + fecha + folio**, como la app ya corregida. Los turnos sin lectura inicial o final, o con dos lecturas del mismo tipo, no se calculan: se listan aparte.
- Calcula `TOTAL N 1`, `TOTAL N 2`, `TOTAL ADBLUE`, el stock teórico y la **diferencia** contra lo medido en el estanque.
- Alerta los turnos con un total negativo o un consumo imposible para un turno, que son las huellas de un cruce equivocado o de un dígito de más.

## Probado con planillas reales

El repositorio solo trae datos ficticios, pero el flujo se probó en local con 26 planillas reales de dos días (1.754 cargas de 17 terminales). Esa prueba encontró dos problemas de datos que los datos ficticios no tenían y que hoy el código maneja:

- **Una planilla completa con el mes mal digitado** (noviembre en vez de diciembre, en las dos columnas de fecha). Esas cargas se ordenaban un mes antes y producían **28 kilometrajes negativos**: el odómetro parecía retroceder.
- **Filas que solo tenían la numeración** al final o al comienzo de la tabla, que se colaban como cargas vacías.

## Errores encontrados al revisar el código

- **El orden por fecha estaba mal entre meses.** La fecha se pasaba a texto `dd-mm-aaaa` antes de ordenar, y como texto el `02-01-2025` queda antes que el `15-12-2024`. Cuando las cargas cruzaban un cambio de mes, los km se calculaban contra la lectura equivocada. Ahora se ordena con la fecha real.
- **Buses sin rango por cómo estaba escrita la norma.** En la planilla real de rangos, la misma norma aparece como `Euro V` y `EURO V`, o `Euro III Plus` y `EURO III PLUS`. El cruce exacto dejaba esos buses sin rango y `REV` nunca los marcaba: el reporte decía "todo bien" justo en los datos mal escritos. Ahora modelo y norma se normalizan antes del cruce, y los buses que igual quedan sin rango se avisan por pantalla (por ejemplo, una norma escrita como `O 500 EURO ELEC`, con el modelo metido adentro).
- **La primera carga de cada bus salía marcada `BR`.** Sin carga anterior, `KMACC` vale 0 y el rendimiento también. Ahora esa fila no se marca.

Cada uno tiene un test que lo reproduce.

## Cómo correrlo

```bash
pip install -r requirements.txt
python generar_ejemplo.py       # datos ficticios en entrada_planillas/, entrada_rangos/ y entrada_estanques/
python consolidar_planillas.py  # entrada_consolidados/AAAA-MM-DD.xlsx
python main.py                  # Salida/REPORTE_RENDIMIENTO.xlsx
python control_estanques.py     # Salida/CONTROL_ESTANQUES.xlsx
pytest -q                       # 13 tests
```

Con datos reales, los archivos van en las mismas carpetas. Todas las carpetas de entrada y salida, y cualquier `.xlsx`, quedan fuera de git para no subir datos operativos por error.

<details>
<summary>Formato de los archivos de entrada</summary>

**Planillas de cada terminal:** hoja `Carga` con el encabezado en la fila 16 (la de `KILOMETROS`). **Consolidado diario (hoja `B.D`, lo escribe `consolidar_planillas.py`):** `NUMERO INTERNO`, `PATENTE`, `ODOMETRO`, `LITROS`, `TERMINAL`, `FOLIO`, `FECHA PLANILLA`, `FECHA REAL`, `ROL`, `HORA`, `BOMBERO`, `TURNO`, `AD BLUE`.

**`Rangos.xlsx`:** hoja `detalle` (`PATENTE`, `N INTERNO`, `MODELO`, `NORMA`) y hoja `rango` (`MODELO`, `NORMA`, `RANGO_MIN`, `RANGO_MAX`).

**`Estanques.xlsx`:** hoja `lecturas` (`TERMINAL`, `FECHA`, `FOLIO`, `TIPO` = INICIAL o FINAL, `PISTOLA 1`, `PISTOLA 2`, `ADBLUE`, `STOCK`) y hoja `recepciones` (`TERMINAL`, `FECHA`, `FOLIO`, `LITROS`).

</details>

## Stack

Python · pandas · openpyxl (fórmulas y formato condicional) · pytest · GitHub Actions · AppSheet

## Licencia

MIT — ver [LICENSE](LICENSE).

## Autor

**Pablo Reyes** — [github.com/Rxyxs](https://github.com/Rxyxs)

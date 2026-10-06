"""
Control de estanques: la logica de la app de AppSheet, reimplementada en Python
Autor: Pablo Reyes
Descripcion: Empareja la lectura inicial y final de cada turno, calcula el volumen
             despachado por cada pistola (TOTAL N), el consumo de AdBlue y el stock
             teorico del estanque, y lo compara con la medicion fisica.

La app original vive en AppSheet; este modulo replica sus formulas para poder
probarlas con tests y datos ficticios. Las mismas reglas:

    TOTAL N 1      = PISTOLA 1 FINAL - PISTOLA 1 INICIAL
    TOTAL N 2      = PISTOLA 2 FINAL - PISTOLA 2 INICIAL
    TOTAL ADBLUE   = ADBLUE FINAL - ADBLUE INICIAL
    STOCK TEORICO  = STOCK INICIAL + RECEPCIONES - (TOTAL N 1 + TOTAL N 2)
    DIFERENCIA     = STOCK MEDIDO - STOCK TEORICO
"""

import os

import pandas as pd

DIR_ESTANQUES = "entrada_estanques"
ARCHIVO_ESTANQUES = os.path.join(DIR_ESTANQUES, "Estanques.xlsx")
ARCHIVO_SALIDA = os.path.join("Salida", "CONTROL_ESTANQUES.xlsx")

# El turno se identifica por estas tres columnas. En la app, buscar la lectura
# inicial solo por terminal (o solo por fecha) traia la de otro turno y producia
# consumos negativos o enormes: el cruce tiene que usar las tres.
CLAVE_TURNO = ["TERMINAL", "FECHA", "FOLIO"]
LECTURAS = ["PISTOLA 1", "PISTOLA 2", "ADBLUE", "STOCK"]

# Un estanque de terminal no despacha cientos de miles de litros en un turno: un
# total mayor que esto casi siempre es una lectura de otro turno o un digito de mas.
MAX_LITROS_TURNO = 20000


def emparejar_turnos(lecturas):
    """Une la lectura INICIAL y la FINAL de cada turno en una sola fila.

    Devuelve (pares, problemas). ``problemas`` lista los turnos que no se pueden
    calcular: sin inicial, sin final, o con mas de una lectura del mismo tipo.
    """
    df = lecturas.copy()
    df["TIPO"] = df["TIPO"].astype(str).str.strip().str.upper()
    df["TERMINAL"] = df["TERMINAL"].astype(str).str.strip().str.upper()
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

    problemas = []
    conteo = df.groupby(CLAVE_TURNO + ["TIPO"]).size()
    for (terminal, fecha, folio, tipo), n in conteo[conteo > 1].items():
        problemas.append((terminal, fecha, folio, f"{n} lecturas {tipo}"))

    df = df.drop_duplicates(CLAVE_TURNO + ["TIPO"], keep=False)
    ini = df[df["TIPO"] == "INICIAL"].set_index(CLAVE_TURNO)[LECTURAS]
    fin = df[df["TIPO"] == "FINAL"].set_index(CLAVE_TURNO)[LECTURAS]
    for clave in ini.index.difference(fin.index):
        problemas.append((*clave, "sin lectura FINAL"))
    for clave in fin.index.difference(ini.index):
        problemas.append((*clave, "sin lectura INICIAL"))

    pares = ini.join(fin, lsuffix=" INICIAL", rsuffix=" FINAL", how="inner").reset_index()
    problemas = pd.DataFrame(problemas, columns=CLAVE_TURNO + ["PROBLEMA"])
    return pares, problemas


def calcular_turnos(pares, recepciones):
    """TOTAL N por pistola, AdBlue, stock teorico y diferencia contra lo medido."""
    df = pares.copy()
    df["TOTAL N 1"] = df["PISTOLA 1 FINAL"] - df["PISTOLA 1 INICIAL"]
    df["TOTAL N 2"] = df["PISTOLA 2 FINAL"] - df["PISTOLA 2 INICIAL"]
    df["TOTAL ADBLUE"] = df["ADBLUE FINAL"] - df["ADBLUE INICIAL"]
    df["CONSUMO"] = df["TOTAL N 1"] + df["TOTAL N 2"]

    rec = recepciones.copy()
    rec["TERMINAL"] = rec["TERMINAL"].astype(str).str.strip().str.upper()
    rec["FECHA"] = pd.to_datetime(rec["FECHA"], errors="coerce")
    rec = rec.groupby(CLAVE_TURNO, as_index=False)["LITROS"].sum().rename(columns={"LITROS": "RECEPCIONES"})
    df = df.merge(rec, on=CLAVE_TURNO, how="left")
    df["RECEPCIONES"] = pd.to_numeric(df["RECEPCIONES"], errors="coerce").fillna(0)

    df["STOCK TEORICO"] = df["STOCK INICIAL"] + df["RECEPCIONES"] - df["CONSUMO"]
    df["DIFERENCIA"] = df["STOCK FINAL"] - df["STOCK TEORICO"]
    df["ALERTA"] = alertas(df)
    return df


def alertas(df):
    """Texto de alerta por turno; vacio si el turno esta bien."""
    def una(fila):
        motivos = []
        for col in ("TOTAL N 1", "TOTAL N 2", "TOTAL ADBLUE"):
            if fila[col] < 0:
                motivos.append(f"{col} negativo")
        if fila["CONSUMO"] > MAX_LITROS_TURNO:
            motivos.append("consumo imposible para un turno")
        return "; ".join(motivos)
    return df.apply(una, axis=1)


def main():
    print("Iniciando control de estanques...\n")
    if not os.path.exists(ARCHIVO_ESTANQUES):
        print(f"[ERROR] No se encontro {ARCHIVO_ESTANQUES}")
        return
    lecturas = pd.read_excel(ARCHIVO_ESTANQUES, sheet_name="lecturas")
    recepciones = pd.read_excel(ARCHIVO_ESTANQUES, sheet_name="recepciones")

    pares, problemas = emparejar_turnos(lecturas)
    turnos = calcular_turnos(pares, recepciones)
    for _, p in problemas.iterrows():
        print(f"[ADVERTENCIA] {p['TERMINAL']} {p['FECHA']:%d-%m-%Y} folio {p['FOLIO']}: {p['PROBLEMA']}")
    n_alertas = int((turnos["ALERTA"] != "").sum())
    print(f"[OK] {len(turnos)} turnos calculados, {n_alertas} con alerta, {len(problemas)} sin calcular")

    os.makedirs(os.path.dirname(ARCHIVO_SALIDA), exist_ok=True)
    salida = turnos.copy()
    salida["FECHA"] = salida["FECHA"].dt.strftime("%d-%m-%Y")
    with pd.ExcelWriter(ARCHIVO_SALIDA) as w:
        salida.to_excel(w, sheet_name="turnos", index=False)
        problemas.to_excel(w, sheet_name="sin calcular", index=False)
    print(f"[OK] Archivo generado: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()

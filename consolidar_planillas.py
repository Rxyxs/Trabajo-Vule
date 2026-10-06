"""
Consolidacion diaria de las planillas de carga de cada terminal
Autor: Pablo Reyes
Descripcion: Lee las planillas que llena cada terminal (hoja "Carga", con el encabezado
             en la fila 16), las limpia y escribe un consolidado por dia con todas las
             sedes, en el formato que lee main.py (hoja "B.D").

Es el primer paso del flujo:

    entrada_planillas/*.xlsm  ->  consolidar_planillas.py  ->  entrada_consolidados/AAAA-MM-DD.xlsx
                                                           ->  main.py  ->  Salida/REPORTE_RENDIMIENTO.xlsx

Antes este paso se hacia con una macro VBA y luego con notebooks de Jupyter, archivo
por archivo. Aqui procesa una carpeta completa de una vez.
"""

import os
import re

import pandas as pd

DIR_PLANILLAS = "entrada_planillas"
DIR_CONSOLIDADOS = "entrada_consolidados"

HOJA = "Carga"
FILA_ENCABEZADO = 15  # el encabezado real esta en la fila 16 de Excel

# Columnas que trae la planilla y no se usan: numeracion, checklist del bus y celdas sin nombre
COLUMNAS_SOBRANTES = ("N°", "N�", "REJILLA", "TAPA", "NUEVA_COLUMNA", "NUEVA COLUMNA")

COLUMNAS_CONSOLIDADO = ['TERMINAL', 'FOLIO', 'FECHA PLANILLA', 'FECHA REAL', 'NUMERO INTERNO',
                        'PATENTE', 'ROL', 'ODOMETRO', 'LITROS', 'HORA', 'BOMBERO', 'TURNO', 'AD BLUE']


def leer_planilla(ruta):
    """Lee la hoja de cargas de una planilla y devuelve solo las filas con datos."""
    df = pd.read_excel(ruta, sheet_name=HOJA, header=FILA_ENCABEZADO, engine="openpyxl")
    df.columns = [str(c).strip().upper() for c in df.columns]

    # La planilla trae filas vacias con formato hasta el final de la hoja: se corta en la
    # ultima fila con al menos 3 datos, igual que en el notebook original.
    validas = df.dropna(thresh=3)
    if validas.empty:
        return df.iloc[0:0]
    df = df.loc[:validas.index[-1]]

    sobrantes = [c for c in df.columns if c in COLUMNAS_SOBRANTES or c.startswith("UNNAMED")]
    df = df.drop(columns=sobrantes).rename(columns={"KILOMETROS": "ODOMETRO"})
    # Despues de quitar las columnas sobrantes: una fila que solo tenia la numeracion N°
    # queda vacia y se descarta
    return df.dropna(how="all")


def fecha_del_nombre(archivo):
    """'TERMINAL NORTE - 23-12-2024.xlsm' -> 2024-12-23; None si el nombre no trae fecha."""
    m = re.search(r"(\d{2})-(\d{2})-(\d{4})", archivo)
    return pd.Timestamp(f"{m.group(3)}-{m.group(2)}-{m.group(1)}") if m else None


def consolidar(dir_planillas=DIR_PLANILLAS, dir_salida=DIR_CONSOLIDADOS):
    """Une todas las planillas y escribe un archivo por dia. Devuelve los archivos creados."""
    archivos = sorted(f for f in os.listdir(dir_planillas)
                      if f.lower().endswith((".xlsm", ".xlsx")) and not f.startswith("~$"))
    partes = []
    for archivo in archivos:
        try:
            df = leer_planilla(os.path.join(dir_planillas, archivo))
        except Exception as e:  # una planilla danada no debe detener el resto
            print(f"[ADVERTENCIA] No se pudo leer '{archivo}': {e}")
            continue
        faltantes = sorted(set(COLUMNAS_CONSOLIDADO) - set(df.columns))
        if faltantes:
            print(f"[ADVERTENCIA] '{archivo}' omitido: faltan columnas {faltantes}")
            continue
        df["ARCHIVO ORIGEN"] = archivo
        # Cada planilla es de un dia: el dia lo dice el nombre del archivo. Si la fecha
        # digitada adentro no coincide (paso con un mes mal escrito), se avisa: el consolidado
        # va al dia del archivo, pero la fecha mal digitada hay que corregirla en la planilla.
        dia = fecha_del_nombre(archivo)
        digitada = pd.to_datetime(df["FECHA PLANILLA"], errors="coerce").dt.normalize()
        if dia is not None and (digitada != dia).any():
            distintas = sorted({f"{d:%d-%m-%Y}" for d in digitada.dropna() if d != dia})
            print(f"[ADVERTENCIA] '{archivo}': {int((digitada != dia).sum())} cargas con FECHA PLANILLA "
                  f"{distintas or ['vacia']}, distinta del dia del archivo ({dia:%d-%m-%Y})")
        df["DIA"] = dia if dia is not None else digitada
        partes.append(df)
        print(f"[OK] {archivo}: {len(df)} cargas")

    if not partes:
        print("[ERROR] No hay planillas validas para consolidar.")
        return []

    todo = pd.concat(partes, ignore_index=True)
    sin_dia = todo["DIA"].isna()
    if sin_dia.any():
        print(f"[ADVERTENCIA] {int(sin_dia.sum())} cargas sin fecha (ni en el nombre del archivo ni digitada) quedan fuera")
        todo = todo[~sin_dia]

    os.makedirs(dir_salida, exist_ok=True)
    creados = []
    for fecha, dia in todo.groupby(pd.to_datetime(todo["DIA"]).dt.date):
        ruta = os.path.join(dir_salida, f"{fecha:%Y-%m-%d}.xlsx")
        dia[COLUMNAS_CONSOLIDADO + ["ARCHIVO ORIGEN"]].to_excel(ruta, sheet_name="B.D", index=False)
        creados.append(ruta)
        print(f"[OK] Consolidado {fecha:%d-%m-%Y}: {len(dia)} cargas de {dia['TERMINAL'].nunique()} terminales")
    return creados


if __name__ == "__main__":
    consolidar()

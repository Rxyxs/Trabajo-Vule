"""
Genera archivos de entrada ficticios para probar main.py sin datos reales.

    python generar_ejemplo.py
    python main.py

Crea entrada_rangos/Rangos.xlsx y dos planillas en entrada_consolidados/.
Las patentes, numeros internos y lecturas son inventados.
"""

import os

import numpy as np
import pandas as pd

import main

BUSES = [("ABCD12", "101", "M1", "EURO5"), ("EFGH34", "102", "M1", "EURO6"),
         ("IJKL56", "103", "M2", "EURO6")]


def generar(seed=7):
    rng = np.random.default_rng(seed)
    main.crear_carpetas()

    detalle = pd.DataFrame(BUSES, columns=["PATENTE", "N INTERNO", "MODELO", "NORMA"])
    rango = pd.DataFrame({"MODELO": ["M1", "M1", "M2"], "NORMA": ["EURO5", "EURO6", "EURO6"],
                          "RANGO_MIN": [2.2, 2.4, 1.8], "RANGO_MAX": [3.4, 3.6, 2.8]})
    with pd.ExcelWriter(os.path.join(main.DIR_RANGOS, "Rangos.xlsx")) as w:
        detalle.to_excel(w, sheet_name="detalle", index=False)
        rango.to_excel(w, sheet_name="rango", index=False)

    # Cargas diarias de cada bus entre mediados de diciembre y enero, cada una
    # registrada en la planilla del terminal donde cargo
    fechas = pd.date_range("2024-12-16", "2025-01-15", freq="D")
    planillas = {"TERMINAL NORTE": [], "TERMINAL SUR": []}
    for patente, interno, _, _ in BUSES:
        odometro = int(rng.integers(100_000, 300_000))
        for fecha in fechas[rng.random(len(fechas)) < 0.6]:
            km = int(rng.normal(250, 40))
            litros = round(km / rng.normal(2.8, 0.4), 1)
            odometro += km
            terminal = str(rng.choice(list(planillas)))
            planillas[terminal].append({
                "NUMERO INTERNO": interno, "PATENTE": patente, "ODOMETRO": odometro,
                "LITROS": litros, "TERMINAL": terminal,
                "FOLIO": len(planillas[terminal]) + 1,
                "FECHA PLANILLA": fecha, "FECHA REAL": fecha, "ROL": "TRONCAL",
                "HORA": str(rng.choice(["630", "7:15", "22.40", "23:05:00"])),
                "BOMBERO": "OPERADOR", "TURNO": "DIA", "AD BLUE": 0,
            })
    for terminal, filas in planillas.items():
        nombre = terminal.replace(" ", "_") + ".xlsx"
        pd.DataFrame(filas).to_excel(os.path.join(main.DIR_CONSOLIDADOS, nombre),
                                     sheet_name="B.D", index=False)

if __name__ == "__main__":
    generar()
    print("[OK] Archivos de ejemplo creados en entrada_rangos/ y entrada_consolidados/")

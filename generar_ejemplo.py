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

import control_estanques
import main

# La norma viene escrita distinto en cada hoja ("Euro V" / "EURO V"), como en la planilla
# real: main.py tiene que normalizarla para encontrar el rango de cada bus.
BUSES = [("ABCD12", "101", "M1", "Euro V"), ("EFGH34", "102", "M1", "EURO VI"),
         ("IJKL56", "103", "M2", "Euro VI")]


def generar(seed=7):
    rng = np.random.default_rng(seed)
    main.crear_carpetas()

    detalle = pd.DataFrame(BUSES, columns=["PATENTE", "N INTERNO", "MODELO", "NORMA"])
    rango = pd.DataFrame({"MODELO": ["M1", "M1", "M2"], "NORMA": ["EURO V", "Euro VI", "EURO VI"],
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

    generar_estanques(planillas, rng)


def generar_estanques(planillas, rng):
    """Lecturas de pistolas y stock por terminal y dia, coherentes con las cargas de los buses.

    Las pistolas son contadores acumulativos: lo que despachan en un dia es exactamente lo
    que se cargo a los buses en ese terminal. Un turno queda sin lectura FINAL a proposito,
    para que control_estanques.py muestre el aviso.
    """
    os.makedirs(control_estanques.DIR_ESTANQUES, exist_ok=True)
    lecturas, recepciones = [], []
    for terminal, filas in planillas.items():
        cargas = pd.DataFrame(filas).groupby("FECHA REAL")["LITROS"].sum()
        p1, p2 = float(rng.integers(100_000, 200_000)), float(rng.integers(100_000, 200_000))
        adblue, stock = 500.0, 15_000.0
        for folio, (fecha, litros) in enumerate(cargas.items(), start=1):
            base = {"TERMINAL": terminal, "FECHA": fecha, "FOLIO": folio}
            lecturas.append({**base, "TIPO": "INICIAL", "PISTOLA 1": p1, "PISTOLA 2": p2,
                             "ADBLUE": adblue, "STOCK": stock})
            recibido = 8_000.0 if stock - litros < 4_000 else 0.0
            if recibido:
                recepciones.append({**base, "LITROS": recibido})
            reparto = rng.uniform(0.4, 0.6)
            p1, p2 = p1 + round(litros * reparto, 1), p2 + round(litros * (1 - reparto), 1)
            adblue += round(litros * 0.03, 1)
            # La medicion fisica difiere del teorico en unos pocos litros (regla, temperatura)
            stock = round(stock + recibido - litros + rng.normal(0, 15), 1)
            if not (terminal == "TERMINAL SUR" and folio == 3):
                lecturas.append({**base, "TIPO": "FINAL", "PISTOLA 1": p1, "PISTOLA 2": p2,
                                 "ADBLUE": adblue, "STOCK": stock})
    with pd.ExcelWriter(control_estanques.ARCHIVO_ESTANQUES) as w:
        pd.DataFrame(lecturas).to_excel(w, sheet_name="lecturas", index=False)
        pd.DataFrame(recepciones, columns=["TERMINAL", "FECHA", "FOLIO", "LITROS"]).to_excel(
            w, sheet_name="recepciones", index=False)

if __name__ == "__main__":
    generar()
    print("[OK] Archivos de ejemplo creados en entrada_rangos/, entrada_consolidados/ y entrada_estanques/")

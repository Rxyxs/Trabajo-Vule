import pandas as pd

import main


def _cargas(filas):
    base = {"TERMINAL": "T1", "FOLIO": 1, "FECHA PLANILLA": None, "ROL": "R",
            "BOMBERO": "B", "TURNO": "DIA", "AD BLUE": 0}
    df = pd.DataFrame([{**base, **f} for f in filas])
    df["FECHA PLANILLA"] = df["FECHA REAL"]
    return df


def _rangos():
    return pd.DataFrame([{"PATENTE": "ABCD12", "N INTERNO": "101", "MODELO": "M1",
                          "NORMA": "EURO6", "DESDE": 2.0, "HASTA": 4.0}])


def test_limpiar_hora():
    assert main.limpiar_hora("830") == "08:30"
    assert main.limpiar_hora("8:30") == "08:30"
    assert main.limpiar_hora("20.25") == "20:25"
    assert main.limpiar_hora("14:05:59") == "14:05"
    assert main.limpiar_hora(None) == ""


def test_kmacc_respeta_el_orden_cronologico_entre_meses():
    # Tres cargas del mismo bus en dic-2024 y ene-2025. Ordenadas como texto
    # dd-mm-aaaa, el 02-01-2025 quedaria antes que el 15-12-2024.
    df = _cargas([
        {"NUMERO INTERNO": 101, "PATENTE": "abcd12", "ODOMETRO": 1000, "LITROS": 100,
         "FECHA REAL": "2024-12-15", "HORA": "0800"},
        {"NUMERO INTERNO": 101, "PATENTE": "ABCD12", "ODOMETRO": 1300, "LITROS": 100,
         "FECHA REAL": "2024-12-28", "HORA": "0800"},
        {"NUMERO INTERNO": 101, "PATENTE": "ABCD12", "ODOMETRO": 1600, "LITROS": 100,
         "FECHA REAL": "2025-01-02", "HORA": "0800"},
    ])
    out = main.procesar_datos(df, _rangos())
    assert list(out["FECHA REAL"]) == ["15-12-2024", "28-12-2024", "02-01-2025"]
    assert list(out["KMACC"]) == [0, 300, 300]
    assert list(out["RENDIMIENTO"]) == [0.0, 3.0, 3.0]
    assert list(out["REV"]) == [0, 0, 0]  # la primera carga no tiene lectura anterior


def test_rev_marca_bajo_y_sobre_rango():
    df = _cargas([
        {"NUMERO INTERNO": 101, "PATENTE": "ABCD12", "ODOMETRO": 0, "LITROS": 100,
         "FECHA REAL": "2025-01-01", "HORA": "0800"},
        {"NUMERO INTERNO": 101, "PATENTE": "ABCD12", "ODOMETRO": 100, "LITROS": 100,
         "FECHA REAL": "2025-01-02", "HORA": "0800"},
        {"NUMERO INTERNO": 101, "PATENTE": "ABCD12", "ODOMETRO": 600, "LITROS": 100,
         "FECHA REAL": "2025-01-03", "HORA": "0800"},
    ])
    out = main.procesar_datos(df, _rangos())
    assert list(out["REV"]) == [0, "BR", "CI"]

import pandas as pd

import control_estanques as ce


def _lectura(terminal, fecha, folio, tipo, p1, p2, adblue, stock):
    return {"TERMINAL": terminal, "FECHA": fecha, "FOLIO": folio, "TIPO": tipo,
            "PISTOLA 1": p1, "PISTOLA 2": p2, "ADBLUE": adblue, "STOCK": stock}


def test_formulas_de_la_app():
    lecturas = pd.DataFrame([
        _lectura("NORTE", "2025-01-10", 1, "INICIAL", 1000, 5000, 200, 10000),
        _lectura("NORTE", "2025-01-10", 1, "FINAL", 1800, 5700, 230, 10480),
    ])
    recepciones = pd.DataFrame([{"TERMINAL": "NORTE", "FECHA": "2025-01-10", "FOLIO": 1, "LITROS": 2000}])
    pares, problemas = ce.emparejar_turnos(lecturas)
    t = ce.calcular_turnos(pares, recepciones).iloc[0]
    assert problemas.empty
    assert (t["TOTAL N 1"], t["TOTAL N 2"], t["TOTAL ADBLUE"]) == (800, 700, 30)
    assert t["STOCK TEORICO"] == 10000 + 2000 - 1500          # 10.500
    assert t["DIFERENCIA"] == -20                             # medido 10.480
    assert t["ALERTA"] == ""


def test_el_inicial_se_busca_por_terminal_fecha_y_folio():
    # Dos turnos el mismo dia en el mismo terminal. Las pistolas son acumulativas: el
    # segundo turno parte donde termino el primero.
    lecturas = pd.DataFrame([
        _lectura("NORTE", "2025-01-10", 1, "INICIAL", 1000, 0, 0, 9000),
        _lectura("NORTE", "2025-01-10", 1, "FINAL", 1800, 0, 0, 8200),
        _lectura("NORTE", "2025-01-10", 2, "INICIAL", 1800, 0, 0, 8200),
        _lectura("NORTE", "2025-01-10", 2, "FINAL", 2500, 0, 0, 7500),
    ])
    pares, _ = ce.emparejar_turnos(lecturas)
    t = ce.calcular_turnos(pares, pd.DataFrame(columns=["TERMINAL", "FECHA", "FOLIO", "LITROS"]))
    # Cada turno con su propio inicial: 800 y 700 litros. Si el turno 1 tomara el inicial
    # del turno 2 (1.800), su consumo daria 0; si el 2 tomara el final del 1, daria negativo.
    assert t["TOTAL N 1"].tolist() == [800, 700]
    assert (t["ALERTA"] == "").all()


def test_turnos_incompletos_o_duplicados_no_se_calculan():
    lecturas = pd.DataFrame([
        _lectura("SUR", "2025-01-10", 7, "INICIAL", 0, 0, 0, 0),             # sin FINAL
        _lectura("SUR", "2025-01-11", 8, "inicial ", 0, 0, 0, 0),            # dos INICIAL
        _lectura("SUR", "2025-01-11", 8, "INICIAL", 10, 0, 0, 0),
        _lectura("SUR", "2025-01-11", 8, "FINAL", 50, 0, 0, 0),
    ])
    pares, problemas = ce.emparejar_turnos(lecturas)
    assert pares.empty
    assert sorted(problemas["PROBLEMA"]) == ["2 lecturas INICIAL", "sin lectura FINAL", "sin lectura INICIAL"]


def test_alerta_consumos_negativos_e_imposibles():
    pares = pd.DataFrame([{
        "TERMINAL": "NORTE", "FECHA": pd.Timestamp("2025-01-10"), "FOLIO": 1,
        "PISTOLA 1 INICIAL": 5000, "PISTOLA 1 FINAL": 4000,       # negativo
        "PISTOLA 2 INICIAL": 0, "PISTOLA 2 FINAL": 90000,          # un digito de mas
        "ADBLUE INICIAL": 0, "ADBLUE FINAL": 5, "STOCK INICIAL": 0, "STOCK FINAL": 0,
    }])
    alerta = ce.calcular_turnos(pares, pd.DataFrame(columns=["TERMINAL", "FECHA", "FOLIO", "LITROS"]))["ALERTA"].iloc[0]
    assert "TOTAL N 1 negativo" in alerta and "imposible" in alerta

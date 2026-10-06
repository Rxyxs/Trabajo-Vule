import pandas as pd

import consolidar_planillas as cp


def _planilla(ruta, filas):
    """Escribe una planilla con el formato real: 15 filas de portada y el encabezado en la 16."""
    portada = pd.DataFrame([["PLANILLA DE CARGA"]] + [[None]] * 14)
    with pd.ExcelWriter(ruta) as w:
        portada.to_excel(w, sheet_name="Carga", header=False, index=False)
        pd.DataFrame(filas).to_excel(w, sheet_name="Carga", startrow=cp.FILA_ENCABEZADO, index=False)


def _carga(n, fecha, **extra):
    base = {"N°": n, "TERMINAL": "NORTE", "FOLIO": 1, "FECHA PLANILLA": fecha, "FECHA REAL": fecha,
            "NUMERO INTERNO": 101, "PATENTE": "ABCD12", "ROL": 1, "KILOMETROS": 1000 + n,
            "LITROS": 90.0, "HORA": "08:00", "BOMBERO": "X", "TURNO": "DIA", "AD BLUE": 0,
            "REJILLA": "OK", "TAPA": "OK"}
    return {**base, **extra}


def test_lee_la_hoja_real_y_deja_solo_las_columnas_del_consolidado(tmp_path):
    ruta = tmp_path / "NORTE - 23-12-2024.xlsx"
    filas = [_carga(1, "2024-12-23"), _carga(2, "2024-12-23")]
    filas.append({"N°": 3})  # fila con solo la numeracion: no es una carga
    _planilla(ruta, filas)
    df = cp.leer_planilla(ruta)
    assert len(df) == 2
    assert "ODOMETRO" in df.columns and "KILOMETROS" not in df.columns
    assert not {"N°", "REJILLA", "TAPA"} & set(df.columns)


def test_fecha_del_nombre():
    assert cp.fecha_del_nombre("TERMINAL SUR -23-12-2024.xlsm") == pd.Timestamp("2024-12-23")
    assert cp.fecha_del_nombre("planilla.xlsx") is None


def test_consolida_por_dia_del_archivo_y_avisa_el_mes_mal_digitado(tmp_path, capsys):
    entrada, salida = tmp_path / "planillas", tmp_path / "consolidados"
    entrada.mkdir()
    _planilla(entrada / "NORTE - 23-12-2024.xlsx", [_carga(1, "2024-12-23")])
    # Un terminal digito noviembre en vez de diciembre en toda su planilla
    _planilla(entrada / "SUR - 23-12-2024.xlsx", [_carga(1, "2024-11-23", TERMINAL="SUR"),
                                                  _carga(2, "2024-11-23", TERMINAL="SUR")])
    creados = cp.consolidar(str(entrada), str(salida))
    assert [p.split("\\")[-1].split("/")[-1] for p in creados] == ["2024-12-23.xlsx"]
    dia = pd.read_excel(creados[0], sheet_name="B.D")
    assert sorted(dia["TERMINAL"].unique()) == ["NORTE", "SUR"] and len(dia) == 3
    assert "SUR - 23-12-2024.xlsx" in capsys.readouterr().out


def test_una_planilla_sin_columnas_requeridas_se_omite(tmp_path, capsys):
    entrada = tmp_path / "planillas"
    entrada.mkdir()
    _planilla(entrada / "NORTE - 23-12-2024.xlsx", [{"TERMINAL": "NORTE", "FOLIO": 1, "PATENTE": "X"}])
    assert cp.consolidar(str(entrada), str(tmp_path / "out")) == []
    assert "omitido" in capsys.readouterr().out

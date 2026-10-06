"""El motor no inventa cuotas y no liquida Over a 1.0."""

import pandas as pd

from src.backtest.engine import BacktestEngine
from src.rules.base import Regla


def _regla(tipo):
    return Regla(
        nombre=f"siempre_{tipo}",
        descripcion="dispara siempre",
        condicion=lambda p: True,
        tipo_apuesta=tipo,
        confianza_esperada=0.5,
        activa=True,
    )


def test_over_usa_cuota_real_y_no_uno():
    df = pd.DataFrame([
        {
            'Date': '2024-01-01',
            'Local': 'A',
            'Visitante': 'B',
            'Resultado': 'H',
            'Goles_Local': 2,
            'Goles_Visitante': 1,
            'Total_Goles': 3,
            'Cuota_Over_25': 1.90,
        }
    ])
    resultado = BacktestEngine(df, [_regla('Over')]).ejecutar(verbose=False)
    r = resultado['siempre_Over']
    assert r['disparos'] == 1
    assert r['aciertos'] == 1
    assert r['ganancia_total'] == 0.90
    assert r['omitidos_sin_cuota'] == 0
    assert r['partidos'][0]['cuota'] == 1.90


def test_over_sin_cuota_no_entra_en_roi():
    df = pd.DataFrame([
        {
            'Date': '2024-01-01',
            'Local': 'A',
            'Visitante': 'B',
            'Resultado': 'H',
            'Goles_Local': 3,
            'Goles_Visitante': 1,
            'Total_Goles': 4,
        }
    ])
    resultado = BacktestEngine(df, [_regla('Over')]).ejecutar(verbose=False)
    r = resultado['siempre_Over']
    assert r['disparos'] == 0
    assert r['ganancia_total'] == 0.0
    assert r['omitidos_sin_cuota'] == 1


def test_cuota_uno_o_ausente_no_se_inventa():
    df = pd.DataFrame([
        {
            'Date': '2024-01-01',
            'Local': 'A',
            'Visitante': 'B',
            'Resultado': 'H',
            'Cuota_Local': 1.0,
        },
        {
            'Date': '2024-01-08',
            'Local': 'C',
            'Visitante': 'D',
            'Resultado': 'A',
            'Cuota_Local': None,
        },
    ])
    resultado = BacktestEngine(df, [_regla('Local')]).ejecutar(verbose=False)
    r = resultado['siempre_Local']
    assert r['disparos'] == 0
    assert r['omitidos_sin_cuota'] == 2


def test_local_pierde_resta_stake_con_cuota_real():
    df = pd.DataFrame([
        {
            'Date': '2024-02-01',
            'Local': 'A',
            'Visitante': 'B',
            'Resultado': 'A',
            'Cuota_Local': 1.45,
        }
    ])
    resultado = BacktestEngine(df, [_regla('Local')]).ejecutar(verbose=False)
    r = resultado['siempre_Local']
    assert r['disparos'] == 1
    assert r['aciertos'] == 0
    assert r['ganancia_total'] == -1.0
    assert r['partidos'][0]['cuota'] == 1.45

"""Rachas sin look-ahead y edge contra la cuota, no contra el 50 %."""

import pandas as pd

from src.backtest.engine import BacktestEngine
from src.backtest.validation import DataValidator
from src.data.feature_engineering import FeatureEngineer
from src.rules.base import Regla


def _liga_minima():
    return pd.DataFrame([
        {'Date': '2024-01-01', 'Local': 'A', 'Visitante': 'B', 'Resultado': 'H', 'Goles_Local': 1, 'Goles_Visitante': 0},
        {'Date': '2024-01-08', 'Local': 'A', 'Visitante': 'C', 'Resultado': 'A', 'Goles_Local': 0, 'Goles_Visitante': 2},
        {'Date': '2024-01-15', 'Local': 'B', 'Visitante': 'A', 'Resultado': 'A', 'Goles_Local': 0, 'Goles_Visitante': 1},
        {'Date': '2024-01-22', 'Local': 'A', 'Visitante': 'D', 'Resultado': 'H', 'Goles_Local': 2, 'Goles_Visitante': 1},
    ])


def test_derrotas_no_cuentan_el_partido_actual():
    df = FeatureEngineer().generar_todas_features(_liga_minima())
    ultimo = df[df['Date'] == '2024-01-22'].iloc[0]
    assert ultimo['Local_Derrotas_L3'] == 1
    assert ultimo['Local_Victorias_L3'] == 2
    assert ultimo['Local_Forma_L5'] == 6
    assert ultimo['Local_BTTS_L4'] == 0


def test_btts_historico_no_incluye_el_partido():
    df = pd.DataFrame([
        {'Date': '2024-01-01', 'Local': 'A', 'Visitante': 'B', 'Resultado': 'H', 'Goles_Local': 1, 'Goles_Visitante': 1},
        {'Date': '2024-01-08', 'Local': 'C', 'Visitante': 'A', 'Resultado': 'D', 'Goles_Local': 2, 'Goles_Visitante': 2},
        {'Date': '2024-01-15', 'Local': 'A', 'Visitante': 'D', 'Resultado': 'H', 'Goles_Local': 1, 'Goles_Visitante': 0},
    ])
    out = FeatureEngineer().generar_todas_features(df)
    ultimo = out.iloc[-1]
    assert ultimo['Local_BTTS_L4'] == 2
    assert ultimo['Local_Goles_Prom_L5'] == 1.5


def test_edge_no_sale_de_ganar_favoritos_al_azar_de_la_cuota():
    partidos = [{'acerto': True, 'cuota': 1.50} for _ in range(60)]
    partidos += [{'acerto': False, 'cuota': 1.50} for _ in range(40)]
    sig = DataValidator().validar_contra_cuota(partidos)
    assert sig['significativo'] is False
    assert sig['esperados'] > sig['aciertos']


def test_cartera_una_apuesta_por_partido():
    df = pd.DataFrame([
        {
            'Date': '2024-02-01', 'Local': 'A', 'Visitante': 'B', 'Resultado': 'H',
            'Cuota_Local': 1.40, 'Cuota_Visitante': 6.0,
        }
    ])
    # Edge local = 0.90*1.40-1 = 0.26. Edge visitante = 0.10*6-1 = -0.40.
    reglas = [
        Regla('local', 'l', lambda p: True, 'Local', 0.90, True),
        Regla('visitante', 'v', lambda p: True, 'Visitante', 0.10, True),
    ]
    cartera = BacktestEngine(df, reglas).ejecutar_cartera(verbose=False)
    assert cartera['disparos'] == 1
    assert cartera['partidos'][0]['regla'] == 'local'
    assert cartera['aciertos'] == 1

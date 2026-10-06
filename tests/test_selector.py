"""El selector no apuesta un favorito solo porque acierte mucho."""

from src.backtest.selector import edge, merece_apuesta, regla_apta


def test_favorito_corto_no_tiene_margen():
    # 78 % a cuota 1.25 es edge negativo: el mercado ya paga menos.
    assert edge(0.78, 1.25) < 0
    assert merece_apuesta(0.78, 1.25) is False


def test_margen_minimo_de_cuatro_puntos():
    assert merece_apuesta(0.55, 2.0) is True  # edge 0.10
    assert merece_apuesta(0.52, 2.0) is True  # edge 0.04 entra
    assert merece_apuesta(0.51, 2.0) is False


def test_regla_con_roi_negativo_queda_fuera():
    assert regla_apta({"disparos": 80, "roi": -0.05}) is False
    assert regla_apta({"disparos": 80, "roi": 0.02}) is True
    assert regla_apta({"disparos": 10, "roi": 0.20}) is False

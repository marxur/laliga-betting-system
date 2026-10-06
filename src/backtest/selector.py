"""Selección de apuestas con margen mínimo sobre la cuota.

El win rate de train no basta: a cuota 1.40 el mercado ya espera ~71 %.
Solo pasa una apuesta si la confianza de train supera 1/cuota en un margen.
"""

MARGEN_MINIMO = 0.04
MUESTRA_MINIMA = 40


def edge(confianza: float, cuota: float) -> float:
    return confianza * cuota - 1.0


def regla_apta(resultado_train: dict, minimo: int = MUESTRA_MINIMA) -> bool:
    if not resultado_train:
        return False
    if resultado_train.get("disparos", 0) < minimo:
        return False
    if resultado_train.get("roi", 0) <= 0:
        return False
    return True


def merece_apuesta(confianza: float, cuota: float, margen: float = MARGEN_MINIMO) -> bool:
    if cuota is None or cuota <= 1.0:
        return False
    return edge(confianza, cuota) >= margen

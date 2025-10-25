"""
Criterio de Kelly para gestión de bankroll
Responsabilidad: Calcular stakes óptimos
"""

from typing import Optional
import logging

from src.config import BACKTEST_CONFIG

logger = logging.getLogger(__name__)


def calcular_stake_kelly(
    probabilidad: float,
    cuota: float,
    bankroll: float,
    kelly_fraction: float = 0.25,
    max_stake_pct: float = 0.05
) -> float:
    """
    Calcula stake óptimo usando Kelly Criterion fraccionado
    
    Formula Kelly: f = (bp - q) / b
    donde:
        f = fracción del bankroll a apostar
        b = cuota - 1 (ganancia neta por unidad apostada)
        p = probabilidad de ganar
        q = probabilidad de perder (1 - p)
    
    Args:
        probabilidad: Probabilidad estimada de ganar (0-1)
        cuota: Cuota decimal de la apuesta
        bankroll: Bankroll actual
        kelly_fraction: Fracción de Kelly a usar (0.25 = conservador)
        max_stake_pct: Máximo % del bankroll por apuesta
    
    Returns:
        Stake en unidades monetarias
    """
    
    # Validar inputs
    if probabilidad <= 0 or probabilidad >= 1:
        logger.warning(f"Probabilidad inválida: {probabilidad}")
        return 0.0
    
    if cuota <= 1.0:
        logger.warning(f"Cuota inválida: {cuota}")
        return 0.0
    
    # Calcular edge (ventaja)
    edge = (probabilidad * cuota) - 1
    
    # Si no hay edge, no apostar
    if edge <= 0:
        return 0.0
    
    # Kelly completo
    kelly_full = edge / (cuota - 1)
    
    # Kelly fraccionado (conservador)
    kelly_frac = kelly_full * kelly_fraction
    
    # Aplicar límite máximo
    stake_pct = min(kelly_frac, max_stake_pct)
    
    # Convertir a unidades monetarias
    stake = bankroll * stake_pct
    
    return max(0.0, stake)


def calcular_probabilidad_implicita(cuota: float) -> float:
    """
    Calcula probabilidad implícita de una cuota
    
    Args:
        cuota: Cuota decimal
    
    Returns:
        Probabilidad implícita (0-1)
    """
    if cuota <= 1.0:
        return 0.0
    
    return 1.0 / cuota


def calcular_edge(probabilidad_real: float, cuota: float) -> float:
    """
    Calcula edge (ventaja) de una apuesta
    
    Args:
        probabilidad_real: Probabilidad estimada real
        cuota: Cuota ofrecida
    
    Returns:
        Edge (valor esperado - 1)
    """
    return (probabilidad_real * cuota) - 1


def recomendar_stake(
    confianza: float,
    cuota: float,
    bankroll: float,
    config=BACKTEST_CONFIG
) -> dict:
    """
    Recomienda stake basado en confianza de la regla
    
    Args:
        confianza: Confianza de la regla (win rate esperado)
        cuota: Cuota del partido
        bankroll: Bankroll actual
        config: Configuración de backtest
    
    Returns:
        Dict con recomendación de stake
    """
    
    # Calcular stake Kelly
    stake = calcular_stake_kelly(
        probabilidad=confianza,
        cuota=cuota,
        bankroll=bankroll,
        kelly_fraction=config.kelly_fraction,
        max_stake_pct=config.max_stake
    )
    
    # Calcular métricas adicionales
    prob_implicita = calcular_probabilidad_implicita(cuota)
    edge = calcular_edge(confianza, cuota)
    
    return {
        'stake': stake,
        'stake_pct': stake / bankroll if bankroll > 0 else 0,
        'edge': edge,
        'prob_implicita': prob_implicita,
        'valor': confianza > prob_implicita  # True si hay value
    }


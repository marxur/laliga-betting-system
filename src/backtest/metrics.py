"""
Cálculo de métricas de rendimiento
"""

from typing import Dict, Any
import numpy as np


def calcular_metricas(
    aciertos: int,
    disparos: int,
    ganancia_total: float,
    stake_total: float
) -> Dict[str, Any]:
    """
    Calcula todas las métricas de rendimiento
    
    Args:
        aciertos: Número de apuestas acertadas
        disparos: Número total de apuestas
        ganancia_total: Ganancia/pérdida neta
        stake_total: Total apostado
    
    Returns:
        Dict con todas las métricas
    """
    
    if disparos == 0:
        return {
            'aciertos': 0,
            'disparos': 0,
            'win_rate': 0.0,
            'roi': 0.0,
            'ganancia_total': 0.0,
            'stake_total': 0.0,
            'profit_factor': 0.0
        }
    
    win_rate = aciertos / disparos
    roi = ganancia_total / stake_total if stake_total > 0 else 0.0
    
    # Profit Factor = Ganancias / Pérdidas
    # (Simplificado, versión completa requiere tracking separado)
    profit_factor = (ganancia_total + stake_total) / stake_total if stake_total > 0 else 0.0
    
    return {
        'aciertos': aciertos,
        'disparos': disparos,
        'win_rate': win_rate,
        'roi': roi,
        'ganancia_total': ganancia_total,
        'stake_total': stake_total,
        'profit_factor': profit_factor
    }


def calcular_sharpe_ratio(returns: list, risk_free_rate: float = 0.0) -> float:
    """
    Calcula Sharpe Ratio (retorno ajustado por riesgo)
    
    Args:
        returns: Lista de retornos por apuesta
        risk_free_rate: Tasa libre de riesgo
    
    Returns:
        Sharpe Ratio
    """
    if len(returns) == 0:
        return 0.0
    
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0.0
    
    return (mean_return - risk_free_rate) / std_return


def calcular_max_drawdown(cumulative_returns: list) -> float:
    """
    Calcula máxima caída desde pico
    
    Args:
        cumulative_returns: Lista de retornos acumulados
    
    Returns:
        Max Drawdown (valor positivo)
    """
    if len(cumulative_returns) == 0:
        return 0.0
    
    peak = cumulative_returns[0]
    max_dd = 0.0
    
    for value in cumulative_returns:
        if value > peak:
            peak = value
        dd = (peak - value) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
    
    return max_dd


"""
Motor de backtesting.
Liquida solo con cuota real. La cartera no apuesta dos veces el mismo partido.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import logging
import math

from src.rules.base import Regla
from src.backtest.metrics import calcular_metricas
from src.backtest.selector import merece_apuesta, edge as calcular_edge
from src.config import BACKTEST_CONFIG

logger = logging.getLogger(__name__)

CUOTAS_POR_MERCADO = {
    'Local': ['Cuota_Local', 'B365H'],
    'Visitante': ['Cuota_Visitante', 'B365A'],
    'Empate': ['Cuota_Empate', 'B365D'],
    'BTTS': ['Cuota_BTTS', 'B365BTTS', 'AvgBTTS'],
    'Over': [
        'Cuota_Over_25', 'Cuota_Over', 'B365>2.5', 'Avg>2.5',
        'BbAv>2.5', 'Max>2.5', 'P>2.5', 'PC>2.5',
    ],
    'Under': [
        'Cuota_Under_25', 'Cuota_Under', 'B365<2.5', 'Avg<2.5',
        'BbAv<2.5', 'Max<2.5', 'P<2.5', 'PC<2.5',
    ],
}


def _cuota_valida(valor) -> Optional[float]:
    if valor is None or isinstance(valor, bool):
        return None
    try:
        if pd.isna(valor):
            return None
        cuota = float(valor)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(cuota) or cuota <= 1.0:
        return None
    return cuota


def _max_drawdown(ganancias: List[float]) -> float:
    equity = 0.0
    pico = 0.0
    peor = 0.0
    for ganancia in ganancias:
        equity += ganancia
        pico = max(pico, equity)
        peor = max(peor, pico - equity)
    return peor


class BacktestEngine:
    """Motor de backtesting. Liquida solo apuestas con cuota real."""

    def __init__(self, df: pd.DataFrame, reglas: List[Regla], config=BACKTEST_CONFIG):
        self.df = df.copy()
        if 'Date' in self.df.columns:
            self.df = self.df.sort_values('Date')
        self.reglas = [r for r in reglas if r.activa]
        self.config = config
        self.resultados = {}

    def ejecutar(self, verbose: bool = True) -> Dict[str, Dict[str, Any]]:
        if verbose:
            logger.info("EJECUTANDO BACKTEST")
        for regla in self.reglas:
            resultado = self._testear_regla(regla)
            self.resultados[regla.nombre] = resultado
            if verbose:
                self._mostrar_resultado(regla, resultado)
        return self.resultados

    def ejecutar_cartera(self, verbose: bool = True) -> Dict[str, Any]:
        """Como mucho una apuesta por partido, y solo con margen de edge."""
        aciertos = 0
        disparos = 0
        omitidos = 0
        stake_total = 0.0
        ganancia_total = 0.0
        partidos = []

        for idx, partido in self.df.iterrows():
            candidatas = []
            for regla in self.reglas:
                if not regla.evaluar(partido):
                    continue
                cuota = self._obtener_cuota(partido, regla.tipo_apuesta)
                if cuota is None or not merece_apuesta(regla.confianza_esperada, cuota):
                    omitidos += 1
                    continue
                edge = calcular_edge(regla.confianza_esperada, cuota)
                candidatas.append((edge, regla, cuota))

            if not candidatas:
                continue
            candidatas.sort(key=lambda item: item[0], reverse=True)
            edge, regla, cuota = candidatas[0]
            disparos += 1
            stake = 1.0
            stake_total += stake
            acerto = self._verificar_acierto(partido, regla.tipo_apuesta)
            ganancia = stake * (cuota - 1.0) if acerto else -stake
            if acerto:
                aciertos += 1
            ganancia_total += ganancia
            partidos.append({
                'fecha': partido.get('Date'),
                'local': partido.get('Local'),
                'visitante': partido.get('Visitante'),
                'regla': regla.nombre,
                'tipo': regla.tipo_apuesta,
                'acerto': acerto,
                'cuota': cuota,
                'edge_declarado': edge,
                'ganancia': ganancia,
                'partido_id': idx,
            })

        metricas = calcular_metricas(aciertos, disparos, ganancia_total, stake_total)
        metricas['omitidos_sin_cuota'] = omitidos
        metricas['max_drawdown'] = _max_drawdown([p['ganancia'] for p in partidos])
        metricas['partidos'] = partidos
        if verbose:
            logger.info(
                f"Cartera: {aciertos}/{disparos} ROI={metricas['roi']:.1%} "
                f"drawdown={metricas['max_drawdown']:.2f}u omitidos={omitidos}"
            )
        return metricas

    def _testear_regla(self, regla: Regla) -> Dict[str, Any]:
        aciertos = 0
        disparos = 0
        omitidos = 0
        stake_total = 0.0
        ganancia_total = 0.0
        partidos_disparados = []
        partidos_omitidos = []

        for _, partido in self.df.iterrows():
            if not regla.evaluar(partido):
                continue
            cuota = self._obtener_cuota(partido, regla.tipo_apuesta)
            ident = {
                'fecha': partido.get('Date'),
                'local': partido.get('Local'),
                'visitante': partido.get('Visitante'),
                'tipo': regla.tipo_apuesta,
            }
            if cuota is None:
                omitidos += 1
                partidos_omitidos.append({**ident, 'motivo': 'sin_cuota'})
                continue
            disparos += 1
            stake = 1.0
            stake_total += stake
            acerto = self._verificar_acierto(partido, regla.tipo_apuesta)
            ganancia = stake * (cuota - 1.0) if acerto else -stake
            if acerto:
                aciertos += 1
            ganancia_total += ganancia
            partidos_disparados.append({**ident, 'acerto': acerto, 'cuota': cuota, 'stake': stake, 'ganancia': ganancia})

        metricas = calcular_metricas(aciertos, disparos, ganancia_total, stake_total)
        metricas['omitidos_sin_cuota'] = omitidos
        metricas['max_drawdown'] = _max_drawdown([p['ganancia'] for p in partidos_disparados])
        metricas['partidos'] = partidos_disparados
        metricas['partidos_omitidos'] = partidos_omitidos
        return metricas

    def _verificar_acierto(self, partido: pd.Series, tipo_apuesta: str) -> bool:
        resultado = partido.get('Resultado')
        if tipo_apuesta == 'Local':
            return resultado == 'H'
        if tipo_apuesta == 'Visitante':
            return resultado == 'A'
        if tipo_apuesta == 'Empate':
            return resultado == 'D'
        if tipo_apuesta == 'BTTS':
            if 'BTTS' in partido.index and pd.notna(partido.get('BTTS')):
                return bool(partido.get('BTTS'))
            goles_local = partido.get('Goles_Local')
            goles_visitante = partido.get('Goles_Visitante')
            if pd.isna(goles_local) or pd.isna(goles_visitante):
                return False
            return float(goles_local) > 0 and float(goles_visitante) > 0
        if tipo_apuesta in ('Over', 'Under'):
            total = partido.get('Total_Goles')
            if total is None or pd.isna(total):
                goles_local = partido.get('Goles_Local')
                goles_visitante = partido.get('Goles_Visitante')
                if pd.isna(goles_local) or pd.isna(goles_visitante):
                    return False
                total = float(goles_local) + float(goles_visitante)
            total = float(total)
            return total > 2.5 if tipo_apuesta == 'Over' else total < 2.5
        return False

    def _obtener_cuota(self, partido: pd.Series, tipo_apuesta: str) -> Optional[float]:
        for columna in CUOTAS_POR_MERCADO.get(tipo_apuesta, []):
            if columna not in partido.index:
                continue
            cuota = _cuota_valida(partido.get(columna))
            if cuota is not None:
                return cuota
        return None

    def _mostrar_resultado(self, regla: Regla, resultado: Dict[str, Any]):
        disparos = resultado['disparos']
        omitidos = resultado.get('omitidos_sin_cuota', 0)
        if disparos == 0:
            logger.info(f"{regla.nombre}: sin disparos liquidables (omitidos={omitidos})")
            return
        logger.info(
            f"{regla.nombre}: {resultado['aciertos']}/{disparos} "
            f"({resultado['win_rate']:.1%}) ROI={resultado['roi']:.1%} "
            f"DD={resultado['max_drawdown']:.2f}u omitidos={omitidos}"
        )

    def ejecutar_periodicamente(self, intervalo_horas: int = 24):
        import time
        while True:
            self.ejecutar(verbose=True)
            time.sleep(intervalo_horas * 3600)

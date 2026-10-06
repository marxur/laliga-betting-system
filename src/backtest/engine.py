"""
Motor principal de backtesting
Responsabilidad: Ejecutar reglas contra datos históricos y liquidarlas
con la cuota real del mercado. Sin cuota válida no hay apuesta.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import logging
import math

from src.rules.base import Regla
from src.backtest.metrics import calcular_metricas
from src.config import BACKTEST_CONFIG

logger = logging.getLogger(__name__)

# Columnas candidatas, de más específica a respaldo. La primera cuota
# decimal > 1 gana. No hay cuotas por defecto.
CUOTAS_POR_MERCADO = {
    'Local': ['Cuota_Local', 'B365H'],
    'Visitante': ['Cuota_Visitante', 'B365A'],
    'Empate': ['Cuota_Empate', 'B365D'],
    'BTTS': ['Cuota_BTTS', 'B365BTTS', 'AvgBTTS'],
    'Over': [
        'Cuota_Over_25',
        'Cuota_Over',
        'B365>2.5',
        'Avg>2.5',
        'BbAv>2.5',
        'Max>2.5',
        'P>2.5',
        'PC>2.5',
    ],
    'Under': [
        'Cuota_Under_25',
        'Cuota_Under',
        'B365<2.5',
        'Avg<2.5',
        'BbAv<2.5',
        'Max<2.5',
        'P<2.5',
        'PC<2.5',
    ],
}


def _cuota_valida(valor) -> Optional[float]:
    """Devuelve la cuota si es un decimal apostable; si no, None."""
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


class BacktestEngine:
    """Motor de backtesting. Liquida solo apuestas con cuota real."""

    def __init__(self, df: pd.DataFrame, reglas: List[Regla], config=BACKTEST_CONFIG):
        self.df = df.copy()
        if 'Date' in self.df.columns:
            self.df = self.df.sort_values('Date')
        self.reglas = reglas
        self.config = config
        self.resultados = {}

    def ejecutar(self, verbose: bool = True) -> Dict[str, Dict[str, Any]]:
        """Ejecuta el backtest de todas las reglas."""
        if verbose:
            logger.info("\n" + "=" * 70)
            logger.info("EJECUTANDO BACKTEST")
            logger.info("=" * 70 + "\n")

        for regla in self.reglas:
            resultado = self._testear_regla(regla)
            self.resultados[regla.nombre] = resultado
            if verbose:
                self._mostrar_resultado(regla, resultado)

        return self.resultados

    def _testear_regla(self, regla: Regla) -> Dict[str, Any]:
        """Testea una regla. Un disparo sin cuota no entra en las métricas."""
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

            if acerto:
                aciertos += 1
                ganancia = stake * (cuota - 1.0)
                ganancia_total += ganancia
            else:
                ganancia = -stake
                ganancia_total += ganancia

            partidos_disparados.append({
                **ident,
                'acerto': acerto,
                'cuota': cuota,
                'stake': stake,
                'ganancia': ganancia,
            })

        metricas = calcular_metricas(
            aciertos=aciertos,
            disparos=disparos,
            ganancia_total=ganancia_total,
            stake_total=stake_total,
        )
        metricas['omitidos_sin_cuota'] = omitidos
        metricas['partidos'] = partidos_disparados
        metricas['partidos_omitidos'] = partidos_omitidos
        return metricas

    def _verificar_acierto(self, partido: pd.Series, tipo_apuesta: str) -> bool:
        """Verifica el resultado del mercado. Over/Under son a 2.5 goles."""
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
            if total is None or (not isinstance(total, str) and pd.isna(total)):
                goles_local = partido.get('Goles_Local')
                goles_visitante = partido.get('Goles_Visitante')
                if pd.isna(goles_local) or pd.isna(goles_visitante):
                    return False
                total = float(goles_local) + float(goles_visitante)
            total = float(total)
            if tipo_apuesta == 'Over':
                return total > 2.5
            return total < 2.5

        return False

    def _obtener_cuota(self, partido: pd.Series, tipo_apuesta: str) -> Optional[float]:
        """Cuota decimal real del mercado. None si no hay cuota apostable."""
        for columna in CUOTAS_POR_MERCADO.get(tipo_apuesta, []):
            if columna not in partido.index:
                continue
            cuota = _cuota_valida(partido.get(columna))
            if cuota is not None:
                return cuota
        return None

    def _mostrar_resultado(self, regla: Regla, resultado: Dict[str, Any]):
        """Muestra el resultado de una regla."""
        disparos = resultado['disparos']
        omitidos = resultado.get('omitidos_sin_cuota', 0)
        win_rate = resultado['win_rate']
        roi = resultado['roi']

        if disparos == 0:
            logger.info(
                f"{regla.nombre}: sin disparos liquidables "
                f"(omitidos sin cuota: {omitidos})"
            )
            return

        if win_rate >= 0.70 and roi > 0:
            marca = "OK"
        elif win_rate >= 0.55 and roi > 0:
            marca = "REV"
        else:
            marca = "NO"

        logger.info(
            f"[{marca}] {regla.nombre}: "
            f"{resultado['aciertos']}/{disparos} "
            f"({win_rate:.1%}) | ROI: {roi:.1%} | "
            f"omitidos sin cuota: {omitidos}"
        )

    def ejecutar_periodicamente(self, intervalo_horas: int = 24):
        """Ejecuta el backtest en bucle. Pensado para un proceso de monitoreo."""
        import time

        while True:
            logger.info("Ejecutando backtest periódico...")
            self.ejecutar(verbose=True)
            logger.info(f"Esperando {intervalo_horas}h hasta la próxima ejecución...")
            time.sleep(intervalo_horas * 3600)

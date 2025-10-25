"""
Motor principal de backtesting
Responsabilidad: Ejecutar reglas contra datos históricos
"""

import pandas as pd
from typing import List, Dict, Any
import logging

from src.rules.base import Regla
from src.backtest.metrics import calcular_metricas
from src.config import BACKTEST_CONFIG

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Motor de backtesting robusto"""
    
    def __init__(self, df: pd.DataFrame, reglas: List[Regla], config=BACKTEST_CONFIG):
        self.df = df.copy()
        self.reglas = reglas
        self.config = config
        self.resultados = {}
    
    def ejecutar(self, verbose: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Ejecuta backtest completo de todas las reglas
        
        Args:
            verbose: Si mostrar progreso en consola
        
        Returns:
            Dict con resultados por regla
        """
        
        if verbose:
            logger.info("\n" + "="*70)
            logger.info("📊 EJECUTANDO BACKTEST")
            logger.info("="*70 + "\n")
        
        for regla in self.reglas:
            resultado = self._testear_regla(regla)
            self.resultados[regla.nombre] = resultado
            
            if verbose:
                self._mostrar_resultado(regla, resultado)
        
        return self.resultados
    
    def _testear_regla(self, regla: Regla) -> Dict[str, Any]:
        """
        Testea una regla individual contra el dataset
        
        Returns:
            Dict con métricas de rendimiento
        """
        
        aciertos = 0
        disparos = 0
        stake_total = 0.0
        ganancia_total = 0.0
        partidos_disparados = []
        
        for idx, partido in self.df.iterrows():
            # Evaluar si la regla dispara
            if regla.evaluar(partido):
                disparos += 1
                stake = 1.0  # Apuesta unitaria
                stake_total += stake
                
                # Verificar resultado
                acerto = self._verificar_acierto(partido, regla.tipo_apuesta)
                cuota = self._obtener_cuota(partido, regla.tipo_apuesta)
                
                if acerto:
                    aciertos += 1
                    ganancia = stake * (cuota - 1)
                    ganancia_total += ganancia
                else:
                    ganancia_total -= stake
                
                # Guardar info del partido
                partidos_disparados.append({
                    'fecha': partido['Date'],
                    'local': partido['Local'],
                    'visitante': partido['Visitante'],
                    'acerto': acerto,
                    'cuota': cuota
                })
        
        # Calcular métricas
        metricas = calcular_metricas(
            aciertos=aciertos,
            disparos=disparos,
            ganancia_total=ganancia_total,
            stake_total=stake_total
        )
        
        metricas['partidos'] = partidos_disparados
        
        return metricas
    
    def _verificar_acierto(self, partido: pd.Series, tipo_apuesta: str) -> bool:
        """Verifica si la apuesta fue correcta"""
        resultado = partido['Resultado']
        
        if tipo_apuesta == 'Local':
            return resultado == 'H'
        elif tipo_apuesta == 'Visitante':
            return resultado == 'A'
        elif tipo_apuesta == 'Empate':
            return resultado == 'D'
        elif tipo_apuesta == 'BTTS':
            return partido.get('BTTS', False)
        elif tipo_apuesta == 'Over':
            return partido.get('Total_Goles', 0) > 2.5
        elif tipo_apuesta == 'Under':
            return partido.get('Total_Goles', 0) < 2.5
        
        return False
    
    def _obtener_cuota(self, partido: pd.Series, tipo_apuesta: str) -> float:
        """Obtiene cuota del partido según tipo de apuesta"""
        if tipo_apuesta == 'Local':
            return partido.get('Cuota_Local', 1.5)
        elif tipo_apuesta == 'Visitante':
            return partido.get('Cuota_Visitante', 2.5)
        elif tipo_apuesta == 'Empate':
            return partido.get('Cuota_Empate', 3.0)
        elif tipo_apuesta == 'BTTS':
            return partido.get('Cuota_BTTS', 1.8)
        
        return 1.0
    
    def _mostrar_resultado(self, regla: Regla, resultado: Dict[str, Any]):
        """Muestra resultado de una regla en consola"""
        disparos = resultado['disparos']
        win_rate = resultado['win_rate']
        roi = resultado['roi']
        
        if disparos == 0:
            logger.info(f"⚪ {regla.nombre}: Sin disparos")
            return
        
        # Determinar emoji según rendimiento
        if win_rate >= 0.70 and roi > 0:
            emoji = "🟢"
        elif win_rate >= 0.55 and roi > 0:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        logger.info(
            f"{emoji} {regla.nombre}: "
            f"{resultado['aciertos']}/{disparos} "
            f"({win_rate:.1%}) | "
            f"ROI: {roi:.1%}"
        )
    
    def ejecutar_periodicamente(self, intervalo_horas: int = 24):
        """
        Ejecuta backtest periódicamente (para monitoreo)
        
        Args:
            intervalo_horas: Horas entre ejecuciones
        """
        import time
        
        while True:
            logger.info(f"\n⏰ Ejecutando backtest periódico...")
            self.ejecutar(verbose=True)
            
            logger.info(f"\n💤 Esperando {intervalo_horas}h hasta próxima ejecución...")
            time.sleep(intervalo_horas * 3600)


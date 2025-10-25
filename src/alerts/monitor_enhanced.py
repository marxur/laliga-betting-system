"""
Monitor mejorado que combina reglas originales y personalizadas
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.rules.laliga_rules import crear_reglas_laliga
from src.rules.custom_rules import crear_reglas_personalizadas
from src.data.unified_api import UnifiedAPIClient
from src.alerts.email_alert import EmailAlert
from src.risk.kelly import KellyCalculator
from src.config import ALERT_CONFIG

logger = logging.getLogger(__name__)


class EnhancedMonitor:
    """
    Monitor mejorado con reglas originales y personalizadas
    """
    
    def __init__(self):
        # Reglas originales (pre-partido)
        self.reglas_pre_partido = crear_reglas_laliga()
        
        # Reglas personalizadas (medio tiempo)
        self.reglas_medio_tiempo = crear_reglas_personalizadas()
        
        # Filtrar solo reglas rentables
        self.reglas_pre_partido_activas = [
            r for r in self.reglas_pre_partido
            if r.nombre in [
                'Local_Invicto_Favorito',
                'Favorito_Local_Forma',
                'Visitante_Invicto'
            ]
        ]
        
        self.reglas_medio_tiempo_activas = [
            r for r in self.reglas_medio_tiempo
            if r.nombre in [
                'Ganando_1-0_HT_No_Pierde',
                'Over25_Si_2Goles_HT',
                'Favorito_Mantiene_Ventaja',
                'Under25_Si_0-0_HT'
            ]
        ]
        
        self.api_client = UnifiedAPIClient()
        self.email_alert = EmailAlert()
        self.kelly_calc = KellyCalculator()
        
        logger.info(f"Monitor inicializado:")
        logger.info(f"  - Reglas pre-partido: {len(self.reglas_pre_partido_activas)}")
        logger.info(f"  - Reglas medio tiempo: {len(self.reglas_medio_tiempo_activas)}")
    
    def evaluar_proximos_partidos(self, dias: int = 7) -> List[Dict[str, Any]]:
        """
        Evalúa próximos partidos con reglas pre-partido
        
        Args:
            dias: Días hacia adelante para buscar partidos
        
        Returns:
            Lista de alertas generadas
        """
        logger.info(f"Evaluando próximos partidos ({dias} días)...")
        
        try:
            # Obtener próximos partidos
            partidos = self.api_client.get_proximos_partidos(dias=dias)
            
            if not partidos:
                logger.info("No hay próximos partidos programados")
                return []
            
            logger.info(f"Partidos obtenidos: {len(partidos)}")
            
            alertas = []
            
            for partido in partidos:
                # Evaluar contra reglas pre-partido
                for regla in self.reglas_pre_partido_activas:
                    if regla.evaluar(partido):
                        # Obtener cuota
                        cuota = self._obtener_cuota_pre_partido(regla, partido)
                        
                        # Calcular stake
                        win_rate = self._obtener_win_rate_pre_partido(regla.nombre)
                        stake = self.kelly_calc.calcular_stake(win_rate, cuota)
                        
                        alerta = {
                            'partido': {
                                'local': partido.get('local', ''),
                                'visitante': partido.get('visitante', ''),
                                'fecha': partido.get('fecha', ''),
                                'estadio': partido.get('estadio', '')
                            },
                            'regla': regla.nombre,
                            'descripcion': regla.descripcion,
                            'tipo_apuesta': regla.tipo_apuesta,
                            'cuota': cuota,
                            'confianza': win_rate,
                            'stake': stake,
                            'roi_historico': self._obtener_roi_pre_partido(regla.nombre),
                            'momento': 'pre-partido'
                        }
                        
                        alertas.append(alerta)
                        logger.info(f"Alerta pre-partido: {regla.nombre} para {partido.get('local')} vs {partido.get('visitante')}")
            
            # Enviar alertas si hay
            if alertas:
                self._enviar_alertas_agrupadas(alertas, "Pre-Partido")
            
            return alertas
        
        except Exception as e:
            logger.error(f"Error evaluando próximos partidos: {e}")
            return []
    
    def evaluar_partido_medio_tiempo(self, partido: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evalúa un partido en medio tiempo con reglas personalizadas
        
        Args:
            partido: Datos del partido al medio tiempo
        
        Returns:
            Lista de alertas generadas
        """
        alertas = []
        
        for regla in self.reglas_medio_tiempo_activas:
            # Preparar datos
            p_dict = {
                'Local': partido.get('local', ''),
                'Visitante': partido.get('visitante', ''),
                'HT_Home': partido.get('ht_home', 0),
                'HT_Away': partido.get('ht_away', 0),
                'Cuota_Local': partido.get('cuota_local', 999),
                'Cuota_Empate': partido.get('cuota_empate', 999),
                'Cuota_Visitante': partido.get('cuota_visitante', 999)
            }
            
            if regla.evaluar(p_dict):
                cuota = self._obtener_cuota_medio_tiempo(regla.tipo_apuesta, p_dict)
                win_rate = self._obtener_win_rate_medio_tiempo(regla.nombre)
                stake = self.kelly_calc.calcular_stake(win_rate, cuota)
                
                alerta = {
                    'partido': {
                        'local': partido.get('local', ''),
                        'visitante': partido.get('visitante', ''),
                        'ht_score': f"{partido.get('ht_home', 0)}-{partido.get('ht_away', 0)}",
                        'fecha': partido.get('fecha', datetime.now())
                    },
                    'regla': regla.nombre,
                    'descripcion': regla.descripcion,
                    'tipo_apuesta': regla.tipo_apuesta,
                    'cuota': cuota,
                    'confianza': win_rate,
                    'stake': stake,
                    'roi_historico': self._obtener_roi_medio_tiempo(regla.nombre),
                    'momento': 'medio-tiempo'
                }
                
                alertas.append(alerta)
        
        return alertas
    
    def _obtener_cuota_pre_partido(self, regla, partido: Dict[str, Any]) -> float:
        """Obtiene cuota para reglas pre-partido"""
        if regla.tipo_apuesta == "Local":
            return partido.get('cuota_local', 1.90)
        elif regla.tipo_apuesta == "Visitante":
            return partido.get('cuota_visitante', 1.90)
        return 1.90
    
    def _obtener_cuota_medio_tiempo(self, tipo_apuesta: str, partido: Dict[str, Any]) -> float:
        """Obtiene cuota para reglas de medio tiempo"""
        if tipo_apuesta == "Favorito":
            return min(partido.get('Cuota_Local', 999), partido.get('Cuota_Visitante', 999))
        elif tipo_apuesta == "Doble Chance (ganador HT)":
            return 1.20
        elif tipo_apuesta in ["Under 2.5", "Over 2.5"]:
            return 1.90
        elif tipo_apuesta == "Gol en 2H":
            return 1.50
        return 1.90
    
    def _obtener_win_rate_pre_partido(self, nombre_regla: str) -> float:
        """Win rates de reglas pre-partido"""
        win_rates = {
            'Local_Invicto_Favorito': 0.807,
            'Favorito_Local_Forma': 0.789,
            'Visitante_Invicto': 0.569
        }
        return win_rates.get(nombre_regla, 0.65)
    
    def _obtener_win_rate_medio_tiempo(self, nombre_regla: str) -> float:
        """Win rates de reglas de medio tiempo"""
        win_rates = {
            'Ganando_1-0_HT_No_Pierde': 0.90,
            'Over25_Si_2Goles_HT': 0.858,
            'Favorito_Mantiene_Ventaja': 0.849,
            'Under25_Si_0-0_HT': 0.825
        }
        return win_rates.get(nombre_regla, 0.75)
    
    def _obtener_roi_pre_partido(self, nombre_regla: str) -> float:
        """ROI de reglas pre-partido"""
        rois = {
            'Local_Invicto_Favorito': 5.1,
            'Favorito_Local_Forma': 7.8,
            'Visitante_Invicto': 13.4
        }
        return rois.get(nombre_regla, 0.0)
    
    def _obtener_roi_medio_tiempo(self, nombre_regla: str) -> float:
        """ROI de reglas de medio tiempo"""
        rois = {
            'Ganando_1-0_HT_No_Pierde': 71.0,
            'Over25_Si_2Goles_HT': 63.0,
            'Favorito_Mantiene_Ventaja': 61.4,
            'Under25_Si_0-0_HT': 56.7
        }
        return rois.get(nombre_regla, 0.0)
    
    def _enviar_alertas_agrupadas(self, alertas: List[Dict[str, Any]], tipo: str):
        """Envía alertas agrupadas por email"""
        try:
            for alerta in alertas:
                self.email_alert.enviar_alerta(alerta)
            logger.info(f"Emails enviados: {len(alertas)} alertas de {tipo}")
        except Exception as e:
            logger.error(f"Error enviando emails: {e}")
    
    def ejecutar_revision_completa(self):
        """
        Ejecuta una revisión completa:
        1. Evalúa próximos partidos (pre-partido)
        2. Retorna alertas generadas
        """
        logger.info("="*70)
        logger.info("🎯 REVISIÓN COMPLETA DEL SISTEMA")
        logger.info("="*70)
        
        # Evaluar próximos partidos
        alertas_pre = self.evaluar_proximos_partidos(dias=7)
        
        logger.info(f"\n📊 Resumen:")
        logger.info(f"  - Alertas pre-partido: {len(alertas_pre)}")
        
        logger.info("\n" + "="*70)
        logger.info("✅ REVISIÓN COMPLETADA")
        logger.info("="*70 + "\n")
        
        return {
            'pre_partido': alertas_pre,
            'total': len(alertas_pre)
        }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    monitor = EnhancedMonitor()
    monitor.ejecutar_revision_completa()


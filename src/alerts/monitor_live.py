"""
Monitor de alertas en vivo para estrategias de medio tiempo
Requiere datos en tiempo real con resultados de medio tiempo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.rules.custom_rules import crear_reglas_personalizadas
from src.alerts.email_alert import EmailAlert
from src.config import ALERT_CONFIG

logger = logging.getLogger(__name__)


class LiveMonitor:
    """
    Monitor de alertas en vivo para estrategias de medio tiempo
    """
    
    def __init__(self):
        self.reglas = crear_reglas_personalizadas()
        self.email_alert = EmailAlert()
        
        # Filtrar solo las mejores reglas (ROI > 55%)
        self.reglas_activas = [
            r for r in self.reglas 
            if r.nombre in [
                'Ganando_1-0_HT_No_Pierde',
                'Over25_Si_2Goles_HT',
                'Favorito_Mantiene_Ventaja',
                'Under25_Si_0-0_HT'
            ]
        ]
        
        logger.info(f"Monitor inicializado con {len(self.reglas_activas)} reglas activas")
    
    def evaluar_partido_medio_tiempo(self, partido: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evalúa un partido en medio tiempo contra las reglas
        
        Args:
            partido: Diccionario con datos del partido al medio tiempo
                {
                    'local': str,
                    'visitante': str,
                    'ht_home': int,  # Goles local al descanso
                    'ht_away': int,  # Goles visitante al descanso
                    'cuota_local': float,
                    'cuota_empate': float,
                    'cuota_visitante': float,
                    'fecha': datetime
                }
        
        Returns:
            Lista de alertas generadas
        """
        alertas = []
        
        for regla in self.reglas_activas:
            # Preparar datos para evaluación
            p_dict = {
                'Local': partido.get('local', ''),
                'Visitante': partido.get('visitante', ''),
                'HT_Home': partido.get('ht_home', 0),
                'HT_Away': partido.get('ht_away', 0),
                'Cuota_Local': partido.get('cuota_local', 999),
                'Cuota_Empate': partido.get('cuota_empate', 999),
                'Cuota_Visitante': partido.get('cuota_visitante', 999)
            }
            
            # Evaluar regla
            if regla.evaluar(p_dict):
                # Determinar cuota según tipo de apuesta
                cuota = self._obtener_cuota(regla.tipo_apuesta, p_dict)
                
                # Obtener win rate histórico
                win_rate = self._obtener_win_rate_historico(regla.nombre)
                
                # Calcular stake (Kelly fraccionado)
                stake = self._calcular_stake(win_rate, cuota)
                
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
                    'roi_historico': self._obtener_roi_historico(regla.nombre)
                }
                
                alertas.append(alerta)
                logger.info(f"Alerta generada: {regla.nombre} para {partido.get('local')} vs {partido.get('visitante')}")
        
        return alertas
    
    def _obtener_cuota(self, tipo_apuesta: str, partido: Dict[str, Any]) -> float:
        """
        Obtiene la cuota apropiada según el tipo de apuesta
        """
        if tipo_apuesta == "Favorito":
            cuota_local = partido.get('Cuota_Local', 999)
            cuota_visitante = partido.get('Cuota_Visitante', 999)
            return min(cuota_local, cuota_visitante)
        
        elif tipo_apuesta == "Doble Chance (ganador HT)":
            # Doble chance del que gana al descanso
            return 1.20  # Cuota aproximada para doble chance
        
        elif tipo_apuesta in ["Under 2.5", "Over 2.5"]:
            return 1.90  # Cuota típica para over/under
        
        elif tipo_apuesta == "Gol en 2H":
            return 1.50  # Cuota típica para gol en segunda mitad
        
        return 1.90
    
    def _obtener_win_rate_historico(self, nombre_regla: str) -> float:
        """
        Obtiene el win rate histórico de una regla
        """
        win_rates = {
            'Ganando_1-0_HT_No_Pierde': 0.90,
            'Over25_Si_2Goles_HT': 0.858,
            'Favorito_Mantiene_Ventaja': 0.849,
            'Under25_Si_0-0_HT': 0.825
        }
        return win_rates.get(nombre_regla, 0.75)
    
    def _obtener_roi_historico(self, nombre_regla: str) -> float:
        """
        Obtiene el ROI histórico de una regla
        """
        rois = {
            'Ganando_1-0_HT_No_Pierde': 71.0,
            'Over25_Si_2Goles_HT': 63.0,
            'Favorito_Mantiene_Ventaja': 61.4,
            'Under25_Si_0-0_HT': 56.7
        }
        return rois.get(nombre_regla, 0.0)
    
    def _calcular_stake(self, win_rate: float, cuota: float) -> float:
        """
        Calcula el stake óptimo usando Kelly fraccionado
        """
        # Kelly fraccionado (25% del Kelly completo)
        kelly_fraction = 0.25
        
        # Fórmula de Kelly: (p * q - (1 - p)) / q
        # donde p = probabilidad de ganar, q = cuota - 1
        p = win_rate
        q = cuota - 1
        
        kelly = (p * cuota - 1) / q
        kelly_fraccionado = kelly * kelly_fraction
        
        # Limitar entre 0.5% y 3% del bankroll
        stake = max(0.005, min(kelly_fraccionado, 0.03))
        
        return round(stake * 100, 2)  # Convertir a porcentaje
    
    def enviar_alertas(self, alertas: List[Dict[str, Any]]):
        """
        Envía alertas por email
        """
        if not alertas:
            logger.info("No hay alertas para enviar")
            return
        
        for alerta in alertas:
            try:
                self.email_alert.enviar_alerta(alerta)
                logger.info(f"Email enviado para {alerta['regla']}")
            except Exception as e:
                logger.error(f"Error enviando email: {e}")
    
    def procesar_partidos_medio_tiempo(self, partidos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa una lista de partidos en medio tiempo
        
        Args:
            partidos: Lista de partidos con datos de medio tiempo
        
        Returns:
            Lista de todas las alertas generadas
        """
        todas_alertas = []
        
        for partido in partidos:
            alertas = self.evaluar_partido_medio_tiempo(partido)
            todas_alertas.extend(alertas)
        
        # Enviar alertas
        if todas_alertas:
            self.enviar_alertas(todas_alertas)
            logger.info(f"Total de alertas generadas: {len(todas_alertas)}")
        
        return todas_alertas


def ejemplo_uso():
    """
    Ejemplo de uso del monitor en vivo
    """
    monitor = LiveMonitor()
    
    # Ejemplo de partido en medio tiempo
    partido_ejemplo = {
        'local': 'Real Madrid',
        'visitante': 'Barcelona',
        'ht_home': 1,
        'ht_away': 0,
        'cuota_local': 1.50,
        'cuota_empate': 4.00,
        'cuota_visitante': 6.00,
        'fecha': datetime.now()
    }
    
    alertas = monitor.evaluar_partido_medio_tiempo(partido_ejemplo)
    
    print(f"\n🎯 Alertas generadas: {len(alertas)}\n")
    
    for alerta in alertas:
        print(f"Regla: {alerta['regla']}")
        print(f"Tipo: {alerta['tipo_apuesta']}")
        print(f"Confianza: {alerta['confianza']*100:.1f}%")
        print(f"Cuota: {alerta['cuota']:.2f}")
        print(f"Stake: {alerta['stake']:.2f}%")
        print(f"ROI histórico: +{alerta['roi_historico']:.1f}%")
        print("-" * 50)


if __name__ == '__main__':
    ejemplo_uso()


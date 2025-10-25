"""
Monitor de alertas automáticas
Responsabilidad: Evaluar próximos partidos y enviar alertas
"""

import pandas as pd
from typing import List, Dict
from datetime import datetime
import logging
import time

from src.data.unified_api import UnifiedAPIClient
from src.rules.laliga_rules import crear_reglas_laliga
from src.risk.kelly import recomendar_stake
from src.alerts.email_alert import EmailAlertSystem
from src.config import ALERT_CONFIG

logger = logging.getLogger(__name__)


class AlertMonitor:
    """Monitor que evalúa próximos partidos y genera alertas"""
    
    def __init__(self, config=ALERT_CONFIG):
        self.config = config
        self.api_client = UnifiedAPIClient()
        self.reglas = crear_reglas_laliga()
        self.email_system = EmailAlertSystem(config)
        
        # Filtrar solo reglas activas y rentables
        self.reglas_activas = [r for r in self.reglas if r.activa]
        logger.info(f"✓ Monitor inicializado con {len(self.reglas_activas)} reglas activas")
    
    def evaluar_proximos_partidos(self, dias: int = 7) -> List[Dict]:
        """
        Evalúa próximos partidos contra todas las reglas activas
        
        Args:
            dias: Días hacia adelante a evaluar
        
        Returns:
            Lista de alertas generadas
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🔍 EVALUANDO PRÓXIMOS PARTIDOS ({dias} días)")
        logger.info(f"{'='*70}\n")
        
        # Obtener próximos partidos
        partidos = self.api_client.get_proximos_partidos(dias)
        
        if not partidos:
            logger.warning("⚠️ No se encontraron próximos partidos")
            return []
        
        logger.info(f"📅 Partidos a evaluar: {len(partidos)}\n")
        
        alertas = []
        
        for partido in partidos:
            logger.info(f"⚽ {partido['local']} vs {partido['visitante']}")
            logger.info(f"   Fecha: {partido['fecha']}")
            
            # Convertir a formato evaluable
            partido_eval = self._preparar_partido_para_evaluacion(partido)
            
            # Evaluar contra cada regla
            for regla in self.reglas_activas:
                if regla.evaluar(partido_eval):
                    logger.info(f"   ✓ Dispara regla: {regla.nombre}")
                    
                    # Calcular stake recomendado
                    stake_info = recomendar_stake(
                        confianza=regla.confianza_esperada,
                        cuota=partido_eval.get('cuota', 1.5),
                        bankroll=1000  # Bankroll ejemplo
                    )
                    
                    # Crear alerta
                    alerta = {
                        'partido': partido,
                        'regla': regla.nombre,
                        'tipo_apuesta': regla.tipo_apuesta,
                        'confianza': regla.confianza_esperada,
                        'stake': stake_info['stake'],
                        'edge': stake_info['edge'],
                        'tiene_valor': stake_info['valor']
                    }
                    
                    alertas.append(alerta)
                    
                    # Enviar email si cumple umbral de confianza
                    if regla.confianza_esperada >= self.config.min_confidence:
                        self.email_system.enviar_alerta(
                            partido=partido,
                            regla=regla.nombre,
                            confianza=regla.confianza_esperada,
                            stake_recomendado=stake_info['stake']
                        )
            
            logger.info("")
        
        logger.info(f"{'='*70}")
        logger.info(f"✅ Evaluación completada: {len(alertas)} alertas generadas")
        logger.info(f"{'='*70}\n")
        
        return alertas
    
    def _preparar_partido_para_evaluacion(self, partido: Dict) -> pd.Series:
        """
        Convierte un partido de la API a formato evaluable por las reglas
        
        Args:
            partido: Dict con datos del partido
        
        Returns:
            Serie de pandas con formato estándar
        """
        # NOTA: En producción, aquí se calcularían las features reales
        # (forma, rachas, etc.) consultando el historial del equipo
        
        # Por ahora, valores por defecto para testing
        return pd.Series({
            'Date': partido.get('fecha'),
            'Local': partido.get('local'),
            'Visitante': partido.get('visitante'),
            'Cuota_Local': 1.5,  # Placeholder
            'Cuota_Visitante': 2.5,  # Placeholder
            'Cuota_Empate': 3.0,  # Placeholder
            'Local_Forma_L5': 10,  # Placeholder
            'Visitante_Forma_L5': 8,  # Placeholder
            'Local_Derrotas_L3': 0,  # Placeholder
            'Visitante_Derrotas_L3': 0,  # Placeholder
            'Local_Goles_Prom_L5': 1.8,  # Placeholder
            'Visitante_Goles_Prom_L5': 1.5,  # Placeholder
        })
    
    def ejecutar_monitor_continuo(self):
        """
        Ejecuta el monitor de forma continua con intervalos configurados
        """
        logger.info("🚀 Monitor de alertas iniciado")
        logger.info(f"⏰ Intervalo de chequeo: {self.config.check_interval_hours}h")
        logger.info(f"📧 Email: {self.config.receiver_email}")
        logger.info(f"🎯 Confianza mínima: {self.config.min_confidence:.0%}\n")
        
        try:
            while True:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"\n{'='*70}")
                logger.info(f"⏰ Chequeo: {timestamp}")
                logger.info(f"{'='*70}")
                
                # Evaluar próximos partidos
                alertas = self.evaluar_proximos_partidos(
                    dias=self.config.alert_hours_before // 24
                )
                
                # Esperar hasta el próximo chequeo
                logger.info(f"\n💤 Esperando {self.config.check_interval_hours}h hasta próximo chequeo...")
                time.sleep(self.config.check_interval_hours * 3600)
                
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Monitor detenido por el usuario")


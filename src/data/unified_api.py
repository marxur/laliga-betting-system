"""
API Unificada con sistema de fallback automático
Responsabilidad: Gestionar múltiples fuentes de datos con prioridad
"""

from typing import List, Dict, Optional
import logging

from src.data.api_sports import APISportsClient
from src.data.thesportsdb import TheSportsDBClient
from src.config import API_CONFIG

logger = logging.getLogger(__name__)


class UnifiedAPIClient:
    """
    Cliente unificado que gestiona múltiples APIs con fallback automático
    
    Prioridad:
    1. API-Sports.io (datos premium, tiempo real)
    2. TheSportsDB (respaldo gratuito)
    """
    
    def __init__(self, config=API_CONFIG):
        self.config = config
        self.api_sports = APISportsClient(config)
        self.thesportsdb = TheSportsDBClient(config)
        
        # Estado de las APIs
        self.api_sports_activa = True
        self.intentos_fallidos_api_sports = 0
        self.max_intentos_fallidos = 3
    
    def get_proximos_partidos(self, dias: int = 7) -> List[Dict]:
        """
        Obtiene próximos partidos con fallback automático
        
        Args:
            dias: Días hacia adelante (solo para API-Sports)
        
        Returns:
            Lista de próximos partidos
        """
        logger.info("🔍 Buscando próximos partidos...")
        
        # Intentar con API-Sports primero
        if self.api_sports_activa:
            try:
                partidos = self.api_sports.get_proximos_partidos(dias)
                
                if partidos:
                    logger.info(f"✓ API-Sports: {len(partidos)} partidos obtenidos")
                    self.intentos_fallidos_api_sports = 0
                    return self._normalizar_partidos_api_sports(partidos)
                else:
                    logger.warning("⚠️ API-Sports no devolvió partidos")
                    self.intentos_fallidos_api_sports += 1
                    
            except Exception as e:
                logger.error(f"❌ Error en API-Sports: {e}")
                self.intentos_fallidos_api_sports += 1
        
        # Desactivar API-Sports si falla repetidamente
        if self.intentos_fallidos_api_sports >= self.max_intentos_fallidos:
            logger.warning("⚠️ API-Sports desactivada temporalmente (muchos fallos)")
            self.api_sports_activa = False
        
        # Fallback a TheSportsDB
        if self.config.use_fallback:
            logger.info("🔄 Usando TheSportsDB como respaldo...")
            try:
                partidos = self.thesportsdb.get_proximos_partidos()
                
                if partidos:
                    logger.info(f"✓ TheSportsDB: {len(partidos)} partidos obtenidos")
                    return self._normalizar_partidos_thesportsdb(partidos)
                    
            except Exception as e:
                logger.error(f"❌ Error en TheSportsDB: {e}")
        
        logger.error("❌ No se pudieron obtener partidos de ninguna fuente")
        return []
    
    def _normalizar_partidos_api_sports(self, partidos: List[Dict]) -> List[Dict]:
        """
        Normaliza partidos de API-Sports a formato estándar
        
        Returns:
            Lista de partidos en formato estándar
        """
        normalizados = []
        
        for partido in partidos:
            try:
                fixture = partido.get('fixture', {})
                teams = partido.get('teams', {})
                
                normalizado = {
                    'id': fixture.get('id'),
                    'fecha': fixture.get('date'),
                    'local': teams.get('home', {}).get('name'),
                    'visitante': teams.get('away', {}).get('name'),
                    'local_id': teams.get('home', {}).get('id'),
                    'visitante_id': teams.get('away', {}).get('id'),
                    'estadio': fixture.get('venue', {}).get('name'),
                    'estado': fixture.get('status', {}).get('long'),
                    'fuente': 'api-sports'
                }
                
                normalizados.append(normalizado)
                
            except Exception as e:
                logger.warning(f"Error normalizando partido API-Sports: {e}")
                continue
        
        return normalizados
    
    def _normalizar_partidos_thesportsdb(self, partidos: List[Dict]) -> List[Dict]:
        """
        Normaliza partidos de TheSportsDB a formato estándar
        
        Returns:
            Lista de partidos en formato estándar
        """
        normalizados = []
        
        for partido in partidos:
            try:
                normalizado = {
                    'id': partido.get('idEvent'),
                    'fecha': f"{partido.get('dateEvent')} {partido.get('strTime', '00:00')}",
                    'local': partido.get('strHomeTeam'),
                    'visitante': partido.get('strAwayTeam'),
                    'local_id': partido.get('idHomeTeam'),
                    'visitante_id': partido.get('idAwayTeam'),
                    'estadio': partido.get('strVenue'),
                    'estado': partido.get('strStatus'),
                    'fuente': 'thesportsdb'
                }
                
                normalizados.append(normalizado)
                
            except Exception as e:
                logger.warning(f"Error normalizando partido TheSportsDB: {e}")
                continue
        
        return normalizados
    
    def reactivar_api_sports(self):
        """Reactiva API-Sports después de un período de enfriamiento"""
        self.api_sports_activa = True
        self.intentos_fallidos_api_sports = 0
        logger.info("✓ API-Sports reactivada")
    
    def get_estado_apis(self) -> Dict:
        """
        Obtiene el estado actual de todas las APIs
        
        Returns:
            Dict con estado de cada API
        """
        return {
            'api_sports': {
                'activa': self.api_sports_activa,
                'intentos_fallidos': self.intentos_fallidos_api_sports
            },
            'thesportsdb': {
                'activa': True,  # Siempre disponible
                'tipo': 'respaldo gratuito'
            }
        }


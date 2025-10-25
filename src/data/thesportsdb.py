"""
Integración con TheSportsDB (API gratuita de respaldo)
Responsabilidad: Obtener datos cuando API-Sports falla o se agota
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging

from src.config import API_CONFIG

logger = logging.getLogger(__name__)


class TheSportsDBClient:
    """Cliente para TheSportsDB API (respaldo gratuito)"""
    
    def __init__(self, config=API_CONFIG):
        self.config = config
        self.base_url = config.thesportsdb_base_url
        self.league_id = config.thesportsdb_league_id
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """
        Realiza petición a TheSportsDB
        
        Args:
            endpoint: Endpoint completo con parámetros
        
        Returns:
            Respuesta JSON o None
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en TheSportsDB: {e}")
            return None
    
    def get_proximos_partidos(self, limit: int = 15) -> List[Dict]:
        """
        Obtiene próximos partidos de La Liga
        
        Args:
            limit: Número máximo de partidos
        
        Returns:
            Lista de partidos
        """
        endpoint = f"eventsnextleague.php?id={self.league_id}"
        data = self._make_request(endpoint)
        
        if data and 'events' in data and data['events']:
            partidos = data['events'][:limit]
            logger.info(f"✓ TheSportsDB: {len(partidos)} próximos partidos")
            return partidos
        
        logger.warning("TheSportsDB: No se encontraron próximos partidos")
        return []
    
    def get_resultados_recientes(self, limit: int = 50) -> List[Dict]:
        """
        Obtiene resultados recientes de La Liga
        
        Args:
            limit: Número máximo de partidos
        
        Returns:
            Lista de partidos pasados
        """
        endpoint = f"eventspastleague.php?id={self.league_id}"
        data = self._make_request(endpoint)
        
        if data and 'events' in data and data['events']:
            partidos = data['events'][:limit]
            logger.info(f"✓ TheSportsDB: {len(partidos)} resultados recientes")
            return partidos
        
        return []
    
    def get_info_equipo(self, team_id: str) -> Optional[Dict]:
        """
        Obtiene información de un equipo
        
        Args:
            team_id: ID del equipo en TheSportsDB
        
        Returns:
            Dict con info del equipo o None
        """
        endpoint = f"lookupteam.php?id={team_id}"
        data = self._make_request(endpoint)
        
        if data and 'teams' in data and data['teams']:
            return data['teams'][0]
        
        return None
    
    def get_detalles_partido(self, event_id: str) -> Optional[Dict]:
        """
        Obtiene detalles de un partido específico
        
        Args:
            event_id: ID del evento
        
        Returns:
            Dict con detalles del partido
        """
        endpoint = f"lookupevent.php?id={event_id}"
        data = self._make_request(endpoint)
        
        if data and 'events' in data and data['events']:
            return data['events'][0]
        
        return None
    
    def buscar_equipo_por_nombre(self, nombre: str) -> Optional[Dict]:
        """
        Busca un equipo por nombre
        
        Args:
            nombre: Nombre del equipo
        
        Returns:
            Dict con info del equipo
        """
        endpoint = f"searchteams.php?t={nombre}"
        data = self._make_request(endpoint)
        
        if data and 'teams' in data and data['teams']:
            # Filtrar solo equipos de La Liga
            for team in data['teams']:
                if team.get('idLeague') == self.league_id:
                    return team
        
        return None


"""
Integración con API-Sports.io
Responsabilidad: Obtener datos en tiempo real de La Liga
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import time

from src.config import API_CONFIG

logger = logging.getLogger(__name__)


class APISportsClient:
    """Cliente para API-Sports.io"""
    
    def __init__(self, config=API_CONFIG):
        self.config = config
        self.base_url = config.api_sports_base_url
        self.headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': config.api_sports_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Realiza una petición a la API con manejo de errores
        
        Args:
            endpoint: Endpoint de la API (ej: '/fixtures')
            params: Parámetros de la query
        
        Returns:
            Respuesta JSON o None si falla
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Verificar si la respuesta es válida
                if data.get('errors'):
                    logger.error(f"API Error: {data['errors']}")
                    return None
                
                return data
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento {attempt + 1}/{self.config.max_retries} falló: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Error en petición a {endpoint}: {e}")
                    return None
        
        return None
    
    def get_proximos_partidos(self, dias: int = 7) -> List[Dict]:
        """
        Obtiene próximos partidos de La Liga
        
        Args:
            dias: Número de días hacia adelante
        
        Returns:
            Lista de partidos
        """
        fecha_desde = datetime.now().strftime('%Y-%m-%d')
        fecha_hasta = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')
        
        params = {
            'league': self.config.api_sports_league_id,
            'season': datetime.now().year,
            'from': fecha_desde,
            'to': fecha_hasta
        }
        
        data = self._make_request('/fixtures', params)
        
        if data and 'response' in data:
            logger.info(f"✓ Obtenidos {len(data['response'])} próximos partidos")
            return data['response']
        
        return []
    
    def get_estadisticas_partido(self, fixture_id: int) -> Optional[Dict]:
        """
        Obtiene estadísticas detalladas de un partido
        
        Args:
            fixture_id: ID del partido
        
        Returns:
            Dict con estadísticas o None
        """
        params = {'fixture': fixture_id}
        data = self._make_request('/fixtures/statistics', params)
        
        if data and 'response' in data:
            return data['response']
        
        return None
    
    def get_estadisticas_equipo(self, team_id: int, season: int = None) -> Optional[Dict]:
        """
        Obtiene estadísticas de un equipo en la temporada
        
        Args:
            team_id: ID del equipo
            season: Año de la temporada (default: actual)
        
        Returns:
            Dict con estadísticas o None
        """
        if season is None:
            season = datetime.now().year
        
        params = {
            'team': team_id,
            'league': self.config.api_sports_league_id,
            'season': season
        }
        
        data = self._make_request('/teams/statistics', params)
        
        if data and 'response' in data:
            return data['response']
        
        return None
    
    def get_clasificacion(self, season: int = None) -> List[Dict]:
        """
        Obtiene la clasificación actual de La Liga
        
        Args:
            season: Año de la temporada (default: actual)
        
        Returns:
            Lista con la clasificación
        """
        if season is None:
            season = datetime.now().year
        
        params = {
            'league': self.config.api_sports_league_id,
            'season': season
        }
        
        data = self._make_request('/standings', params)
        
        if data and 'response' in data:
            return data['response']
        
        return []
    
    def check_api_status(self) -> Dict:
        """
        Verifica el estado de la API y el límite de requests
        
        Returns:
            Dict con información del estado
        """
        data = self._make_request('/status')
        
        if data:
            return {
                'activa': True,
                'requests_disponibles': data.get('response', {}).get('requests', {}).get('current', 0),
                'limite_diario': data.get('response', {}).get('requests', {}).get('limit_day', 0)
            }
        
        return {'activa': False}


"""
Configuración centralizada del sistema
Todos los parámetros configurables en un solo lugar
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List
import os

# Rutas base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"


@dataclass
class DataConfig:
    """Configuración de datos"""
    raw_dir: Path = DATA_DIR / "raw"
    processed_dir: Path = DATA_DIR / "processed"
    splits_dir: Path = DATA_DIR / "splits"
    proximos_dir: Path = DATA_DIR / "proximos"
    
    # URLs de descarga (Football-Data.co.uk - histórico)
    base_url: str = "https://www.football-data.co.uk/mmz4281/"
    liga_code: str = "SP1"  # La Liga
    
    # Temporadas a cargar
    temporadas: List[str] = None  # ['1819', '1920', ..., '2425']
    
    def __post_init__(self):
        if self.temporadas is None:
            # Generar automáticamente desde 2018 hasta 2025
            self.temporadas = [f"{i}{i+1}" for i in range(18, 25)]


@dataclass
class APIConfig:
    """Configuración de APIs"""
    
    # API-Sports.io (Principal)
    api_sports_key: str = os.getenv('API_SPORTS_KEY', 'TU_API_KEY_AQUI')
    api_sports_base_url: str = "https://v3.football.api-sports.io"
    api_sports_league_id: int = 140  # La Liga
    
    # TheSportsDB (Respaldo gratuito)
    thesportsdb_base_url: str = "https://www.thesportsdb.com/api/v1/json/3"
    thesportsdb_league_id: str = "4335"  # La Liga
    
    # Configuración de fallback
    use_fallback: bool = True
    max_retries: int = 3
    timeout: int = 10


@dataclass
class BacktestConfig:
    """Configuración de backtesting"""
    # División temporal
    train_end_date: str = "2023-12-31"
    test_start_date: str = "2024-01-01"
    
    # Filtros de validez
    min_sample_size: int = 30  # Mínimo de disparos para considerar regla
    min_win_rate: float = 0.55  # Mínima tasa de acierto
    min_roi: float = 0.0  # Mínimo ROI
    
    # Significancia estadística
    alpha: float = 0.05  # Nivel de significancia
    null_hypothesis_prob: float = 0.5  # Prob de acertar por azar
    
    # Gestión de riesgo
    kelly_fraction: float = 0.25  # Fracción de Kelly (conservador)
    max_stake: float = 0.05  # Máximo 5% del bankroll por apuesta


@dataclass
class AlertConfig:
    """Configuración de alertas"""
    # Email configurado para Marcos Valencia García
    email_enabled: bool = True
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = "marcosvalenciagarcia@gmail.com"
    sender_password: str = os.getenv('EMAIL_PASSWORD', '')  # Usar variable de entorno
    receiver_email: str = "marcosvalenciagarcia@gmail.com"
    
    # Umbrales de alerta
    min_confidence: float = 0.60  # Solo alertar si confianza >= 60%
    alert_hours_before: int = 24  # Alertar con 24h de antelación
    
    # Frecuencia de monitoreo
    check_interval_hours: int = 24  # Chequear cada 24 horas


@dataclass
class FeatureConfig:
    """Configuración de features"""
    # Ventanas temporales
    forma_window: int = 5  # Últimos N partidos para forma
    racha_window: int = 3  # Últimos N para racha
    goles_window: int = 5  # Últimos N para promedio goles
    
    # Features a calcular
    calculate_form: bool = True
    calculate_streaks: bool = True
    calculate_goal_avg: bool = True
    calculate_btts: bool = True


# Instancias globales
DATA_CONFIG = DataConfig()
API_CONFIG = APIConfig()
BACKTEST_CONFIG = BacktestConfig()
ALERT_CONFIG = AlertConfig()
FEATURE_CONFIG = FeatureConfig()


"""
Script para iniciar el monitor de alertas
Uso: python scripts/start_monitor.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from src.alerts.monitor import AlertMonitor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('outputs/logs/monitor.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Inicia el monitor de alertas"""
    
    logger.info("\n" + "="*70)
    logger.info("🚀 SISTEMA DE ALERTAS - LA LIGA")
    logger.info("="*70 + "\n")
    
    # Crear monitor
    monitor = AlertMonitor()
    
    # Ejecutar monitor continuo
    monitor.ejecutar_monitor_continuo()


if __name__ == "__main__":
    main()


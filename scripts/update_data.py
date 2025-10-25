"""
Script de actualización de datos
Uso: python scripts/update_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from src.data.loader import LaLigaLoader
from src.data.cleaner import DataCleaner
from src.data.feature_engineering import FeatureEngineer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Actualiza datos desde football-data.co.uk"""
    
    logger.info("\n" + "="*60)
    logger.info("🔄 ACTUALIZACIÓN DE DATOS")
    logger.info("="*60 + "\n")
    
    # Cargar datos frescos
    loader = LaLigaLoader()
    df_raw = loader.cargar_todas_temporadas()
    
    # Limpiar
    cleaner = DataCleaner()
    df_clean = cleaner.limpiar(df_raw)
    
    # Generar features
    engineer = FeatureEngineer()
    df_features = engineer.generar_todas_features(df_clean)
    
    # Guardar
    loader.guardar_procesado(df_clean, 'laliga_completo')
    loader.guardar_procesado(df_features, 'laliga_features')
    
    logger.info("\n✅ Datos actualizados correctamente\n")


if __name__ == "__main__":
    main()


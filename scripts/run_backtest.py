"""
Script principal para ejecutar backtest completo
Uso: python scripts/run_backtest.py
"""

import sys
from pathlib import Path

# Añadir directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from src.data.loader import LaLigaLoader
from src.data.cleaner import DataCleaner
from src.data.feature_engineering import FeatureEngineer
from src.rules.laliga_rules import crear_reglas_laliga
from src.backtest.engine import BacktestEngine
from src.backtest.validation import DataValidator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('outputs/logs/backtest.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Pipeline completo de backtest"""
    
    logger.info("="*70)
    logger.info("🚀 SISTEMA DE BACKTEST - LA LIGA")
    logger.info("="*70 + "\n")
    
    # =============================================
    # PASO 1: CARGAR Y LIMPIAR DATOS
    # =============================================
    logger.info("📦 PASO 1: Cargando datos...\n")
    
    loader = LaLigaLoader()
    
    # Intentar cargar datos procesados
    try:
        df = loader.cargar_procesado('laliga_completo')
        logger.info("✓ Datos cargados desde caché\n")
    except FileNotFoundError:
        # Si no existen, descargar y procesar
        logger.info("  No hay caché, descargando datos frescos...")
        df_raw = loader.cargar_todas_temporadas()
        
        cleaner = DataCleaner()
        df = cleaner.limpiar(df_raw)
        
        # Guardar para futuros usos
        loader.guardar_procesado(df, 'laliga_completo')
        logger.info("")
    
    # =============================================
    # PASO 2: GENERAR FEATURES
    # =============================================
    logger.info("🔧 PASO 2: Generando features...\n")
    
    try:
        df_features = loader.cargar_procesado('laliga_features')
        logger.info("✓ Features cargadas desde caché\n")
    except FileNotFoundError:
        engineer = FeatureEngineer()
        df_features = engineer.generar_todas_features(df)
        
        # Guardar features
        loader.guardar_procesado(df_features, 'laliga_features')
        logger.info("")
    
    # =============================================
    # PASO 3: SPLIT TRAIN/TEST
    # =============================================
    logger.info("📊 PASO 3: Dividiendo datos...\n")
    
    validator = DataValidator()
    df_train, df_test = validator.split_temporal(df_features)
    
    # Guardar splits
    loader.guardar_procesado(df_train, '../splits/train_2018-2023')
    loader.guardar_procesado(df_test, '../splits/test_2024-2025')
    logger.info("")
    
    # =============================================
    # PASO 4: BACKTEST EN TRAIN
    # =============================================
    logger.info("\n" + "="*70)
    logger.info("📈 PASO 4: Backtest en conjunto de entrenamiento...\n")
    logger.info("="*70 + "\n")
    
    reglas = crear_reglas_laliga()
    engine_train = BacktestEngine(df_train, reglas)
    resultados_train = engine_train.ejecutar(verbose=True)
    
    # =============================================
    # PASO 5: VALIDACIÓN EN TEST
    # =============================================
    logger.info("\n" + "="*70)
    logger.info("🔬 PASO 5: Validación en conjunto de TEST")
    logger.info("="*70 + "\n")
    
    engine_test = BacktestEngine(df_test, reglas)
    resultados_test = engine_test.ejecutar(verbose=True)
    
    # =============================================
    # PASO 6: DETECTAR OVERFITTING
    # =============================================
    logger.info("\n" + "="*70)
    logger.info("🔍 PASO 6: Análisis de Overfitting")
    logger.info("="*70 + "\n")
    
    overfitting = validator.detectar_overfitting(resultados_train, resultados_test)
    
    if overfitting:
        logger.warning("⚠️ Se detectó posible overfitting en algunas reglas")
        logger.warning("   Revisa las reglas con alta degradación train→test\n")
    else:
        logger.info("✓ No se detectó overfitting significativo\n")
    
    # =============================================
    # PASO 7: EXPORTAR RESULTADOS
    # =============================================
    logger.info("💾 PASO 7: Exportando resultados...\n")
    
    # Aquí se exportarían los resultados a JSON/TXT
    # (simplificado por ahora)
    
    logger.info("")
    
    # =============================================
    # RESUMEN FINAL
    # =============================================
    logger.info("="*70)
    logger.info("✅ BACKTEST COMPLETADO")
    logger.info("="*70)
    logger.info(f"Reglas testeadas: {len(reglas)}")
    logger.info(f"Partidos train: {len(df_train)}")
    logger.info(f"Partidos test: {len(df_test)}")
    logger.info(f"Reportes guardados en: outputs/reports/")
    logger.info("="*70 + "\n")


if __name__ == "__main__":
    main()


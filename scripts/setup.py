"""
Script de configuración inicial del sistema
Uso: python scripts/setup.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import logging
from getpass import getpass

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def crear_archivo_env():
    """Crea archivo .env con las credenciales del usuario"""
    
    logger.info("\n" + "="*70)
    logger.info("🔧 CONFIGURACIÓN INICIAL DEL SISTEMA")
    logger.info("="*70 + "\n")
    
    env_path = Path(__file__).parent.parent / ".env"
    
    if env_path.exists():
        respuesta = input("⚠️  El archivo .env ya existe. ¿Sobrescribir? (s/n): ")
        if respuesta.lower() != 's':
            logger.info("❌ Configuración cancelada")
            return
    
    logger.info("📝 Ingresa tus credenciales:\n")
    
    # API-Sports Key
    logger.info("1️⃣  API-Sports.io")
    logger.info("   Obtén tu API key en: https://dashboard.api-football.com/")
    api_key = input("   API Key: ").strip()
    
    # Email Password
    logger.info("\n2️⃣  Gmail (Contraseña de Aplicación)")
    logger.info("   Genera una en: https://myaccount.google.com/apppasswords")
    logger.info("   Email configurado: marcosvalenciagarcia@gmail.com")
    email_password = getpass("   Contraseña de Aplicación: ").strip()
    
    # Crear archivo .env
    with open(env_path, 'w') as f:
        f.write(f"# Configuración del Sistema\n")
        f.write(f"# Generado automáticamente\n\n")
        f.write(f"API_SPORTS_KEY={api_key}\n")
        f.write(f"EMAIL_PASSWORD={email_password}\n")
    
    logger.info("\n✅ Archivo .env creado exitosamente")
    logger.info(f"📁 Ubicación: {env_path}\n")
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    logger.info("="*70)
    logger.info("✅ CONFIGURACIÓN COMPLETADA")
    logger.info("="*70)
    logger.info("\n📌 Próximos pasos:")
    logger.info("   1. Ejecutar backtest: python scripts/run_backtest.py")
    logger.info("   2. Iniciar monitor: python scripts/start_monitor.py\n")


def main():
    """Ejecuta la configuración inicial"""
    try:
        crear_archivo_env()
    except KeyboardInterrupt:
        logger.info("\n\n❌ Configuración cancelada por el usuario")
    except Exception as e:
        logger.error(f"\n❌ Error durante la configuración: {e}")


if __name__ == "__main__":
    main()


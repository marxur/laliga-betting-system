"""
Script para verificar la configuración del sistema
Uso: python scripts/test_config.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_env_file():
    """Verifica que el archivo .env existe y tiene las variables necesarias"""
    env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        logger.error("❌ Archivo .env no encontrado")
        logger.info("   Ejecuta: python scripts/setup.py")
        return False
    
    load_dotenv(env_path)
    
    api_key = os.getenv('API_SPORTS_KEY')
    email_pass = os.getenv('EMAIL_PASSWORD')
    
    if not api_key or api_key == 'tu_api_key_de_api_sports_aqui':
        logger.error("❌ API_SPORTS_KEY no configurada")
        return False
    
    if not email_pass or email_pass == 'tu_contraseña_de_aplicacion_gmail_aqui':
        logger.error("❌ EMAIL_PASSWORD no configurada")
        return False
    
    logger.info("✅ Archivo .env configurado correctamente")
    return True


def test_api_sports():
    """Prueba la conexión con API-Sports.io"""
    try:
        from src.data.api_sports import APISportsClient
        
        client = APISportsClient()
        status = client.check_api_status()
        
        if status.get('activa'):
            logger.info("✅ API-Sports.io: Conectado")
            logger.info(f"   Requests disponibles: {status.get('requests_disponibles', 'N/A')}")
            return True
        else:
            logger.warning("⚠️  API-Sports.io: No disponible")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error probando API-Sports: {e}")
        return False


def test_thesportsdb():
    """Prueba la conexión con TheSportsDB"""
    try:
        from src.data.thesportsdb import TheSportsDBClient
        
        client = TheSportsDBClient()
        partidos = client.get_proximos_partidos(limit=1)
        
        if partidos:
            logger.info("✅ TheSportsDB: Conectado")
            return True
        else:
            logger.warning("⚠️  TheSportsDB: Sin datos")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error probando TheSportsDB: {e}")
        return False


def test_email():
    """Verifica la configuración de email"""
    from src.config import ALERT_CONFIG
    
    if ALERT_CONFIG.sender_email == "marcosvalenciagarcia@gmail.com":
        logger.info("✅ Email configurado: marcosvalenciagarcia@gmail.com")
        return True
    else:
        logger.warning("⚠️  Email no configurado correctamente")
        return False


def main():
    """Ejecuta todas las pruebas"""
    logger.info("\n" + "="*70)
    logger.info("🔍 VERIFICACIÓN DE CONFIGURACIÓN")
    logger.info("="*70 + "\n")
    
    resultados = []
    
    # Test 1: Archivo .env
    logger.info("1️⃣  Verificando archivo .env...")
    resultados.append(test_env_file())
    logger.info("")
    
    # Test 2: API-Sports
    logger.info("2️⃣  Probando API-Sports.io...")
    resultados.append(test_api_sports())
    logger.info("")
    
    # Test 3: TheSportsDB
    logger.info("3️⃣  Probando TheSportsDB...")
    resultados.append(test_thesportsdb())
    logger.info("")
    
    # Test 4: Email
    logger.info("4️⃣  Verificando configuración de email...")
    resultados.append(test_email())
    logger.info("")
    
    # Resumen
    logger.info("="*70)
    if all(resultados):
        logger.info("✅ TODAS LAS PRUEBAS PASARON")
        logger.info("   El sistema está listo para usar")
    else:
        logger.info("⚠️  ALGUNAS PRUEBAS FALLARON")
        logger.info("   Revisa los errores arriba")
    logger.info("="*70 + "\n")


if __name__ == "__main__":
    main()


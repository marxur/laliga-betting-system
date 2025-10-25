"""
Aplicación web para controlar el sistema de alertas
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
from pathlib import Path
import os
import logging
from datetime import datetime
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.unified_api import UnifiedAPIClient
from src.alerts.monitor import AlertMonitor
from src.config import API_CONFIG, ALERT_CONFIG

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Estado global del sistema
sistema_estado = {
    'monitor_activo': False,
    'ultima_ejecucion': None,
    'alertas_generadas': [],
    'api_configurada': bool(os.getenv('API_SPORTS_KEY')),
    'email_configurado': bool(os.getenv('EMAIL_PASSWORD'))
}


@app.route('/')
def index():
    """Página principal del dashboard"""
    # Actualizar estado de configuración
    sistema_estado['api_configurada'] = bool(os.getenv('API_SPORTS_KEY'))
    sistema_estado['email_configurado'] = bool(os.getenv('EMAIL_PASSWORD'))
    return render_template('index.html', estado=sistema_estado)


@app.route('/configurar', methods=['GET', 'POST'])
def configurar():
    """Página de configuración"""
    if request.method == 'POST':
        api_key = request.form.get('api_key', '').strip()
        email_password = request.form.get('email_password', '').strip()
        
        # Guardar en archivo .env
        env_path = Path(__file__).parent.parent / '.env'
        with open(env_path, 'w') as f:
            f.write(f"API_SPORTS_KEY={api_key}\n")
            f.write(f"EMAIL_PASSWORD={email_password}\n")
        
        # Actualizar estado
        sistema_estado['api_configurada'] = bool(api_key)
        sistema_estado['email_configurado'] = bool(email_password)
        
        # Actualizar variables de entorno en memoria
        os.environ['API_SPORTS_KEY'] = api_key
        os.environ['EMAIL_PASSWORD'] = email_password
        
        return redirect(url_for('index'))
    
    return render_template('configurar.html')


@app.route('/api/estado')
def api_estado():
    """API para obtener el estado del sistema"""
    # Actualizar estado de configuración
    sistema_estado['api_configurada'] = bool(os.getenv('API_SPORTS_KEY'))
    sistema_estado['email_configurado'] = bool(os.getenv('EMAIL_PASSWORD'))
    return jsonify(sistema_estado)


@app.route('/api/evaluar-partidos')
def api_evaluar_partidos():
    """API para evaluar próximos partidos manualmente"""
    try:
        # Verificar configuración
        if not os.getenv('API_SPORTS_KEY'):
            return jsonify({
                'success': False,
                'error': 'API Key no configurada. Ve a Configuración.'
            }), 400
        
        monitor = AlertMonitor()
        alertas = monitor.evaluar_proximos_partidos(dias=7)
        
        sistema_estado['ultima_ejecucion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sistema_estado['alertas_generadas'] = alertas
        
        return jsonify({
            'success': True,
            'alertas': len(alertas),
            'detalles': alertas
        })
    except Exception as e:
        logger.error(f"Error evaluando partidos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test-apis')
def api_test_apis():
    """API para probar las conexiones a las APIs"""
    try:
        # Verificar configuración
        if not os.getenv('API_SPORTS_KEY'):
            return jsonify({
                'success': False,
                'error': 'API Key no configurada. Ve a Configuración.'
            }), 400
        
        client = UnifiedAPIClient()
        estado_apis = client.get_estado_apis()
        
        # Intentar obtener partidos
        partidos = client.get_proximos_partidos(dias=7)
        
        return jsonify({
            'success': True,
            'estado_apis': estado_apis,
            'partidos_obtenidos': len(partidos)
        })
    except Exception as e:
        logger.error(f"Error probando APIs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/proximos-partidos')
def api_proximos_partidos():
    """API para obtener próximos partidos"""
    try:
        # Verificar configuración
        if not os.getenv('API_SPORTS_KEY'):
            return jsonify({
                'success': False,
                'error': 'API Key no configurada. Ve a Configuración.'
            }), 400
        
        client = UnifiedAPIClient()
        partidos = client.get_proximos_partidos(dias=7)
        
        return jsonify({
            'success': True,
            'partidos': partidos
        })
    except Exception as e:
        logger.error(f"Error obteniendo partidos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/resultados')
def resultados():
    """Página con resultados del backtest"""
    # Leer archivo de análisis
    analisis_path = Path(__file__).parent.parent / 'outputs' / 'reports' / 'analisis_resultados.md'
    
    if analisis_path.exists():
        with open(analisis_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            # Convertir markdown a HTML básico
            contenido = contenido.replace('\n', '<br>')
    else:
        contenido = "No hay resultados disponibles. Ejecuta el backtest primero."
    
    return render_template('resultados.html', contenido=contenido)


if __name__ == '__main__':
    # Usar puerto de entorno o 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


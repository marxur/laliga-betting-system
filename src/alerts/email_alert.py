"""
Sistema de alertas por email
Responsabilidad: Enviar notificaciones de apuestas
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import logging

from src.config import ALERT_CONFIG

logger = logging.getLogger(__name__)


class EmailAlertSystem:
    """Sistema de alertas por email"""
    
    def __init__(self, config=ALERT_CONFIG):
        self.config = config
    
    def enviar_alerta(
        self,
        partido: Dict[str, Any],
        regla: str,
        confianza: float,
        stake_recomendado: float
    ) -> bool:
        """
        Envía alerta de apuesta por email
        
        Args:
            partido: Dict con info del partido
            regla: Nombre de la regla que disparó
            confianza: Confianza de la regla
            stake_recomendado: Stake recomendado por Kelly
        
        Returns:
            True si se envió correctamente
        """
        
        if not self.config.email_enabled:
            logger.info("📧 Email deshabilitado en config")
            return False
        
        # Validar confianza mínima
        if confianza < self.config.min_confidence:
            logger.info(f"⚠️ Confianza {confianza:.1%} < umbral {self.config.min_confidence:.1%}")
            return False
        
        # Construir mensaje
        asunto = f"🎯 Alerta de Apuesta: {partido['local']} vs {partido['visitante']}"
        cuerpo = self._construir_mensaje(partido, regla, confianza, stake_recomendado)
        
        # Enviar
        try:
            self._enviar_email(asunto, cuerpo)
            logger.info(f"✓ Alerta enviada: {regla}")
            return True
        except Exception as e:
            logger.error(f"✗ Error enviando email: {e}")
            return False
    
    def _construir_mensaje(
        self,
        partido: Dict[str, Any],
        regla: str,
        confianza: float,
        stake: float
    ) -> str:
        """Construye mensaje HTML del email"""
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2c3e50;">🎯 Nueva Oportunidad de Apuesta</h2>
            
            <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px;">
                <h3>📅 {partido.get('fecha', 'Fecha desconocida')}</h3>
                <h3>⚽ {partido['local']} vs {partido['visitante']}</h3>
            </div>
            
            <div style="margin-top: 20px;">
                <h3>📊 Detalles de la Apuesta</h3>
                <ul>
                    <li><strong>Regla:</strong> {regla}</li>
                    <li><strong>Tipo:</strong> {partido.get('tipo_apuesta', 'N/A')}</li>
                    <li><strong>Cuota:</strong> {partido.get('cuota', 0):.2f}</li>
                    <li><strong>Confianza:</strong> {confianza:.1%}</li>
                </ul>
            </div>
            
            <div style="margin-top: 20px; background-color: #d5f4e6; padding: 15px; border-radius: 5px;">
                <h3>💰 Gestión de Riesgo (Kelly)</h3>
                <ul>
                    <li><strong>Stake Recomendado:</strong> {stake:.2f} unidades</li>
                    <li><strong>Kelly Fraction:</strong> 0.25 (conservador)</li>
                </ul>
            </div>
            
            <div style="margin-top: 30px; color: #7f8c8d; font-size: 12px;">
                <p>⚠️ <em>Esta alerta es solo informativa. Apuesta bajo tu propia responsabilidad.</em></p>
                <p>Sistema de Alertas - La Liga Betting</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _enviar_email(self, asunto: str, cuerpo_html: str):
        """Envía email usando SMTP"""
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = self.config.sender_email
        msg['To'] = self.config.receiver_email
        
        # Adjuntar HTML
        html_part = MIMEText(cuerpo_html, 'html')
        msg.attach(html_part)
        
        # Conectar y enviar
        with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
            server.starttls()
            server.login(self.config.sender_email, self.config.sender_password)
            server.send_message(msg)
    
    def enviar_resumen_diario(self, alertas: List[Dict[str, Any]]):
        """Envía resumen diario de todas las alertas"""
        
        if not alertas:
            logger.info("📧 No hay alertas para enviar")
            return
        
        asunto = f"📊 Resumen Diario - {len(alertas)} Alertas"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>📊 Resumen Diario de Alertas</h2>
            <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
            <p><strong>Total de alertas:</strong> {len(alertas)}</p>
            
            <hr>
        """
        
        for alerta in alertas:
            html += f"""
            <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #007bff;">
                <h3>{alerta['partido']['local']} vs {alerta['partido']['visitante']}</h3>
                <p><strong>Regla:</strong> {alerta['regla']}</p>
                <p><strong>Confianza:</strong> {alerta['confianza']:.1%}</p>
                <p><strong>Stake:</strong> {alerta['stake']:.2f} unidades</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        try:
            self._enviar_email(asunto, html)
            logger.info(f"✓ Resumen diario enviado ({len(alertas)} alertas)")
        except Exception as e:
            logger.error(f"✗ Error enviando resumen: {e}")


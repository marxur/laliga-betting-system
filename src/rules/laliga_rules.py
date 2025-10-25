"""
Reglas específicas para La Liga
AQUÍ defines tus reglas del 80% de acierto
"""

from typing import List
from src.rules.base import Regla


def crear_reglas_laliga() -> List[Regla]:
    """
    Factory function que crea todas las reglas de La Liga
    
    Returns:
        Lista de objetos Regla configurados
    """
    
    reglas = [
        
        # =============================================
        # REGLA 1: Favorito local con buena forma
        # =============================================
        Regla(
            nombre="Favorito_Local_Forma",
            descripcion="Local con cuota <1.70 y forma >10pts últimos 5 partidos",
            condicion=lambda p: (
                p.get('Cuota_Local', 999) < 1.70 and
                p.get('Local_Forma_L5', 0) >= 10
            ),
            tipo_apuesta='Local',
            confianza_esperada=0.78,
            activa=True
        ),
        
        # =============================================
        # REGLA 2: Visitante invicto
        # =============================================
        Regla(
            nombre="Visitante_Invicto",
            descripcion="Visitante sin derrotas últimos 3 partidos y cuota <3.0",
            condicion=lambda p: (
                p.get('Visitante_Derrotas_L3', 99) == 0 and
                p.get('Cuota_Visitante', 999) < 3.0 and
                p.get('Visitante_Forma_L5', 0) >= 8
            ),
            tipo_apuesta='Visitante',
            confianza_esperada=0.72,
            activa=True
        ),
        
        # =============================================
        # REGLA 3: BTTS con equipos goleadores
        # =============================================
        Regla(
            nombre="BTTS_Goleadores",
            descripcion="Ambos equipos con promedio >1.5 goles últimos 5 partidos",
            condicion=lambda p: (
                p.get('Local_Goles_Prom_L5', 0) > 1.5 and
                p.get('Visitante_Goles_Prom_L5', 0) > 1.5
            ),
            tipo_apuesta='BTTS',
            confianza_esperada=0.68,
            activa=True
        ),
        
        # =============================================
        # REGLA 4: Local dominante en casa
        # =============================================
        Regla(
            nombre="Local_Dominante_Casa",
            descripcion="Local con >12pts forma y cuota <2.0",
            condicion=lambda p: (
                p.get('Local_Forma_L5', 0) >= 12 and
                p.get('Cuota_Local', 999) < 2.0
            ),
            tipo_apuesta='Local',
            confianza_esperada=0.75,
            activa=True
        ),
        
        # =============================================
        # REGLA 5: Visitante con racha
        # =============================================
        Regla(
            nombre="Visitante_Racha_Victorias",
            descripcion="Visitante con 2+ victorias consecutivas y cuota <2.5",
            condicion=lambda p: (
                p.get('Visitante_Victorias_L3', 0) >= 2 and
                p.get('Cuota_Visitante', 999) < 2.5
            ),
            tipo_apuesta='Visitante',
            confianza_esperada=0.70,
            activa=True
        ),
        
        # =============================================
        # REGLA 6: Over 2.5 con equipos ofensivos
        # =============================================
        Regla(
            nombre="Over_25_Ofensivos",
            descripcion="Suma promedios goles >3.5 últimos 5 partidos",
            condicion=lambda p: (
                p.get('Local_Goles_Prom_L5', 0) + p.get('Visitante_Goles_Prom_L5', 0) > 3.5
            ),
            tipo_apuesta='Over',
            confianza_esperada=0.65,
            activa=True
        ),
        
        # =============================================
        # REGLA 7: Local invicto con cuota baja
        # =============================================
        Regla(
            nombre="Local_Invicto_Favorito",
            descripcion="Local sin derrotas últimos 3 y cuota <1.50",
            condicion=lambda p: (
                p.get('Local_Derrotas_L3', 99) == 0 and
                p.get('Cuota_Local', 999) < 1.50
            ),
            tipo_apuesta='Local',
            confianza_esperada=0.82,
            activa=True
        ),
        
        # =============================================
        # REGLA 8: BTTS histórico alto
        # =============================================
        Regla(
            nombre="BTTS_Historico_Alto",
            descripcion="Ambos equipos con BTTS en 3+ de últimos 4 partidos",
            condicion=lambda p: (
                p.get('Local_BTTS_L4', 0) >= 3 and
                p.get('Visitante_BTTS_L4', 0) >= 3
            ),
            tipo_apuesta='BTTS',
            confianza_esperada=0.71,
            activa=True
        ),
        
    ]
    
    # Validar todas las reglas
    for regla in reglas:
        regla.validar()
    
    return reglas


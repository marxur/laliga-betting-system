"""
Reglas personalizadas del usuario
Estrategias basadas en patrones de medio tiempo y segunda mitad
"""

from src.rules.base import Regla


def crear_reglas_personalizadas():
    """
    Crea reglas personalizadas basadas en estrategias del usuario
    
    Returns:
        Lista de reglas personalizadas
    """
    
    reglas = []
    
    # ========================================
    # 1. UNDER 2.5 CON 0-0 AL DESCANSO
    # ========================================
    reglas.append(Regla(
        nombre="Under25_Si_0-0_HT",
        descripcion="Under 2.5 cuando el partido va 0-0 al descanso",
        condicion=lambda p: (
            p.get('HT_Home', 0) == 0 and 
            p.get('HT_Away', 0) == 0
        ),
        tipo_apuesta="Under 2.5",
        confianza_esperada=0.65,
        activa=True
    ))
    
    # ========================================
    # 2. FAVORITO MANTIENE VENTAJA
    # ========================================
    reglas.append(Regla(
        nombre="Favorito_Mantiene_Ventaja",
        descripcion="El favorito que gana al descanso seguirá ganando",
        condicion=lambda p: (
            # Favorito es local (cuota < 2.0)
            p.get('Cuota_Local', 999) < 2.0 and
            # Local gana al descanso
            p.get('HT_Home', 0) > p.get('HT_Away', 0)
        ) or (
            # Favorito es visitante (cuota < 2.5)
            p.get('Cuota_Visitante', 999) < 2.5 and
            # Visitante gana al descanso
            p.get('HT_Away', 0) > p.get('HT_Home', 0)
        ),
        tipo_apuesta="Favorito",
        confianza_esperada=0.75,
        activa=True
    ))
    
    # ========================================
    # 3. EQUIPOS GANANDO 1-0 AL DESCANSO
    # ========================================
    reglas.append(Regla(
        nombre="Ganando_1-0_HT_No_Pierde",
        descripcion="Equipos ganando 1-0 al descanso raramente pierden",
        condicion=lambda p: (
            # Local gana 1-0 al descanso
            (p.get('HT_Home', 0) == 1 and p.get('HT_Away', 0) == 0) or
            # Visitante gana 0-1 al descanso
            (p.get('HT_Home', 0) == 0 and p.get('HT_Away', 0) == 1)
        ),
        tipo_apuesta="Doble Chance (ganador HT)",
        confianza_esperada=0.80,
        activa=True
    ))
    
    # ========================================
    # 4. GOL EN 2ª MITAD - EQUIPOS GRANDES
    # ========================================
    equipos_grandes = [
        'Barcelona', 'Real Madrid', 'Sevilla', 'Granada', 'Valencia',
        'FC Barcelona', 'Real Madrid CF', 'Sevilla FC', 'Granada CF', 'Valencia CF'
    ]
    
    reglas.append(Regla(
        nombre="Gol_2H_Equipos_Grandes",
        descripcion="Barcelona, Real Madrid, Sevilla, Granada, Valencia marcan en 2H",
        condicion=lambda p: (
            any(equipo in p.get('Local', '') for equipo in equipos_grandes) or
            any(equipo in p.get('Visitante', '') for equipo in equipos_grandes)
        ),
        tipo_apuesta="Gol en 2H",
        confianza_esperada=0.70,
        activa=True
    ))
    
    # ========================================
    # 5. GOL EN 2H DESPUÉS DE GOL EN 1H
    # ========================================
    reglas.append(Regla(
        nombre="Gol_2H_Si_Gol_1H",
        descripcion="Si hay gol en 1H, habrá gol en 2H",
        condicion=lambda p: (
            # Hubo al menos 1 gol en primera mitad
            (p.get('HT_Home', 0) + p.get('HT_Away', 0)) >= 1
        ),
        tipo_apuesta="Gol en 2H",
        confianza_esperada=0.68,
        activa=True
    ))
    
    # ========================================
    # 6. OVER 2.5 CON 2+ GOLES EN 1H
    # ========================================
    reglas.append(Regla(
        nombre="Over25_Si_2Goles_HT",
        descripcion="Over 2.5 si hay 2 o más goles al descanso",
        condicion=lambda p: (
            (p.get('HT_Home', 0) + p.get('HT_Away', 0)) >= 2
        ),
        tipo_apuesta="Over 2.5",
        confianza_esperada=0.72,
        activa=True
    ))
    
    return reglas


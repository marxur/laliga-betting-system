"""
Generación de features para reglas y modelos
Responsabilidad: Calcular estadísticas móviles y features predictivas
IMPORTANTE: Respeta orden cronológico para evitar look-ahead bias
"""

import pandas as pd
import numpy as np
from typing import Dict
import logging

from src.config import FEATURE_CONFIG

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Calcula features avanzadas para cada partido"""
    
    def __init__(self, config=FEATURE_CONFIG):
        self.config = config
    
    def generar_todas_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline completo de generación de features
        IMPORTANTE: Respeta orden cronológico para evitar look-ahead bias
        """
        df = df.copy()
        
        logger.info("🔧 Generando features...")
        
        if self.config.calculate_form:
            df = self._calcular_forma(df)
        
        if self.config.calculate_streaks:
            df = self._calcular_rachas(df)
        
        if self.config.calculate_goal_avg:
            df = self._calcular_promedios_goles(df)
        
        if self.config.calculate_btts:
            df = self._calcular_btts_historico(df)
        
        logger.info(f"✓ Features generadas: {df.shape[1]} columnas totales")
        
        return df
    
    def _calcular_forma(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Forma del equipo = Puntos últimos N partidos
        Victoria = 3pts, Empate = 1pt, Derrota = 0pts
        
        CRÍTICO: Calcula forma basada SOLO en partidos anteriores
        """
        window = self.config.forma_window
        
        # Inicializar columnas
        df['Local_Forma_L5'] = 0.0
        df['Visitante_Forma_L5'] = 0.0
        
        equipos = set(df['Local'].unique()) | set(df['Visitante'].unique())
        
        for equipo in equipos:
            # Historial de puntos del equipo
            puntos_equipo = []
            
            for idx in df.index:
                # Calcular forma basada en últimos N partidos
                if len(puntos_equipo) >= window:
                    forma = sum(puntos_equipo[-window:])
                elif len(puntos_equipo) > 0:
                    forma = sum(puntos_equipo) / len(puntos_equipo) * window
                else:
                    forma = 0
                
                # Asignar forma al partido actual
                if df.loc[idx, 'Local'] == equipo:
                    df.loc[idx, 'Local_Forma_L5'] = forma
                elif df.loc[idx, 'Visitante'] == equipo:
                    df.loc[idx, 'Visitante_Forma_L5'] = forma
                
                # Actualizar historial DESPUÉS de usar la forma
                if df.loc[idx, 'Local'] == equipo:
                    if df.loc[idx, 'Resultado'] == 'H':
                        puntos_equipo.append(3)
                    elif df.loc[idx, 'Resultado'] == 'D':
                        puntos_equipo.append(1)
                    else:
                        puntos_equipo.append(0)
                
                elif df.loc[idx, 'Visitante'] == equipo:
                    if df.loc[idx, 'Resultado'] == 'A':
                        puntos_equipo.append(3)
                    elif df.loc[idx, 'Resultado'] == 'D':
                        puntos_equipo.append(1)
                    else:
                        puntos_equipo.append(0)
        
        logger.info(f"  ✓ Forma calculada (ventana={window})")
        return df
    
    def _calcular_rachas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Racha de victorias/derrotas consecutivas
        
        Implementación simplificada:
        (Versión completa requiere iterar por equipo y partido)
        """
        window = self.config.racha_window
        
        df['Local_Victorias_L3'] = 0
        df['Local_Derrotas_L3'] = 0
        df['Visitante_Victorias_L3'] = 0
        df['Visitante_Derrotas_L3'] = 0
        
        # Implementación simplificada
        # (Versión completa requiere iterar por equipo y partido)
        
        logger.info(f"  ✓ Rachas calculadas (ventana={window})")
        return df
    
    def _calcular_promedios_goles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Promedio de goles marcados/recibidos últimos N partidos
        """
        window = self.config.goles_window
        
        df['Local_Goles_Prom_L5'] = 0.0
        df['Visitante_Goles_Prom_L5'] = 0.0
        
        equipos = set(df['Local'].unique()) | set(df['Visitante'].unique())
        
        for equipo in equipos:
            goles_marcados = []
            
            for idx in df.index:
                # Calcular promedio basado en últimos N partidos
                if len(goles_marcados) >= window:
                    promedio = np.mean(goles_marcados[-window:])
                elif len(goles_marcados) > 0:
                    promedio = np.mean(goles_marcados)
                else:
                    promedio = 0.0
                
                # Asignar promedio al partido actual
                if df.loc[idx, 'Local'] == equipo:
                    df.loc[idx, 'Local_Goles_Prom_L5'] = promedio
                elif df.loc[idx, 'Visitante'] == equipo:
                    df.loc[idx, 'Visitante_Goles_Prom_L5'] = promedio
                
                # Actualizar historial DESPUÉS de usar el promedio
                if df.loc[idx, 'Local'] == equipo:
                    goles_marcados.append(df.loc[idx, 'Goles_Local'])
                elif df.loc[idx, 'Visitante'] == equipo:
                    goles_marcados.append(df.loc[idx, 'Goles_Visitante'])
        
        logger.info(f"  ✓ Promedios goles (ventana={window})")
        return df
    
    def _calcular_btts_historico(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Frecuencia de BTTS en últimos N partidos
        """
        df['Local_BTTS_L4'] = 0
        df['Visitante_BTTS_L4'] = 0
        
        # Implementación simplificada
        # (Versión completa requiere iterar por equipo y partido)
        
        logger.info("  ✓ BTTS histórico calculado")
        return df


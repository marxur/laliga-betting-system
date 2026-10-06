"""
Generación de features para reglas y modelos.
Solo usa partidos anteriores del mismo equipo: no hay look-ahead.
"""

import pandas as pd
import numpy as np
from typing import List
import logging

from src.config import FEATURE_CONFIG

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Calcula features con historial previo al partido."""

    def __init__(self, config=FEATURE_CONFIG):
        self.config = config

    def generar_todas_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if 'Date' in df.columns:
            df = df.sort_values('Date').reset_index(drop=True)

        logger.info("Generando features...")
        if self.config.calculate_form:
            df = self._calcular_forma(df)
        if self.config.calculate_streaks:
            df = self._calcular_rachas(df)
        if self.config.calculate_goal_avg:
            df = self._calcular_promedios_goles(df)
        if self.config.calculate_btts:
            df = self._calcular_btts_historico(df)

        logger.info(f"Features generadas: {df.shape[1]} columnas")
        return df

    def _equipos(self, df: pd.DataFrame):
        return set(df['Local'].dropna().unique()) | set(df['Visitante'].dropna().unique())

    def _resultado_equipo(self, fila, equipo) -> str:
        if fila['Local'] == equipo:
            if fila['Resultado'] == 'H':
                return 'W'
            if fila['Resultado'] == 'D':
                return 'D'
            return 'L'
        if fila['Resultado'] == 'A':
            return 'W'
        if fila['Resultado'] == 'D':
            return 'D'
        return 'L'

    def _puntos(self, marca: str) -> int:
        return {'W': 3, 'D': 1, 'L': 0}[marca]

    def _calcular_forma(self, df: pd.DataFrame) -> pd.DataFrame:
        """Puntos reales de los últimos N partidos. No se extrapola la ventana corta."""
        window = self.config.forma_window
        df['Local_Forma_L5'] = 0.0
        df['Visitante_Forma_L5'] = 0.0

        for equipo in self._equipos(df):
            puntos: List[int] = []
            for idx in df.index:
                fila = df.loc[idx]
                if fila['Local'] != equipo and fila['Visitante'] != equipo:
                    continue
                forma = float(sum(puntos[-window:]))
                if fila['Local'] == equipo:
                    df.loc[idx, 'Local_Forma_L5'] = forma
                else:
                    df.loc[idx, 'Visitante_Forma_L5'] = forma
                puntos.append(self._puntos(self._resultado_equipo(fila, equipo)))

        logger.info(f"Forma calculada (ventana={window}, sin extrapolar)")
        return df

    def _calcular_rachas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Victorias y derrotas en los últimos N, más racha vigente de victorias."""
        window = self.config.racha_window
        for col in (
            'Local_Victorias_L3',
            'Local_Derrotas_L3',
            'Visitante_Victorias_L3',
            'Visitante_Derrotas_L3',
            'Local_Racha_Victorias',
            'Visitante_Racha_Victorias',
        ):
            df[col] = 0

        for equipo in self._equipos(df):
            marcas: List[str] = []
            for idx in df.index:
                fila = df.loc[idx]
                if fila['Local'] != equipo and fila['Visitante'] != equipo:
                    continue
                ultimos = marcas[-window:]
                victorias = sum(m == 'W' for m in ultimos)
                derrotas = sum(m == 'L' for m in ultimos)
                racha = 0
                for marca in reversed(marcas):
                    if marca != 'W':
                        break
                    racha += 1
                if fila['Local'] == equipo:
                    df.loc[idx, 'Local_Victorias_L3'] = victorias
                    df.loc[idx, 'Local_Derrotas_L3'] = derrotas
                    df.loc[idx, 'Local_Racha_Victorias'] = racha
                else:
                    df.loc[idx, 'Visitante_Victorias_L3'] = victorias
                    df.loc[idx, 'Visitante_Derrotas_L3'] = derrotas
                    df.loc[idx, 'Visitante_Racha_Victorias'] = racha
                marcas.append(self._resultado_equipo(fila, equipo))

        logger.info(f"Rachas calculadas (ventana={window})")
        return df

    def _calcular_promedios_goles(self, df: pd.DataFrame) -> pd.DataFrame:
        window = self.config.goles_window
        df['Local_Goles_Prom_L5'] = 0.0
        df['Visitante_Goles_Prom_L5'] = 0.0

        for equipo in self._equipos(df):
            goles: List[float] = []
            for idx in df.index:
                fila = df.loc[idx]
                if fila['Local'] != equipo and fila['Visitante'] != equipo:
                    continue
                promedio = float(np.mean(goles[-window:])) if goles else 0.0
                if fila['Local'] == equipo:
                    df.loc[idx, 'Local_Goles_Prom_L5'] = promedio
                    goles.append(float(fila['Goles_Local']))
                else:
                    df.loc[idx, 'Visitante_Goles_Prom_L5'] = promedio
                    goles.append(float(fila['Goles_Visitante']))

        logger.info(f"Promedios de goles (ventana={window})")
        return df

    def _calcular_btts_historico(self, df: pd.DataFrame) -> pd.DataFrame:
        """Partidos con ambos equipos marcando en los últimos 4 del equipo."""
        window = 4
        df['Local_BTTS_L4'] = 0
        df['Visitante_BTTS_L4'] = 0

        for equipo in self._equipos(df):
            historial: List[int] = []
            for idx in df.index:
                fila = df.loc[idx]
                if fila['Local'] != equipo and fila['Visitante'] != equipo:
                    continue
                n = int(sum(historial[-window:]))
                if fila['Local'] == equipo:
                    df.loc[idx, 'Local_BTTS_L4'] = n
                else:
                    df.loc[idx, 'Visitante_BTTS_L4'] = n
                ambos = float(fila['Goles_Local']) > 0 and float(fila['Goles_Visitante']) > 0
                historial.append(1 if ambos else 0)

        logger.info("BTTS histórico calculado (ventana=4)")
        return df

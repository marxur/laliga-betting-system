"""
Limpieza y estandarización de datos
Responsabilidad: Transformar datos crudos en formato consistente
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Limpia y estandariza datos de football-data.co.uk"""

    @staticmethod
    def limpiar(df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline completo de limpieza

        Args:
            df: DataFrame crudo

        Returns:
            DataFrame limpio y estandarizado
        """
        df = df.copy()

        # 1. Convertir fechas
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')

        # 2. Filtrar partidos incompletos
        columnas_requeridas = ['FTHG', 'FTAG', 'FTR']
        df = df.dropna(subset=columnas_requeridas)

        # 3. Ordenar cronológicamente (CRÍTICO para backtest)
        df = df.sort_values('Date').reset_index(drop=True)

        # 4. Renombrar columnas a español estándar
        df = DataCleaner._renombrar_columnas(df)

        # 5. Validar tipos de datos
        df = DataCleaner._validar_tipos(df)

        # 6. Añadir metadata útil
        df = DataCleaner._añadir_metadata(df)

        logger.info(f"Datos limpiados: {len(df)} partidos válidos")

        return df

    @staticmethod
    def _renombrar_columnas(df: pd.DataFrame) -> pd.DataFrame:
        """Renombra columnas a nombres estándar."""
        renombrado = {
            'HomeTeam': 'Local',
            'AwayTeam': 'Visitante',
            'FTHG': 'Goles_Local',
            'FTAG': 'Goles_Visitante',
            'FTR': 'Resultado',
            'B365H': 'Cuota_Local',
            'B365D': 'Cuota_Empate',
            'B365A': 'Cuota_Visitante',
            'HTHG': 'Goles_Local_HT',
            'HTAG': 'Goles_Visitante_HT',
            'HTR': 'Resultado_HT',
            'HS': 'Tiros_Local',
            'AS': 'Tiros_Visitante',
            'HST': 'Tiros_Puerta_Local',
            'AST': 'Tiros_Puerta_Visitante',
            # Over/Under 2.5. Sin esto el motor no puede liquidar Over.
            'B365>2.5': 'Cuota_Over_25',
            'B365<2.5': 'Cuota_Under_25',
            'Avg>2.5': 'Cuota_Over_25_Avg',
            'Avg<2.5': 'Cuota_Under_25_Avg',
            'BbAv>2.5': 'Cuota_Over_25_Avg',
            'BbAv<2.5': 'Cuota_Under_25_Avg',
            'Max>2.5': 'Cuota_Over_25_Max',
            'Max<2.5': 'Cuota_Under_25_Max',
            'P>2.5': 'Cuota_Over_25_Pinnacle',
            'P<2.5': 'Cuota_Under_25_Pinnacle',
        }

        renombrado = {k: v for k, v in renombrado.items() if k in df.columns}
        return df.rename(columns=renombrado)

    @staticmethod
    def _validar_tipos(df: pd.DataFrame) -> pd.DataFrame:
        """Asegura tipos de datos correctos."""
        columnas_goles = ['Goles_Local', 'Goles_Visitante']
        for col in columnas_goles:
            if col in df.columns:
                df[col] = df[col].astype(int)

        columnas_cuotas = [
            'Cuota_Local',
            'Cuota_Empate',
            'Cuota_Visitante',
            'Cuota_Over_25',
            'Cuota_Under_25',
            'Cuota_Over_25_Avg',
            'Cuota_Under_25_Avg',
            'Cuota_Over_25_Max',
            'Cuota_Under_25_Max',
            'Cuota_Over_25_Pinnacle',
            'Cuota_Under_25_Pinnacle',
            'Cuota_BTTS',
        ]
        for col in columnas_cuotas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    @staticmethod
    def _añadir_metadata(df: pd.DataFrame) -> pd.DataFrame:
        """Añade columnas de metadata útil."""
        df['Año'] = df['Date'].dt.year
        df['Mes'] = df['Date'].dt.month
        df['Dia_Semana'] = df['Date'].dt.dayofweek
        if 'Temporada' in df.columns:
            df['Jornada'] = df.groupby('Temporada').cumcount() + 1
        df['BTTS'] = (df['Goles_Local'] > 0) & (df['Goles_Visitante'] > 0)
        df['Total_Goles'] = df['Goles_Local'] + df['Goles_Visitante']
        df['Margen'] = abs(df['Goles_Local'] - df['Goles_Visitante'])
        return df

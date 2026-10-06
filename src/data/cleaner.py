"""
Limpieza y estandarización de datos.
No crea columnas duplicadas si dos fuentes de cuota comparten destino.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Limpia y estandariza datos de football-data.co.uk."""

    @staticmethod
    def limpiar(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Date'])
        df = df.dropna(subset=['FTHG', 'FTAG', 'FTR'])
        df = df.sort_values('Date').reset_index(drop=True)
        df = DataCleaner._renombrar_columnas(df)
        df = DataCleaner._validar_tipos(df)
        df = DataCleaner._anadir_metadata(df)
        logger.info(f"Datos limpiados: {len(df)} partidos válidos")
        return df

    @staticmethod
    def _renombrar_columnas(df: pd.DataFrame) -> pd.DataFrame:
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
            'B365CH': 'Cuota_Local_Cierre',
            'B365CD': 'Cuota_Empate_Cierre',
            'B365CA': 'Cuota_Visitante_Cierre',
            'B365C>2.5': 'Cuota_Over_25_Cierre',
            'B365C<2.5': 'Cuota_Under_25_Cierre',
        }
        out = df.copy()
        for src, dst in renombrado.items():
            if src not in out.columns:
                continue
            if dst in out.columns:
                out = out.drop(columns=[src])
                continue
            out = out.rename(columns={src: dst})
        return out

    @staticmethod
    def _validar_tipos(df: pd.DataFrame) -> pd.DataFrame:
        for col in ('Goles_Local', 'Goles_Visitante'):
            if col in df.columns:
                df[col] = df[col].astype(int)
        columnas_cuotas = [
            'Cuota_Local', 'Cuota_Empate', 'Cuota_Visitante',
            'Cuota_Over_25', 'Cuota_Under_25',
            'Cuota_Over_25_Avg', 'Cuota_Under_25_Avg',
            'Cuota_Over_25_Max', 'Cuota_Under_25_Max',
            'Cuota_Over_25_Pinnacle', 'Cuota_Under_25_Pinnacle',
            'Cuota_Local_Cierre', 'Cuota_Empate_Cierre', 'Cuota_Visitante_Cierre',
            'Cuota_Over_25_Cierre', 'Cuota_Under_25_Cierre', 'Cuota_BTTS',
        ]
        for col in columnas_cuotas:
            if col not in df.columns:
                continue
            serie = df[col]
            if isinstance(serie, pd.DataFrame):
                serie = serie.iloc[:, 0]
            df[col] = pd.to_numeric(serie, errors='coerce')
        return df

    @staticmethod
    def _anadir_metadata(df: pd.DataFrame) -> pd.DataFrame:
        df['Año'] = df['Date'].dt.year
        df['Mes'] = df['Date'].dt.month
        df['Dia_Semana'] = df['Date'].dt.dayofweek
        if 'Temporada' in df.columns:
            df['Jornada'] = df.groupby('Temporada').cumcount() + 1
        df['BTTS'] = (df['Goles_Local'] > 0) & (df['Goles_Visitante'] > 0)
        df['Total_Goles'] = df['Goles_Local'] + df['Goles_Visitante']
        df['Margen'] = abs(df['Goles_Local'] - df['Goles_Visitante'])
        return df

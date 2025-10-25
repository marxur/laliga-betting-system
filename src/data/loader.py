"""
Descarga y carga de datos desde football-data.co.uk
Responsabilidad: Obtener datos crudos y guardarlos
"""

import pandas as pd
import requests
from pathlib import Path
from typing import List, Optional
import logging

from src.config import DATA_CONFIG

logger = logging.getLogger(__name__)


class LaLigaLoader:
    """Descarga y carga datos de La Liga"""
    
    def __init__(self, config=DATA_CONFIG):
        self.config = config
        self.config.raw_dir.mkdir(parents=True, exist_ok=True)
    
    def descargar_temporada(self, temporada: str) -> Optional[Path]:
        """
        Descarga CSV de una temporada
        
        Args:
            temporada: Código de temporada (ej: '2324' para 2023-24)
        
        Returns:
            Path al archivo descargado o None si falla
        """
        url = f"{self.config.base_url}{temporada}/{self.config.liga_code}.csv"
        filepath = self.config.raw_dir / f"{self.config.liga_code}_{temporada}.csv"
        
        if filepath.exists():
            logger.info(f"✓ Temporada {temporada} ya existe")
            return filepath
        
        try:
            logger.info(f"⬇ Descargando temporada {temporada}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✓ Descargada: {filepath.name}")
            return filepath
            
        except Exception as e:
            logger.error(f"✗ Error descargando {temporada}: {e}")
            return None
    
    def cargar_temporada(self, temporada: str) -> Optional[pd.DataFrame]:
        """Carga una temporada ya descargada"""
        filepath = self.config.raw_dir / f"{self.config.liga_code}_{temporada}.csv"
        
        if not filepath.exists():
            logger.warning(f"Archivo no existe: {filepath}")
            return None
        
        try:
            df = pd.read_csv(filepath, encoding='latin1')
            df['Temporada'] = f"20{temporada[:2]}-{temporada[2:]}"
            return df
        except Exception as e:
            logger.error(f"Error cargando {filepath}: {e}")
            return None
    
    def cargar_todas_temporadas(self) -> pd.DataFrame:
        """
        Descarga y carga todas las temporadas configuradas
        
        Returns:
            DataFrame con todos los datos históricos
        """
        dfs = []
        
        for temporada in self.config.temporadas:
            # Intentar descargar si no existe
            self.descargar_temporada(temporada)
            
            # Cargar
            df = self.cargar_temporada(temporada)
            if df is not None:
                dfs.append(df)
        
        if not dfs:
            raise ValueError("No se pudieron cargar datos")
        
        df_completo = pd.concat(dfs, ignore_index=True)
        logger.info(f"✓ Cargados {len(df_completo)} partidos de {len(dfs)} temporadas")
        
        return df_completo
    
    def guardar_procesado(self, df: pd.DataFrame, nombre: str = "laliga_completo"):
        """Guarda dataset procesado en formato Parquet"""
        self.config.processed_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.config.processed_dir / f"{nombre}.parquet"
        
        df.to_parquet(filepath, engine='pyarrow', index=False)
        logger.info(f"💾 Guardado: {filepath} ({len(df)} partidos)")
        
        return filepath
    
    def cargar_procesado(self, nombre: str = "laliga_completo") -> pd.DataFrame:
        """Carga dataset procesado desde Parquet"""
        filepath = self.config.processed_dir / f"{nombre}.parquet"
        
        if not filepath.exists():
            raise FileNotFoundError(f"No existe: {filepath}")
        
        df = pd.read_parquet(filepath)
        logger.info(f"📂 Cargado: {filepath.name} ({len(df)} partidos)")
        
        return df


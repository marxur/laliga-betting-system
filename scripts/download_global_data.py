"""
Script para descargar datos históricos de múltiples ligas
desde Football-Data.co.uk
"""

import requests
import pandas as pd
from pathlib import Path
import time

# Configuración de ligas y temporadas
LIGAS = {
    # Europa Principal
    'E0': 'Premier League',
    'E1': 'Championship',
    'SP1': 'La Liga',
    'SP2': 'La Liga 2',
    'D1': 'Bundesliga',
    'D2': 'Bundesliga 2',
    'I1': 'Serie A',
    'I2': 'Serie B',
    'F1': 'Ligue 1',
    'F2': 'Ligue 2',
    'N1': 'Eredivisie',
    'P1': 'Liga Portugal',
    'B1': 'Jupiler League',
    'T1': 'Super Lig',
    'G1': 'Super League Greece',
    
    # Sudamérica
    'ARG': 'Primera Division Argentina',
    'BRA': 'Serie A Brasil',
    
    # Otros
    'SC0': 'Scottish Premiership',
    'MX1': 'Liga MX',
    'USA': 'MLS'
}

# Temporadas a descargar (últimas 7 temporadas)
TEMPORADAS = [
    '1819', '1920', '2021', '2122', '2223', '2324', '2425'
]

BASE_URL = 'https://www.football-data.co.uk/mmz4281'


def descargar_liga_temporada(liga_code: str, temporada: str, output_dir: Path) -> bool:
    """
    Descarga datos de una liga y temporada específica
    
    Args:
        liga_code: Código de la liga (ej: 'E0', 'SP1')
        temporada: Código de temporada (ej: '2425')
        output_dir: Directorio de salida
    
    Returns:
        True si se descargó exitosamente
    """
    url = f"{BASE_URL}/{temporada}/{liga_code}.csv"
    
    try:
        print(f"  Descargando {liga_code} {temporada}...", end=" ")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Guardar CSV
            filename = output_dir / f"{liga_code}_{temporada}.csv"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print("✅")
            return True
        else:
            print(f"❌ (HTTP {response.status_code})")
            return False
    
    except Exception as e:
        print(f"❌ ({str(e)})")
        return False


def descargar_todas_las_ligas():
    """
    Descarga datos de todas las ligas configuradas
    """
    output_dir = Path(__file__).parent.parent / 'data' / 'global'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("📥 DESCARGA DE DATOS GLOBALES")
    print("="*70)
    print(f"\nLigas a descargar: {len(LIGAS)}")
    print(f"Temporadas por liga: {len(TEMPORADAS)}")
    print(f"Total archivos: {len(LIGAS) * len(TEMPORADAS)}\n")
    
    exitosos = 0
    fallidos = 0
    
    for liga_code, liga_nombre in LIGAS.items():
        print(f"\n🏆 {liga_nombre} ({liga_code})")
        
        for temporada in TEMPORADAS:
            if descargar_liga_temporada(liga_code, temporada, output_dir):
                exitosos += 1
            else:
                fallidos += 1
            
            # Pausa para no saturar el servidor
            time.sleep(0.5)
    
    print("\n" + "="*70)
    print("📊 RESUMEN DE DESCARGA")
    print("="*70)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"📁 Directorio: {output_dir}")
    print("="*70 + "\n")


def consolidar_datos():
    """
    Consolida todos los CSVs descargados en un solo DataFrame
    """
    data_dir = Path(__file__).parent.parent / 'data' / 'global'
    
    if not data_dir.exists():
        print("❌ No hay datos descargados")
        return None
    
    print("\n📊 Consolidando datos...")
    
    all_dfs = []
    csv_files = list(data_dir.glob('*.csv'))
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='latin-1', on_bad_lines='skip')
            
            # Extraer liga y temporada del nombre del archivo
            parts = csv_file.stem.split('_')
            liga_code = parts[0]
            temporada = parts[1] if len(parts) > 1 else 'unknown'
            
            # Añadir columnas de metadatos
            df['Liga_Code'] = liga_code
            df['Liga_Nombre'] = LIGAS.get(liga_code, 'Unknown')
            df['Temporada'] = temporada
            
            all_dfs.append(df)
            
        except Exception as e:
            print(f"  ⚠️ Error leyendo {csv_file.name}: {e}")
    
    if not all_dfs:
        print("❌ No se pudieron leer datos")
        return None
    
    # Concatenar todos los DataFrames
    df_global = pd.concat(all_dfs, ignore_index=True)
    
    # Guardar consolidado
    output_file = data_dir.parent / 'processed' / 'global_consolidated.parquet'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_global.to_parquet(output_file, index=False)
    
    print(f"✅ Datos consolidados: {len(df_global)} partidos")
    print(f"✅ Guardado en: {output_file}")
    
    return df_global


if __name__ == '__main__':
    # Descargar datos
    descargar_todas_las_ligas()
    
    # Consolidar
    df = consolidar_datos()
    
    if df is not None:
        print(f"\n📊 Resumen:")
        print(f"  Total partidos: {len(df)}")
        print(f"  Ligas únicas: {df['Liga_Nombre'].nunique()}")
        print(f"  Temporadas: {df['Temporada'].nunique()}")


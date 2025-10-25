"""
Análisis global de la estrategia "Ganando 1-0 al Descanso"
Evalúa el rendimiento en múltiples ligas del mundo
"""

import pandas as pd
import glob
from pathlib import Path
from collections import defaultdict

# Mapeo de códigos de liga a nombres
LIGAS_NOMBRES = {
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
    'ARG': 'Primera Division Argentina',
    'BRA': 'Serie A Brasil',
    'SC0': 'Scottish Premiership',
    'MX1': 'Liga MX',
    'USA': 'MLS'
}


def cargar_datos_globales():
    """
    Carga todos los CSVs descargados
    """
    data_dir = Path(__file__).parent.parent / 'data' / 'global'
    csv_files = list(data_dir.glob('*.csv'))
    
    print(f"📂 Cargando {len(csv_files)} archivos...")
    
    all_data = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='latin-1', on_bad_lines='skip')
            
            # Extraer metadatos del nombre del archivo
            parts = csv_file.stem.split('_')
            liga_code = parts[0]
            temporada = parts[1] if len(parts) > 1 else 'unknown'
            
            # Verificar que tiene datos de medio tiempo
            if 'HTHG' not in df.columns or 'HTAG' not in df.columns:
                continue
            
            # Añadir metadatos
            df['Liga_Code'] = liga_code
            df['Liga_Nombre'] = LIGAS_NOMBRES.get(liga_code, liga_code)
            df['Temporada'] = temporada
            
            all_data.append(df)
            
        except Exception as e:
            print(f"  ⚠️ Error en {csv_file.name}: {e}")
    
    if not all_data:
        return None
    
    df_global = pd.concat(all_data, ignore_index=True)
    
    print(f"✅ {len(df_global)} partidos cargados de {df_global['Liga_Nombre'].nunique()} ligas")
    
    return df_global


def analizar_estrategia_1_0_ht(df):
    """
    Analiza la estrategia "Ganando 1-0 al Descanso No Pierde"
    """
    print("\n" + "="*70)
    print("🎯 ANÁLISIS GLOBAL: Ganando 1-0 al Descanso No Pierde")
    print("="*70 + "\n")
    
    # Filtrar partidos donde alguien ganaba 1-0 al descanso
    df_1_0_ht = df[
        ((df['HTHG'] == 1) & (df['HTAG'] == 0)) |  # Local 1-0
        ((df['HTHG'] == 0) & (df['HTAG'] == 1))    # Visitante 0-1
    ].copy()
    
    print(f"📊 Partidos con 1-0 al descanso: {len(df_1_0_ht)}")
    print(f"📊 Total de partidos analizados: {len(df)}")
    print(f"📊 Porcentaje: {len(df_1_0_ht)/len(df)*100:.2f}%\n")
    
    # Determinar si el ganador al descanso no perdió
    def no_perdio(row):
        if row['HTHG'] == 1 and row['HTAG'] == 0:
            # Local ganaba 1-0
            return row['FTHG'] >= row['FTAG']  # No perdió si empató o ganó
        elif row['HTHG'] == 0 and row['HTAG'] == 1:
            # Visitante ganaba 0-1
            return row['FTAG'] >= row['FTHG']  # No perdió si empató o ganó
        return False
    
    df_1_0_ht['No_Perdio'] = df_1_0_ht.apply(no_perdio, axis=1)
    
    # Análisis global
    total_partidos = len(df_1_0_ht)
    aciertos = df_1_0_ht['No_Perdio'].sum()
    win_rate = (aciertos / total_partidos * 100) if total_partidos > 0 else 0
    
    # ROI asumiendo cuota promedio de 1.20 para doble chance
    cuota_promedio = 1.20
    roi = ((aciertos * cuota_promedio - total_partidos) / total_partidos * 100) if total_partidos > 0 else 0
    
    print("="*70)
    print("📈 RESULTADOS GLOBALES")
    print("="*70)
    print(f"Partidos analizados: {total_partidos:,}")
    print(f"Aciertos: {aciertos:,}")
    print(f"Fallos: {total_partidos - aciertos:,}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"ROI (cuota 1.20): {roi:+.2f}%")
    print("="*70 + "\n")
    
    # Análisis por liga
    print("="*70)
    print("📊 RESULTADOS POR LIGA")
    print("="*70 + "\n")
    
    resultados_por_liga = []
    
    for liga in df_1_0_ht['Liga_Nombre'].unique():
        df_liga = df_1_0_ht[df_1_0_ht['Liga_Nombre'] == liga]
        
        total = len(df_liga)
        aciertos_liga = df_liga['No_Perdio'].sum()
        wr_liga = (aciertos_liga / total * 100) if total > 0 else 0
        roi_liga = ((aciertos_liga * cuota_promedio - total) / total * 100) if total > 0 else 0
        
        resultados_por_liga.append({
            'Liga': liga,
            'Partidos': total,
            'Aciertos': aciertos_liga,
            'Win_Rate': wr_liga,
            'ROI': roi_liga
        })
    
    # Ordenar por número de partidos
    resultados_por_liga = sorted(resultados_por_liga, key=lambda x: x['Partidos'], reverse=True)
    
    # Mostrar top 15
    print("Top 15 ligas por volumen:\n")
    for i, resultado in enumerate(resultados_por_liga[:15], 1):
        print(f"{i:2d}. {resultado['Liga']:30s} | {resultado['Partidos']:4d} partidos | "
              f"WR: {resultado['Win_Rate']:5.1f}% | ROI: {resultado['ROI']:+6.1f}%")
    
    # Análisis por región
    print("\n" + "="*70)
    print("🌍 RESULTADOS POR REGIÓN")
    print("="*70 + "\n")
    
    regiones = {
        'Inglaterra': ['Premier League', 'Championship'],
        'España': ['La Liga', 'La Liga 2'],
        'Alemania': ['Bundesliga', 'Bundesliga 2'],
        'Italia': ['Serie A', 'Serie B'],
        'Francia': ['Ligue 1', 'Ligue 2'],
        'Sudamérica': ['Primera Division Argentina', 'Serie A Brasil'],
        'Otros Europa': ['Eredivisie', 'Liga Portugal', 'Jupiler League', 'Scottish Premiership']
    }
    
    for region, ligas in regiones.items():
        df_region = df_1_0_ht[df_1_0_ht['Liga_Nombre'].isin(ligas)]
        
        if len(df_region) == 0:
            continue
        
        total_region = len(df_region)
        aciertos_region = df_region['No_Perdio'].sum()
        wr_region = (aciertos_region / total_region * 100) if total_region > 0 else 0
        roi_region = ((aciertos_region * cuota_promedio - total_region) / total_region * 100) if total_region > 0 else 0
        
        print(f"{region:20s} | {total_region:5d} partidos | "
              f"WR: {wr_region:5.1f}% | ROI: {roi_region:+6.1f}%")
    
    # Guardar resultados
    df_resultados = pd.DataFrame(resultados_por_liga)
    output_file = Path(__file__).parent.parent / 'outputs' / 'reports' / 'estrategia_1-0_ht_global.csv'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_resultados.to_csv(output_file, index=False)
    
    print(f"\n✅ Resultados guardados en: {output_file}")
    
    # Conclusiones
    print("\n" + "="*70)
    print("💡 CONCLUSIONES")
    print("="*70)
    
    if win_rate >= 85:
        print("✅ La estrategia es ROBUSTA a nivel global")
        print(f"✅ Win rate de {win_rate:.1f}% supera el 85%")
    elif win_rate >= 80:
        print("⚠️  La estrategia es BUENA pero con variaciones")
        print(f"⚠️  Win rate de {win_rate:.1f}% está entre 80-85%")
    else:
        print("❌ La estrategia tiene rendimiento VARIABLE")
        print(f"❌ Win rate de {win_rate:.1f}% es inferior al 80%")
    
    if roi > 10:
        print(f"✅ ROI de {roi:+.1f}% es EXCELENTE")
    elif roi > 5:
        print(f"⚠️  ROI de {roi:+.1f}% es ACEPTABLE")
    else:
        print(f"❌ ROI de {roi:+.1f}% es BAJO")
    
    print("\n" + "="*70 + "\n")
    
    return df_resultados


if __name__ == '__main__':
    # Cargar datos
    df = cargar_datos_globales()
    
    if df is None:
        print("❌ No se pudieron cargar datos")
        exit(1)
    
    # Analizar estrategia
    resultados = analizar_estrategia_1_0_ht(df)


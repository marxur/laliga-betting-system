"""
Script mejorado para backtest de reglas personalizadas
Carga datos directamente desde CSVs originales con datos de medio tiempo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import glob
from src.rules.custom_rules import crear_reglas_personalizadas
from src.backtest.validation import DataValidator
from datetime import datetime

def cargar_datos_originales():
    """
    Carga datos originales desde CSVs con datos de medio tiempo
    """
    print("📊 Cargando datos históricos de La Liga...")
    
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    csv_files = sorted(glob.glob(str(data_dir / 'SP1_*.csv')))
    
    if not csv_files:
        print("❌ No se encontraron archivos CSV")
        return None
    
    dfs = []
    for csv_file in csv_files:
        df_temp = pd.read_csv(csv_file)
        dfs.append(df_temp)
    
    df = pd.concat(dfs, ignore_index=True)
    
    # Renombrar columnas
    df = df.rename(columns={
        'HomeTeam': 'Local',
        'AwayTeam': 'Visitante',
        'FTHG': 'Goles_Local',
        'FTAG': 'Goles_Visitante',
        'FTR': 'Resultado',
        'HTHG': 'HT_Home',
        'HTAG': 'HT_Away',
        'HTR': 'Resultado_HT',
        'B365H': 'Cuota_Local',
        'B365D': 'Cuota_Empate',
        'B365A': 'Cuota_Visitante'
    })
    
    # Convertir fecha
    df['Fecha'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    
    # Limpiar datos
    df = df.dropna(subset=['HT_Home', 'HT_Away', 'Goles_Local', 'Goles_Visitante'])
    
    print(f"✅ Datos cargados: {len(df)} partidos")
    print(f"✅ Columnas de medio tiempo disponibles: HT_Home, HT_Away")
    
    return df


def calcular_resultado_regla(partido, regla):
    """
    Calcula si la regla acertó para un partido específico
    """
    tipo = regla.tipo_apuesta
    
    goles_home = partido.get('Goles_Local', 0)
    goles_away = partido.get('Goles_Visitante', 0)
    total_goles = goles_home + goles_away
    
    ht_home = partido.get('HT_Home', 0)
    ht_away = partido.get('HT_Away', 0)
    
    # Goles en segunda mitad
    goles_2h_home = goles_home - ht_home
    goles_2h_away = goles_away - ht_away
    goles_2h = goles_2h_home + goles_2h_away
    
    if tipo == "Under 2.5":
        return total_goles < 3
    
    elif tipo == "Over 2.5":
        return total_goles > 2
    
    elif tipo == "Favorito":
        # Determinar quién es favorito
        cuota_local = partido.get('Cuota_Local', 999)
        cuota_visitante = partido.get('Cuota_Visitante', 999)
        
        if cuota_local < cuota_visitante:
            # Local es favorito
            return goles_home > goles_away
        else:
            # Visitante es favorito
            return goles_away > goles_home
    
    elif tipo == "Doble Chance (ganador HT)":
        # El que ganaba al descanso no perdió
        if ht_home > ht_away:
            # Local ganaba, no debe perder
            return goles_home >= goles_away
        elif ht_away > ht_home:
            # Visitante ganaba, no debe perder
            return goles_away >= goles_home
        return None
    
    elif tipo == "Gol en 2H":
        return goles_2h > 0
    
    return None


def ejecutar_backtest():
    """
    Ejecuta backtest de reglas personalizadas
    """
    print("\n" + "="*70)
    print("🎯 BACKTEST DE REGLAS PERSONALIZADAS")
    print("="*70 + "\n")
    
    # Cargar datos
    df = cargar_datos_originales()
    
    if df is None or len(df) == 0:
        print("❌ No hay datos para analizar")
        return
    
    # Crear reglas personalizadas
    reglas = crear_reglas_personalizadas()
    
    print(f"📋 Reglas a evaluar: {len(reglas)}\n")
    
    # Split temporal
    fecha_corte = pd.to_datetime('2024-01-01')
    df_train = df[df['Fecha'] < fecha_corte].copy()
    df_test = df[df['Fecha'] >= fecha_corte].copy()
    
    print(f"📊 Datos de entrenamiento: {len(df_train)} partidos (hasta 2023)")
    print(f"📊 Datos de test: {len(df_test)} partidos (2024-2025)")
    print("\n" + "="*70 + "\n")
    
    resultados = []
    
    # Evaluar cada regla
    for regla in reglas:
        print(f"🔍 Evaluando: {regla.nombre}")
        print(f"   {regla.descripcion}")
        print(f"   Tipo: {regla.tipo_apuesta}\n")
        
        # Train
        disparos_train = 0
        aciertos_train = 0
        
        for _, partido in df_train.iterrows():
            p_dict = partido.to_dict()
            
            if regla.evaluar(p_dict):
                disparos_train += 1
                resultado = calcular_resultado_regla(p_dict, regla)
                if resultado:
                    aciertos_train += 1
        
        # Test
        disparos_test = 0
        aciertos_test = 0
        
        for _, partido in df_test.iterrows():
            p_dict = partido.to_dict()
            
            if regla.evaluar(p_dict):
                disparos_test += 1
                resultado = calcular_resultado_regla(p_dict, regla)
                if resultado:
                    aciertos_test += 1
        
        # Calcular métricas
        win_rate_train = (aciertos_train / disparos_train * 100) if disparos_train > 0 else 0
        win_rate_test = (aciertos_test / disparos_test * 100) if disparos_test > 0 else 0
        
        # ROI aproximado (asumiendo cuota promedio de 1.90)
        cuota_promedio = 1.90
        roi_train = ((aciertos_train * cuota_promedio - disparos_train) / disparos_train * 100) if disparos_train > 0 else 0
        roi_test = ((aciertos_test * cuota_promedio - disparos_test) / disparos_test * 100) if disparos_test > 0 else 0
        
        # Validación estadística
        validator = DataValidator()
        validacion = validator.validar_significancia(aciertos_test, disparos_test) if disparos_test > 0 else {'p_value': 1.0, 'es_significativo': False}
        
        resultados.append({
            'Regla': regla.nombre,
            'Tipo': regla.tipo_apuesta,
            'Disparos_Train': disparos_train,
            'Win_Rate_Train': win_rate_train,
            'ROI_Train': roi_train,
            'Disparos_Test': disparos_test,
            'Win_Rate_Test': win_rate_test,
            'ROI_Test': roi_test,
            'P_Value': validacion.get('p_value', 1.0),
            'Significativo': validacion.get('es_significativo', False)
        })
        
        print(f"   📊 TRAIN: {disparos_train} disparos | {win_rate_train:.1f}% WR | {roi_train:+.1f}% ROI")
        print(f"   📊 TEST:  {disparos_test} disparos | {win_rate_test:.1f}% WR | {roi_test:+.1f}% ROI")
        print(f"   📈 P-value: {validacion.get('p_value', 1.0):.4f} {'✅ Significativo' if validacion.get('es_significativo') else '❌ No significativo'}")
        print("\n" + "-"*70 + "\n")
    
    # Crear DataFrame de resultados
    df_resultados = pd.DataFrame(resultados)
    
    # Guardar resultados
    output_dir = Path(__file__).parent.parent / 'outputs' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'backtest_custom_rules_{timestamp}.csv'
    df_resultados.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*70 + "\n")
    
    # Ordenar por ROI en test
    df_resultados_sorted = df_resultados.sort_values('ROI_Test', ascending=False)
    
    print(df_resultados_sorted.to_string(index=False))
    
    print(f"\n✅ Resultados guardados en: {output_file}")
    
    # Identificar reglas rentables
    reglas_rentables = df_resultados_sorted[
        (df_resultados_sorted['ROI_Test'] > 0) & 
        (df_resultados_sorted['Significativo'] == True) &
        (df_resultados_sorted['Disparos_Test'] >= 20)
    ]
    
    if len(reglas_rentables) > 0:
        print("\n" + "="*70)
        print("🎯 REGLAS RENTABLES Y SIGNIFICATIVAS")
        print("="*70 + "\n")
        
        for _, regla in reglas_rentables.iterrows():
            print(f"✅ {regla['Regla']}")
            print(f"   Tipo: {regla['Tipo']}")
            print(f"   Disparos: {int(regla['Disparos_Test'])}")
            print(f"   Win Rate: {regla['Win_Rate_Test']:.1f}%")
            print(f"   ROI: {regla['ROI_Test']:+.1f}%")
            print(f"   P-value: {regla['P_Value']:.4f}")
            print()
    else:
        print("\n⚠️  Ninguna regla cumple los criterios de rentabilidad y significancia estadística")
    
    print("\n" + "="*70)
    print("✅ BACKTEST COMPLETADO")
    print("="*70 + "\n")


if __name__ == '__main__':
    ejecutar_backtest()


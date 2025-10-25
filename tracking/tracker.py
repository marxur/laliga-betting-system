"""
Sistema de Tracking de Apuestas
Gestiona el registro y análisis de apuestas
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class BettingTracker:
    """
    Gestor de tracking de apuestas
    """
    
    def __init__(self):
        self.tracking_dir = Path(__file__).parent
        self.csv_path = self.tracking_dir / 'apuestas.csv'
        
        # Crear archivo si no existe
        if not self.csv_path.exists():
            self._crear_csv()
    
    def _crear_csv(self):
        """Crea el archivo CSV inicial"""
        df = pd.DataFrame(columns=[
            'ID', 'Fecha', 'Hora', 'Partido', 'Tipo_Apuesta', 'Estrategia',
            'Cuota', 'Stake_EUR', 'Ganancia_Posible', 'Resultado',
            'Beneficio_Real', 'ROI', 'Notas'
        ])
        df.to_csv(self.csv_path, index=False)
    
    def agregar_apuesta(self, apuesta: Dict[str, Any]) -> int:
        """
        Agrega una nueva apuesta al tracking
        
        Args:
            apuesta: Diccionario con datos de la apuesta
                {
                    'fecha': str,
                    'hora': str,
                    'partido': str,
                    'tipo_apuesta': str,
                    'estrategia': str,
                    'cuota': float,
                    'stake_eur': float,
                    'notas': str (opcional)
                }
        
        Returns:
            ID de la apuesta creada
        """
        df = pd.read_csv(self.csv_path)
        
        # Calcular nuevo ID
        nuevo_id = 1 if len(df) == 0 else df['ID'].max() + 1
        
        # Calcular ganancia posible
        ganancia_posible = apuesta['stake_eur'] * apuesta['cuota']
        
        # Crear nueva fila
        nueva_fila = {
            'ID': nuevo_id,
            'Fecha': apuesta['fecha'],
            'Hora': apuesta['hora'],
            'Partido': apuesta['partido'],
            'Tipo_Apuesta': apuesta['tipo_apuesta'],
            'Estrategia': apuesta['estrategia'],
            'Cuota': apuesta['cuota'],
            'Stake_EUR': apuesta['stake_eur'],
            'Ganancia_Posible': round(ganancia_posible, 2),
            'Resultado': 'Pendiente',
            'Beneficio_Real': 0.00,
            'ROI': 0.00,
            'Notas': apuesta.get('notas', '')
        }
        
        # Añadir al DataFrame
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        df.to_csv(self.csv_path, index=False)
        
        print(f"✅ Apuesta #{nuevo_id} registrada")
        return nuevo_id
    
    def actualizar_resultado(self, apuesta_id: int, resultado: str, beneficio_real: float = None):
        """
        Actualiza el resultado de una apuesta
        
        Args:
            apuesta_id: ID de la apuesta
            resultado: 'Ganada', 'Perdida', 'Void', 'Pendiente'
            beneficio_real: Beneficio real obtenido (opcional, se calcula automáticamente)
        """
        df = pd.read_csv(self.csv_path)
        
        # Buscar apuesta
        idx = df[df['ID'] == apuesta_id].index
        
        if len(idx) == 0:
            print(f"❌ Apuesta #{apuesta_id} no encontrada")
            return
        
        idx = idx[0]
        
        # Actualizar resultado
        df.at[idx, 'Resultado'] = resultado
        
        # Calcular beneficio
        if beneficio_real is None:
            if resultado == 'Ganada':
                beneficio_real = df.at[idx, 'Ganancia_Posible'] - df.at[idx, 'Stake_EUR']
            elif resultado == 'Perdida':
                beneficio_real = -df.at[idx, 'Stake_EUR']
            elif resultado == 'Void':
                beneficio_real = 0.00
            else:
                beneficio_real = 0.00
        
        df.at[idx, 'Beneficio_Real'] = round(beneficio_real, 2)
        
        # Calcular ROI
        if df.at[idx, 'Stake_EUR'] > 0:
            roi = (beneficio_real / df.at[idx, 'Stake_EUR']) * 100
            df.at[idx, 'ROI'] = round(roi, 2)
        
        df.to_csv(self.csv_path, index=False)
        
        print(f"✅ Apuesta #{apuesta_id} actualizada: {resultado}")
        print(f"   Beneficio: {beneficio_real:+.2f} EUR | ROI: {df.at[idx, 'ROI']:+.2f}%")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Calcula estadísticas generales
        
        Returns:
            Diccionario con estadísticas
        """
        df = pd.read_csv(self.csv_path)
        
        # Filtrar solo apuestas finalizadas
        df_finalizadas = df[df['Resultado'].isin(['Ganada', 'Perdida', 'Void'])]
        
        if len(df_finalizadas) == 0:
            return {
                'total_apuestas': len(df),
                'pendientes': len(df[df['Resultado'] == 'Pendiente']),
                'mensaje': 'No hay apuestas finalizadas aún'
            }
        
        total_apuestas = len(df_finalizadas)
        ganadas = len(df_finalizadas[df_finalizadas['Resultado'] == 'Ganada'])
        perdidas = len(df_finalizadas[df_finalizadas['Resultado'] == 'Perdida'])
        void = len(df_finalizadas[df_finalizadas['Resultado'] == 'Void'])
        
        win_rate = (ganadas / total_apuestas * 100) if total_apuestas > 0 else 0
        
        total_invertido = df_finalizadas['Stake_EUR'].sum()
        beneficio_total = df_finalizadas['Beneficio_Real'].sum()
        roi_total = (beneficio_total / total_invertido * 100) if total_invertido > 0 else 0
        
        # Estadísticas por estrategia
        stats_por_estrategia = df_finalizadas.groupby('Estrategia').agg({
            'ID': 'count',
            'Beneficio_Real': 'sum',
            'Stake_EUR': 'sum'
        }).reset_index()
        
        stats_por_estrategia['ROI'] = (stats_por_estrategia['Beneficio_Real'] / stats_por_estrategia['Stake_EUR'] * 100).round(2)
        stats_por_estrategia.columns = ['Estrategia', 'Apuestas', 'Beneficio', 'Invertido', 'ROI']
        
        return {
            'total_apuestas': total_apuestas,
            'ganadas': ganadas,
            'perdidas': perdidas,
            'void': void,
            'pendientes': len(df[df['Resultado'] == 'Pendiente']),
            'win_rate': round(win_rate, 2),
            'total_invertido': round(total_invertido, 2),
            'beneficio_total': round(beneficio_total, 2),
            'roi_total': round(roi_total, 2),
            'por_estrategia': stats_por_estrategia.to_dict('records')
        }
    
    def generar_reporte(self) -> str:
        """
        Genera un reporte en texto
        
        Returns:
            Reporte formateado
        """
        stats = self.obtener_estadisticas()
        
        if 'mensaje' in stats:
            return f"""
📊 REPORTE DE APUESTAS
{'='*50}

Total de apuestas: {stats['total_apuestas']}
Pendientes: {stats['pendientes']}

{stats['mensaje']}
"""
        
        reporte = f"""
📊 REPORTE DE APUESTAS
{'='*50}

📈 RESUMEN GENERAL
  Total de apuestas: {stats['total_apuestas']}
  ✅ Ganadas: {stats['ganadas']}
  ❌ Perdidas: {stats['perdidas']}
  ⚪ Void: {stats['void']}
  ⏳ Pendientes: {stats['pendientes']}
  
  Win Rate: {stats['win_rate']:.2f}%
  
💰 RENDIMIENTO FINANCIERO
  Total invertido: {stats['total_invertido']:.2f} EUR
  Beneficio total: {stats['beneficio_total']:+.2f} EUR
  ROI: {stats['roi_total']:+.2f}%

📋 POR ESTRATEGIA
"""
        
        for estrategia in stats['por_estrategia']:
            reporte += f"""
  {estrategia['Estrategia']}:
    Apuestas: {estrategia['Apuestas']}
    Invertido: {estrategia['Invertido']:.2f} EUR
    Beneficio: {estrategia['Beneficio']:+.2f} EUR
    ROI: {estrategia['ROI']:+.2f}%
"""
        
        reporte += f"\n{'='*50}\n"
        
        return reporte
    
    def listar_apuestas(self, filtro: Optional[str] = None) -> pd.DataFrame:
        """
        Lista apuestas con filtro opcional
        
        Args:
            filtro: 'Pendiente', 'Ganada', 'Perdida', 'Void', o None para todas
        
        Returns:
            DataFrame con apuestas
        """
        df = pd.read_csv(self.csv_path)
        
        if filtro:
            df = df[df['Resultado'] == filtro]
        
        return df


# Funciones de utilidad
def registrar_apuesta_rapida(partido: str, tipo: str, estrategia: str, cuota: float, stake: float, notas: str = ""):
    """
    Registra una apuesta rápidamente
    """
    tracker = BettingTracker()
    
    ahora = datetime.now()
    
    apuesta = {
        'fecha': ahora.strftime('%d/%m/%Y'),
        'hora': ahora.strftime('%H:%M'),
        'partido': partido,
        'tipo_apuesta': tipo,
        'estrategia': estrategia,
        'cuota': cuota,
        'stake_eur': stake,
        'notas': notas
    }
    
    return tracker.agregar_apuesta(apuesta)


def ver_reporte():
    """
    Muestra el reporte actual
    """
    tracker = BettingTracker()
    print(tracker.generar_reporte())


if __name__ == '__main__':
    # Ejemplo de uso
    tracker = BettingTracker()
    print(tracker.generar_reporte())


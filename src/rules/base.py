"""
Clase base para todas las reglas
Define la interfaz estándar que todas las reglas deben seguir
"""

from typing import Callable, Any
from dataclasses import dataclass
import pandas as pd


@dataclass
class Regla:
    """
    Clase base para reglas de apuesta
    
    Attributes:
        nombre: Identificador único de la regla
        descripcion: Explicación de qué evalúa la regla
        condicion: Función que recibe un partido (Series) y devuelve bool
        tipo_apuesta: 'Local', 'Visitante', 'Empate', 'BTTS', 'Over', 'Under'
        confianza_esperada: Tasa de acierto esperada según backtest manual
        activa: Si la regla está activa para evaluación
    """
    
    nombre: str
    descripcion: str
    condicion: Callable[[pd.Series], bool]
    tipo_apuesta: str
    confianza_esperada: float
    activa: bool = True
    
    def evaluar(self, partido: pd.Series) -> bool:
        """
        Evalúa si la regla dispara para un partido dado
        
        Args:
            partido: Serie de pandas con datos del partido
        
        Returns:
            True si la regla dispara, False en caso contrario
        """
        try:
            return self.condicion(partido)
        except (KeyError, TypeError, AttributeError) as e:
            # Si falta algún dato necesario, la regla no dispara
            return False
    
    def __repr__(self):
        estado = "✓" if self.activa else "✗"
        return f"{estado} Regla('{self.nombre}', {self.tipo_apuesta}, confianza={self.confianza_esperada:.1%})"
    
    def validar(self) -> bool:
        """Valida que la regla esté bien configurada"""
        assert isinstance(self.nombre, str) and self.nombre, "Nombre inválido"
        assert self.tipo_apuesta in ['Local', 'Visitante', 'Empate', 'BTTS', 'Over', 'Under'], \
            f"Tipo de apuesta inválido: {self.tipo_apuesta}"
        assert 0 <= self.confianza_esperada <= 1, "Confianza debe estar entre 0 y 1"
        return True


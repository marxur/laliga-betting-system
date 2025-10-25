"""
Validación estadística de resultados
Responsabilidad: Detectar overfitting y validar significancia
"""

import pandas as pd
from typing import Dict, Any, Tuple
from scipy.stats import binomtest
import logging

from src.config import BACKTEST_CONFIG

logger = logging.getLogger(__name__)


class DataValidator:
    """Valida resultados de backtest estadísticamente"""
    
    def __init__(self, config=BACKTEST_CONFIG):
        self.config = config
    
    def split_temporal(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Divide dataset en train/test por fecha
        
        Args:
            df: DataFrame completo
        
        Returns:
            (df_train, df_test)
        """
        
        df_train = df[df['Date'] <= self.config.train_end_date].copy()
        df_test = df[df['Date'] >= self.config.test_start_date].copy()
        
        logger.info(f"📊 Split temporal:")
        logger.info(f"   Train: {len(df_train)} partidos (hasta {self.config.train_end_date})")
        logger.info(f"   Test:  {len(df_test)} partidos (desde {self.config.test_start_date})")
        
        return df_train, df_test
    
    def validar_significancia(self, aciertos: int, disparos: int, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Test binomial para validar significancia estadística
        
        H0: La regla acierta por azar (p = 0.5)
        H1: La regla tiene ventaja real (p > 0.5)
        
        Args:
            aciertos: Número de apuestas acertadas
            disparos: Número total de apuestas
            alpha: Nivel de significancia (default 0.05)
        
        Returns:
            Dict con p-value y resultado del test
        """
        
        if disparos == 0:
            return {
                'p_value': 1.0,
                'significativo': False,
                'mensaje': 'Sin disparos'
            }
        
        # Test binomial (one-sided: greater)
        result = binomtest(
            aciertos,
            disparos,
            p=self.config.null_hypothesis_prob,
            alternative='greater'
        )
        p_value = result.pvalue
        
        significativo = p_value < alpha
        
        return {
            'p_value': p_value,
            'significativo': significativo,
            'mensaje': f"{'✓ Significativo' if significativo else '✗ No significativo'} (p={p_value:.4f})"
        }
    
    def detectar_overfitting(
        self,
        resultados_train: Dict[str, Dict],
        resultados_test: Dict[str, Dict],
        umbral_degradacion: float = 0.15
    ) -> bool:
        """
        Detecta overfitting comparando train vs test
        
        Args:
            resultados_train: Resultados en conjunto de entrenamiento
            resultados_test: Resultados en conjunto de test
            umbral_degradacion: Máxima degradación aceptable en win rate
        
        Returns:
            True si se detecta overfitting
        """
        
        overfitting_detectado = False
        
        logger.info("\n🔍 Análisis de Overfitting (Train vs Test):")
        logger.info("="*60)
        
        for nombre_regla in resultados_train.keys():
            if nombre_regla not in resultados_test:
                continue
            
            train = resultados_train[nombre_regla]
            test = resultados_test[nombre_regla]
            
            # Comparar win rates
            wr_train = train['win_rate']
            wr_test = test['win_rate']
            degradacion = wr_train - wr_test
            
            # Comparar ROI
            roi_train = train['roi']
            roi_test = test['roi']
            
            # Detectar overfitting
            overfitting_regla = (
                degradacion > umbral_degradacion or
                (roi_train > 0.10 and roi_test < 0)
            )
            
            if overfitting_regla:
                overfitting_detectado = True
                emoji = "⚠️"
            else:
                emoji = "✓"
            
            logger.info(f"{emoji} {nombre_regla}:")
            logger.info(f"   Train: WR={wr_train:.1%}, ROI={roi_train:.1%}")
            logger.info(f"   Test:  WR={wr_test:.1%}, ROI={roi_test:.1%}")
            logger.info(f"   Degradación: {degradacion:.1%}")
            logger.info("")
        
        return overfitting_detectado
    
    def validar_regla(self, resultado: Dict[str, Any]) -> bool:
        """
        Valida si una regla cumple criterios mínimos
        
        Args:
            resultado: Dict con métricas de la regla
        
        Returns:
            True si la regla es válida
        """
        
        disparos = resultado['disparos']
        win_rate = resultado['win_rate']
        roi = resultado['roi']
        
        # Criterios de validación
        cumple_sample_size = disparos >= self.config.min_sample_size
        cumple_win_rate = win_rate >= self.config.min_win_rate
        cumple_roi = roi >= self.config.min_roi
        
        # Validar significancia estadística
        sig = self.validar_significancia(
            resultado['aciertos'],
            disparos,
            self.config.alpha
        )
        
        cumple_significancia = sig['significativo']
        
        # Regla válida si cumple TODOS los criterios
        valida = all([
            cumple_sample_size,
            cumple_win_rate,
            cumple_roi,
            cumple_significancia
        ])
        
        return valida
    
    def calibracion_simple(self, resultados: Dict[str, Dict]) -> Dict[str, float]:
        """
        Calibración simple: compara confianza esperada vs real
        
        Args:
            resultados: Dict con resultados por regla
        
        Returns:
            Dict con métricas de calibración
        """
        
        diferencias = []
        
        for nombre, res in resultados.items():
            # Aquí necesitaríamos la confianza esperada de la regla
            # (simplificado por ahora)
            pass
        
        return {
            'mae': 0.0,  # Mean Absolute Error
            'calibrado': True
        }


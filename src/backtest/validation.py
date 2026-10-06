"""
Validación estadística.
El nulo de una apuesta no es el 50 %: es la probabilidad implícita de su cuota.
"""

import math
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
import logging

from src.config import BACKTEST_CONFIG

logger = logging.getLogger(__name__)


def _p_valor_normal_mayor(z: float) -> float:
    """P(Z > z) para una normal estándar."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


class DataValidator:
    """Valida resultados de backtest."""

    def __init__(self, config=BACKTEST_CONFIG):
        self.config = config

    def split_temporal(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df_train = df[df['Date'] <= self.config.train_end_date].copy()
        df_test = df[df['Date'] >= self.config.test_start_date].copy()
        logger.info("Split temporal:")
        logger.info(f"  Train: {len(df_train)} partidos (hasta {self.config.train_end_date})")
        logger.info(f"  Test:  {len(df_test)} partidos (desde {self.config.test_start_date})")
        return df_train, df_test

    def validar_significancia(
        self,
        aciertos: int,
        disparos: int,
        alpha: float = 0.05,
        p_nulo: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Test binomial. p_nulo por defecto sigue siendo el legado 0.5.
        Para edge hay que usar validar_contra_cuota.
        """
        from scipy.stats import binomtest

        p0 = self.config.null_hypothesis_prob if p_nulo is None else p_nulo
        if disparos == 0:
            return {'p_value': 1.0, 'significativo': False, 'mensaje': 'Sin disparos', 'p_nulo': p0}

        p_value = binomtest(aciertos, disparos, p=p0, alternative='greater').pvalue
        significativo = p_value < alpha
        return {
            'p_value': p_value,
            'significativo': significativo,
            'p_nulo': p0,
            'mensaje': f"{'significativo' if significativo else 'no significativo'} (p={p_value:.4f}, nulo={p0:.3f})",
        }

    def validar_contra_cuota(
        self,
        partidos: List[Dict[str, Any]],
        alpha: float = 0.05,
    ) -> Dict[str, Any]:
        """
        H0: cada acierto tiene probabilidad 1/cuota.
        Aproximación normal de la suma de Bernoulli independientes.
        """
        cuotas = []
        aciertos = 0
        for partido in partidos:
            cuota = partido.get('cuota')
            if cuota is None or cuota <= 1.0:
                continue
            cuotas.append(float(cuota))
            aciertos += int(bool(partido.get('acerto')))

        n = len(cuotas)
        if n == 0:
            return {
                'p_value': 1.0,
                'significativo': False,
                'aciertos': 0,
                'esperados': 0.0,
                'mensaje': 'Sin disparos con cuota',
            }

        esperados = sum(1.0 / c for c in cuotas)
        varianza = sum((1.0 / c) * (1.0 - 1.0 / c) for c in cuotas)
        if varianza <= 0:
            return {
                'p_value': 1.0,
                'significativo': False,
                'aciertos': aciertos,
                'esperados': esperados,
                'mensaje': 'Varianza nula',
            }

        z = (aciertos - esperados) / math.sqrt(varianza)
        p_value = _p_valor_normal_mayor(z)
        significativo = p_value < alpha and aciertos > esperados
        return {
            'p_value': p_value,
            'z': z,
            'significativo': significativo,
            'aciertos': aciertos,
            'esperados': esperados,
            'disparos': n,
            'mensaje': (
                f"{'edge' if significativo else 'sin edge'} "
                f"(aciertos={aciertos}, esperados={esperados:.1f}, p={p_value:.4f})"
            ),
        }

    def detectar_overfitting(
        self,
        resultados_train: Dict[str, Dict],
        resultados_test: Dict[str, Dict],
        umbral_degradacion: float = 0.15,
    ) -> bool:
        overfitting_detectado = False
        logger.info("Analisis train vs test:")
        for nombre in resultados_train:
            if nombre not in resultados_test:
                continue
            train = resultados_train[nombre]
            test = resultados_test[nombre]
            degradacion = train['win_rate'] - test['win_rate']
            sobreajuste = degradacion > umbral_degradacion or (
                train['roi'] > 0.10 and test['roi'] < 0
            )
            overfitting_detectado = overfitting_detectado or sobreajuste
            logger.info(
                f"  {nombre}: train WR={train['win_rate']:.1%} ROI={train['roi']:.1%} | "
                f"test WR={test['win_rate']:.1%} ROI={test['roi']:.1%} | "
                f"degradacion={degradacion:.1%}"
            )
        return overfitting_detectado

    def validar_regla(self, resultado: Dict[str, Any]) -> bool:
        """Una regla vale si tiene muestra, ROI y edge contra su propia cuota."""
        disparos = resultado['disparos']
        if disparos < self.config.min_sample_size:
            return False
        if resultado['roi'] < self.config.min_roi:
            return False
        partidos = resultado.get('partidos') or []
        if partidos:
            return self.validar_contra_cuota(partidos, self.config.alpha)['significativo']
        return self.validar_significancia(
            resultado['aciertos'], disparos, self.config.alpha
        )['significativo']

    def calibracion_simple(self, resultados: Dict[str, Dict], reglas=None) -> Dict[str, Any]:
        """MAE entre la confianza declarada y el win rate observado."""
        confianza = {}
        if reglas:
            confianza = {r.nombre: r.confianza_esperada for r in reglas}

        diferencias = []
        for nombre, res in resultados.items():
            if res.get('disparos', 0) == 0 or nombre not in confianza:
                continue
            diferencias.append(abs(confianza[nombre] - res['win_rate']))

        if not diferencias:
            return {'mae': None, 'calibrado': False, 'n': 0}
        mae = sum(diferencias) / len(diferencias)
        return {'mae': mae, 'calibrado': mae < 0.05, 'n': len(diferencias)}

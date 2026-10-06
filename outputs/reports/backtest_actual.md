# Backtest generado por el motor actual

Estas cifras salen de `src/pipeline.py` sobre `data/global/SP1_*.csv`.
No son las de la tabla antigua del README.

- Partidos: 2660
- Train: 2080
- Test: 580
- Comparación: la cartera anterior, sin margen mínimo, hizo 75/136 y +2,9 %. Ese beneficio no sobrevive al filtro de 4 puntos de edge.

| Regla | Confianza train | Disparos test | Win rate | ROI | Drawdown | Edge |
|---|---:|---:|---:|---:|---:|---|
| Favorito_Local_Forma | 78.0% | 76 | 78.9% | 7.8% | 4.00u | sin edge (aciertos=60, esperados=55.9, p=0.1390) |
| Visitante_Invicto | 72.0% | 84 | 51.2% | 1.0% | 8.26u | sin edge (aciertos=43, esperados=43.6, p=0.5535) |
| BTTS_Goleadores | 68.0% | 0 | 0.0% | 0.0% | 0.00u | Sin disparos con cuota |
| Local_Dominante_Casa | 70.9% | 45 | 73.3% | 1.4% | 3.89u | sin edge (aciertos=33, esperados=32.4, p=0.4150) |
| Visitante_Racha_Victorias | 54.5% | 93 | 60.2% | 8.6% | 5.95u | sin edge (aciertos=56, esperados=51.1, p=0.1487) |
| Over_25_Ofensivos | 65.0% | 96 | 51.0% | -19.8% | 19.44u | sin edge (aciertos=49, esperados=59.0, p=0.9839) |
| Local_Invicto_Favorito | 78.5% | 45 | 80.0% | 2.7% | 2.94u | sin edge (aciertos=36, esperados=34.8, p=0.3391) |
| BTTS_Historico_Alto | 71.0% | 0 | 0.0% | 0.0% | 0.00u | Sin disparos con cuota |

## Cartera en test

Una apuesta por partido, solo si el win rate de train supera la cuota en al menos 4 puntos de edge.
Las reglas con ROI negativo o menos de 40 disparos en train quedan fuera.
- Disparos: 75
- Aciertos: 39
- ROI: -5.5%
- Ganancia: -4.11 unidades
- Drawdown: 10.90 unidades
- Edge: sin edge (aciertos=39, esperados=41.3, p=0.7130)

## Por año de test

- 2024: 22/45, -6.03 unidades
- 2025: 17/30, +1.92 unidades

Si el edge no es significativo, la regla no está validada aunque el ROI puntual sea positivo.

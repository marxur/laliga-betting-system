# Lo que este repositorio mide, y lo que no

La tabla de ROI del README (+5.1 %, +7.8 %, +13.4 %) no sale del motor actual. No debe usarse como resultado hasta que `scripts/run_backtest.py` la regenere con datos y este código.

Desde octubre de 2026 el backtest hace esto:

- No liquida un disparo sin cuota decimal mayor que 1. Over ya no se cierra a 1.0.
- Forma, rachas, goles y BTTS histórico usan solo partidos anteriores. Una ventana corta no se extrapola a 5 partidos.
- El test de edge compara aciertos con la suma de `1/cuota`, no con el 50 %.
- `ejecutar_cartera` deja como mucho una apuesta por partido: la de mayor edge declarado (`confianza_esperada * cuota - 1`). Esa confianza sigue siendo un número escrito en la regla, no una probabilidad estimada.
- BTTS se omite si el histórico no trae `Cuota_BTTS`.

Pendiente: un solo monitor, cierre contra la cuota de cierre (CLV) y sustituir la confianza escrita a mano por la tasa del conjunto de entrenamiento.

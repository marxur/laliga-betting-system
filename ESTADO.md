# Estado auditado

Fecha: 7 de octubre de 2026.

El proyecto funciona como backtest reproducible. No funciona como sistema de alertas validado.

- Datos: 2660 partidos de La Liga en `data/global/SP1_*.csv`.
- Comando: `PYTHONPATH=. python3 scripts/run_backtest.py`
- Tests: `PYTHONPATH=. python3 -m pytest tests -q` (11 pasados en la auditoría).
- Cartera filtrada en test: 39/75, ROI -5,5 %, drawdown 10,90 u.
- Edge contra la cuota: no (39 aciertos, 41,3 esperados, p=0,71).
- La cartera sin margen mínimo (75/136, +2,9 %) tampoco tenía edge.
- Over 2,5 ofensivo: -19,8 % en test. BTTS: sin cuota en los CSV.
- Veredicto: no apostar con estas reglas.

El frontal de lectura está en `docs/front.html`. Las cifras del README antiguo no salen de este motor.

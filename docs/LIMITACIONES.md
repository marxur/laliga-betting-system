# Auditoría del 7 de octubre de 2026

`python scripts/run_backtest.py` corre de punta a punta con los CSV locales de La Liga.

- 2660 partidos, 2080 de train y 580 de test.
- Over se liquida con cuota real. Sin cuota, el disparo no entra.
- BTTS no tiene cuota en football-data.co.uk, así que esas reglas quedan en cero disparos.
- Ninguna regla del test tiene edge significativo contra 1/cuota.
- La cartera (una apuesta por partido, confianza = win rate de train) hizo 75/136, ROI +2.9%, p=0.41.
- El monitor ya no inventa cuotas 1.5/2.5 ni envía email si no hay contraseña de aplicación.

Las cifras antiguas del README (+5.1%, +13.4%, ROI anual 9.5%) no se reproducen.

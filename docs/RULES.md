# 📜 Documentación de Reglas

Este documento detalla cada una de las reglas implementadas en el sistema, su lógica y su rendimiento histórico en los conjuntos de `train` (2018-2023) y `test` (2024-2025).

---

## ✅ Reglas Aprobadas para Producción

Estas reglas han demostrado ser robustas y rentables en el período de validación.

### 1. Local_Invicto_Favorito

-   **Lógica:** Apuesta por el equipo **local** si no ha perdido en sus últimos 3 partidos y su cuota es muy baja (inferior a 1.50). Busca favoritos sólidos que rara vez fallan en casa.
-   **Condición:** `p.get('Local_Derrotas_L3', 99) == 0 and p.get('Cuota_Local', 999) < 1.50`
-   **Rendimiento:**

| Métrica | Train (2018-23) | Test (2024-25) |
| :--- | :--- | :--- |
| Disparos | 282 | 88 |
| Win Rate | 78.0% | **80.7%** |
| ROI | 2.6% | **5.1%** |

-   **Evaluación:** ⭐⭐⭐ **Excelente.** La regla más fiable del sistema. Mejora su rendimiento en el conjunto de test, lo que indica una gran robustez. Es el pilar del sistema.

### 2. Favorito_Local_Forma

-   **Lógica:** Apuesta por el equipo **local** si es favorito (cuota < 1.70) y llega en un gran estado de forma (10+ puntos de los últimos 15 posibles).
-   **Condición:** `p.get('Cuota_Local', 999) < 1.70 and p.get('Local_Forma_L5', 0) >= 10`
-   **Rendimiento:**

| Métrica | Train (2018-23) | Test (2024-25) |
| :--- | :--- | :--- |
| Disparos | 219 | 76 |
| Win Rate | 69.9% | **78.9%** |
| ROI | -4.1% | **7.8%** |

-   **Evaluación:** ⭐⭐ **Muy Buena.** Aunque tuvo un ROI ligeramente negativo en el entrenamiento, mostró una mejora espectacular en el test, con un win rate cercano al 80% y un ROI sólido. 

### 3. Visitante_Invicto

-   **Lógica:** Apuesta por el equipo **visitante** si llega en buena forma (sin derrotas en los últimos 3 partidos, 8+ puntos de 15) y no es un claro no favorito (cuota < 3.0).
-   **Condición:** `p.get('Visitante_Derrotas_L3', 99) == 0 and p.get('Cuota_Visitante', 999) < 3.0 and p.get('Visitante_Forma_L5', 0) >= 8`
-   **Rendimiento:**

| Métrica | Train (2018-23) | Test (2024-25) |
| :--- | :--- | :--- |
| Disparos | 240 | 130 |
| Win Rate | 47.5% | **56.9%** |
| ROI | -8.8% | **13.4%** |

-   **Evaluación:** ⭐ **Buena.** Es la regla con el ROI más alto en el período de test. Aunque su win rate es más bajo, las cuotas más altas compensan con creces, generando un valor excelente.

---

## ❌ Reglas Desactivadas (No Rentables)

Estas reglas mostraron un rendimiento pobre y han sido desactivadas para evitar pérdidas.

### 4. BTTS_Goleadores

-   **Lógica:** Apuesta a que **ambos equipos marcan (BTTS)** si ambos tienen un promedio de goles superior a 1.5 en sus últimos 5 partidos.
-   **Rendimiento:**

| Métrica | Train (2018-23) | Test (2024-25) |
| :--- | :--- | :--- |
| Win Rate | 50.5% | 38.5% |
| ROI | -9.0% | **-30.8%** |

-   **Evaluación:** ❌ **Mala.** El rendimiento se degrada fuertemente en el test. La lógica es demasiado simple y no captura la complejidad de los mercados de goles.

### 5. Over_25_Ofensivos

-   **Lógica:** Apuesta a que habrá **más de 2.5 goles** si la suma de los promedios de goles de ambos equipos es superior a 3.5.
-   **Rendimiento:**

| Métrica | Train (2018-23) | Test (2024-25) |
| :--- | :--- | :--- |
| Win Rate | 49.8% | 51.0% |
| ROI | -50.2% | **-49.0%** |

-   **Evaluación:** ❌ **Pésima.** Un ROI de casi -50% indica que esta regla es un fracaso total. El mercado de Over/Under está bien ajustado por las casas de apuestas.

---

## ⚪ Reglas a Revisar (No Dispararon)

Estas reglas no se activaron durante el backtest, probablemente debido a que las features necesarias no se implementaron completamente.

### 6. Visitante_Racha_Victorias

-   **Lógica:** Apuesta por el **visitante** si llega con 2 o más victorias consecutivas y tiene una cuota razonable (< 2.5).
-   **Estado:** ⚪ **Inactiva.** La feature `Visitante_Victorias_L3` no fue calculada, por lo que la regla nunca se disparó.

### 7. BTTS_Historico_Alto

-   **Lógica:** Apuesta a **BTTS** si ambos equipos han tenido 3 o más partidos con BTTS en sus últimos 4 encuentros.
-   **Estado:** ⚪ **Inactiva.** Las features `Local_BTTS_L4` y `Visitante_BTTS_L4` no fueron calculadas.

---

## 📋 Resumen de Rendimiento (Test 2024-2025)

| Regla | Disparos | Win Rate | ROI | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **Local_Invicto_Favorito** | 88 | 80.7% | **+5.1%** | ✅ **Aprobada** |
| **Favorito_Local_Forma** | 76 | 78.9% | **+7.8%** | ✅ **Aprobada** |
| **Visitante_Invicto** | 130 | 56.9% | **+13.4%** | ✅ **Aprobada** |
| Local_Dominante_Casa | 45 | 73.3% | +1.4% | ⚠️ En Observación |
| BTTS_Goleadores | 52 | 38.5% | -30.8% | ❌ Desactivada |
| Over_25_Ofensivos | 96 | 51.0% | -49.0% | ❌ Desactivada |
| Visitante_Racha_Victorias | 0 | - | - | ⚪ A Revisar |
| BTTS_Historico_Alto | 0 | - | - | ⚪ A Revisar |


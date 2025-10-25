# ⚡ Guía de Inicio Rápido

**Sistema 100% operativo configurado para Marcos Valencia García**

---

## 🚀 Pasos para Empezar (5 minutos)

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Credenciales

```bash
python scripts/setup.py
```

Te pedirá:
- **API Key de API-Sports.io:** Regístrate en https://dashboard.api-football.com/
- **Contraseña de Gmail:** Genera una en https://myaccount.google.com/apppasswords

### 3. Verificar Configuración

```bash
python scripts/test_config.py
```

Debe mostrar ✅ en todas las pruebas.

### 4. Ejecutar Backtest (Opcional)

```bash
python scripts/run_backtest.py
```

Valida las reglas contra datos históricos 2018-2025.

### 5. Iniciar Monitor de Alertas

```bash
python scripts/start_monitor.py
```

El sistema:
- Consulta próximos partidos cada 24h
- Evalúa contra reglas validadas
- Envía email a: marcosvalenciagarcia@gmail.com

---

## 📧 Ejemplo de Alerta

Recibirás emails como este:

```
🎯 Nueva Oportunidad de Apuesta

📅 2025-10-28 20:00
⚽ Real Madrid vs Barcelona

📊 Detalles:
- Regla: Local_Invicto_Favorito
- Tipo: Local
- Cuota: 1.45
- Confianza: 82%

💰 Gestión de Riesgo:
- Stake Recomendado: 12.5 unidades
- Kelly Fraction: 0.25 (conservador)
```

---

## 🔧 Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `python scripts/setup.py` | Configurar credenciales |
| `python scripts/test_config.py` | Verificar configuración |
| `python scripts/run_backtest.py` | Ejecutar backtest |
| `python scripts/update_data.py` | Actualizar datos |
| `python scripts/start_monitor.py` | Iniciar alertas |

---

## ⚠️ Troubleshooting

### "API_SPORTS_KEY no configurada"
→ Ejecuta `python scripts/setup.py` y añade tu API key

### "EMAIL_PASSWORD no configurada"
→ Genera una contraseña de aplicación en Gmail (no uses tu contraseña normal)

### "API-Sports.io: No disponible"
→ Verifica tu API key o usa el respaldo automático (TheSportsDB)

### "Sin próximos partidos"
→ Normal si no hay partidos programados en los próximos 7 días

---

## 📊 Reglas Activas

El sistema tiene **3 reglas validadas** con ROI positivo:

1. **Local_Invicto_Favorito** (80.7% win rate, +5.1% ROI)
2. **Favorito_Local_Forma** (78.9% win rate, +7.8% ROI)
3. **Visitante_Invicto** (56.9% win rate, +13.4% ROI)

**ROI anual esperado:** ~9.5%

---

## 🎯 ¿Qué Hace el Sistema?

1. **Obtiene próximos partidos** de La Liga (API-Sports o TheSportsDB)
2. **Calcula features** (forma, rachas, promedios de goles)
3. **Evalúa reglas** validadas estadísticamente
4. **Calcula stake óptimo** con Kelly fraccionado
5. **Envía alerta por email** si detecta oportunidad

Todo automático, cada 24 horas.

---

**¡Listo! El sistema está operativo.** 🚀

Para más detalles, consulta el [README.md](README.md) completo.


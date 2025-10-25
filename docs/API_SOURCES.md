# Fuentes de Datos - APIs Disponibles

## 1. API-Sports.io (Principal)
- **URL Base:** https://v3.football.api-sports.io/
- **Tipo:** Premium (con plan gratuito limitado)
- **Límite gratuito:** 100 requests/día
- **Cobertura:** La Liga completa con estadísticas detalladas
- **Endpoints clave:**
  - `/fixtures` - Próximos partidos y resultados
  - `/fixtures/statistics` - Estadísticas detalladas por partido
  - `/teams/statistics` - Estadísticas de equipos
  - `/standings` - Clasificación de la liga

## 2. TheSportsDB (Respaldo gratuito)
- **URL Base:** https://www.thesportsdb.com/api/v1/json/3/
- **Tipo:** Gratuito (con opción premium)
- **Límite:** Sin límite estricto en plan gratuito
- **ID La Liga:** 4335
- **Endpoints clave:**
  - `eventsnextleague.php?id=4335` - Próximos partidos
  - `eventspastleague.php?id=4335` - Resultados pasados
  - `lookupteam.php?id={team_id}` - Info de equipo
  - `lookupevent.php?id={event_id}` - Detalles de partido

## 3. Football-Data.co.uk (Datos históricos)
- **URL Base:** https://www.football-data.co.uk/
- **Tipo:** Gratuito (CSV)
- **Cobertura:** Datos históricos completos desde 1993
- **Formato:** CSV descargables por temporada
- **Ventaja:** Incluye cuotas de múltiples casas de apuestas

## Estrategia de Fallback

1. **Primario:** API-Sports.io (datos en tiempo real, estadísticas detalladas)
2. **Secundario:** TheSportsDB (si se agota el límite de API-Sports)
3. **Histórico:** Football-Data.co.uk (para backtest y datos pasados)


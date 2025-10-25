# 🚀 Guía de Despliegue Permanente en Render.com

## 📋 Resumen

Esta guía te mostrará cómo desplegar tu sistema de alertas de forma **permanente y gratuita** en Render.com. El proceso toma aproximadamente **10 minutos** y no requiere conocimientos técnicos avanzados.

---

## ✅ Ventajas de Render.com

- ✅ **Completamente gratuito** (tier gratuito permanente)
- ✅ **Disponible 24/7** (tu sitio nunca se apaga)
- ✅ **URL permanente** (no cambia nunca)
- ✅ **Actualizaciones automáticas** (cada vez que hagas cambios)
- ✅ **SSL gratis** (HTTPS incluido)
- ✅ **Sin tarjeta de crédito** requerida

---

## 📝 Paso 1: Crear Cuenta en GitHub (5 minutos)

GitHub es donde guardaremos el código del sistema.

1. **Ve a** https://github.com/signup
2. **Regístrate** con tu email (puedes usar marcosvalenciagarcia@gmail.com)
3. **Verifica tu email**
4. **Completa el perfil** (puedes saltar las preguntas opcionales)

---

## 📤 Paso 2: Subir el Código a GitHub (3 minutos)

### Opción A: Desde la Web (Más Fácil)

1. **Inicia sesión en GitHub**
2. **Haz clic en el botón "+" arriba a la derecha** y selecciona "New repository"
3. **Configura el repositorio:**
   - **Nombre:** `laliga-betting-system`
   - **Descripción:** "Sistema de alertas de apuestas deportivas para La Liga"
   - **Visibilidad:** Privado (recomendado) o Público
   - **NO marques** "Initialize this repository with a README"
4. **Haz clic en "Create repository"**

5. **Sube los archivos:**
   - Descarga el archivo `laliga-betting-system-v2.0-COMPLETO.tar.gz` que te proporcioné
   - Descomprímelo en tu computadora
   - En la página del repositorio de GitHub, haz clic en "uploading an existing file"
   - **Arrastra TODOS los archivos y carpetas** del sistema
   - Escribe un mensaje: "Subida inicial del sistema"
   - Haz clic en "Commit changes"

### Opción B: Desde Manus (Automático)

Si prefieres que yo lo haga automáticamente, necesito que:

1. Ve a https://github.com/settings/tokens/new
2. Crea un token con permisos de "repo"
3. Cópialo y dámelo (lo usaré solo para subir el código)

---

## 🌐 Paso 3: Desplegar en Render.com (2 minutos)

1. **Ve a** https://render.com/
2. **Haz clic en "Get Started"** (o "Sign Up")
3. **Selecciona "Sign up with GitHub"**
4. **Autoriza a Render** para acceder a tu cuenta de GitHub

5. **En el Dashboard de Render:**
   - Haz clic en **"New +"** → **"Web Service"**
   - Selecciona **"Connect a repository"**
   - Busca y selecciona **`laliga-betting-system`**
   - Haz clic en **"Connect"**

6. **Configura el servicio:**
   - **Name:** `laliga-betting-alerts` (o el nombre que prefieras)
   - **Region:** Frankfurt (más cercano a España)
   - **Branch:** `master` (o `main`)
   - **Root Directory:** (déjalo vacío)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT web.app:app`
   - **Instance Type:** **Free** ⚠️ ¡MUY IMPORTANTE!

7. **Variables de Entorno (Environment Variables):**
   
   Haz clic en "Advanced" y añade estas dos variables:
   
   - **Nombre:** `API_SPORTS_KEY`  
     **Valor:** (tu API key de API-Sports.io)
   
   - **Nombre:** `EMAIL_PASSWORD`  
     **Valor:** (tu contraseña de aplicación de Gmail)

8. **Haz clic en "Create Web Service"**

---

## ⏳ Paso 4: Esperar el Despliegue (3-5 minutos)

Render empezará a construir y desplegar tu aplicación. Verás un log en tiempo real.

Cuando termine, verás:
- ✅ "Your service is live"
- Una URL como: `https://laliga-betting-alerts.onrender.com`

**¡Esa es tu URL permanente!** 🎉

---

## 🎯 Paso 5: Configurar el Sistema (2 minutos)

1. **Abre tu URL** (ej: `https://laliga-betting-alerts.onrender.com`)
2. **Haz clic en "⚙️ Configuración"**
3. **Introduce:**
   - Tu **API Key de API-Sports.io**
   - Tu **Contraseña de Aplicación de Gmail**
4. **Guarda**

**¡Listo!** El sistema ya está operativo 24/7.

---

## 📧 Uso Diario

Desde cualquier dispositivo (Chromebook, móvil, tablet):

1. **Abre tu URL**
2. **Haz clic en "🎯 Evaluar Partidos Ahora"**
3. El sistema:
   - Obtiene próximos partidos de La Liga
   - Los evalúa contra las reglas validadas
   - Te envía un email si encuentra oportunidades

**Recomendación:** Hazlo una vez al día para estar al tanto de nuevos partidos.

---

## 🔄 Automatización (Opcional)

Si quieres que el sistema se ejecute automáticamente cada día:

1. **En Render Dashboard**, ve a tu servicio
2. **Haz clic en "Cron Jobs"** (en el menú izquierdo)
3. **Crea un nuevo Cron Job:**
   - **Name:** `daily-evaluation`
   - **Command:** `python scripts/start_monitor.py`
   - **Schedule:** `0 9 * * *` (todos los días a las 9:00 AM)

---

## ⚠️ Notas Importantes

### Tier Gratuito de Render

- ✅ **Siempre gratuito**
- ✅ **750 horas/mes** (suficiente para 24/7)
- ⚠️ **Se duerme después de 15 minutos de inactividad**
- ⚠️ **Tarda ~30 segundos en despertar** la primera vez que lo visitas

**Solución:** Si quieres que esté siempre despierto, puedes:
1. Usar un servicio como UptimeRobot (gratuito) para hacer ping cada 5 minutos
2. O simplemente acepta el delay de 30 segundos cuando lo visites

### Límites de API-Sports

- Plan gratuito: 100 requests/día
- El sistema usa fallback automático a TheSportsDB si se agota

### Seguridad

- Tus credenciales están seguras en las variables de entorno de Render
- Nadie más puede verlas
- El repositorio puede ser privado

---

## 🆘 Solución de Problemas

### "Build failed"
→ Verifica que subiste TODOS los archivos, incluyendo `requirements.txt` y `render.yaml`

### "Application error"
→ Revisa los logs en Render Dashboard. Probablemente faltan las variables de entorno.

### "No se conecta a la API"
→ Verifica que añadiste correctamente `API_SPORTS_KEY` en las variables de entorno.

### "No envía emails"
→ Verifica que añadiste correctamente `EMAIL_PASSWORD` y que es una contraseña de aplicación de Gmail.

---

## 📞 Contacto

Si tienes problemas con el despliegue, puedes:
1. Revisar los logs en Render Dashboard
2. Contactarme para ayuda

---

## 🎉 ¡Felicidades!

Una vez completados estos pasos, tendrás:

✅ Un sistema de alertas funcionando 24/7  
✅ Una URL permanente accesible desde cualquier dispositivo  
✅ Actualizaciones automáticas cuando hagas cambios  
✅ Todo completamente gratis  

**Tu URL será algo como:** `https://laliga-betting-alerts.onrender.com`

¡Disfruta del sistema! ⚽🎯


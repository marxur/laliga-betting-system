> # ⚙️ Guía de Instalación y Configuración
> 
> Sigue estos pasos para instalar y configurar el sistema en tu entorno local.
> 
> ---
> 
> ## 📋 Prerrequisitos
> 
> - Python 3.9 o superior
> - `pip` (gestor de paquetes de Python)
> 
> ---
> 
> ## 🛠️ Pasos de Instalación
> 
> ### Paso 1: Clonar el Repositorio
> 
> Abre tu terminal y clona este repositorio en tu máquina local:
> 
> ```bash
> git clone <URL_DEL_REPOSITORIO>
> cd laliga-betting-system
> ```
> 
> ### Paso 2: Instalar Dependencias
> 
> El proyecto utiliza un conjunto de librerías de Python listadas en el archivo `requirements.txt`. Instálalas usando `pip`:
> 
> ```bash
> pip install -r requirements.txt
> ```
> 
> Esto instalará `pandas`, `numpy`, `scipy`, `requests` y `pyarrow`.
> 
> ### Paso 3: Configurar Alertas por Email (Crítico)
> 
> Para que el sistema pueda enviarte alertas, necesitas configurar tus credenciales de email. El sistema está pre-configurado para usar **Gmail**.
> 
> 1.  **Abre el archivo de configuración:** `src/config.py`
> 
> 2.  **Modifica la sección `AlertConfig`:**
> 
>     ```python
>     @dataclass
>     class AlertConfig:
>         # ...
>         sender_email: str = "tu_email@gmail.com"  # 👈 TU EMAIL DE GMAIL
>         sender_password: str = "tu_app_password" # 👈 TU CONTRASEÑA DE APLICACIÓN
>         receiver_email: str = "tu_email_destino@gmail.com" # 👈 EMAIL DONDE RECIBIRÁS LAS ALERTAS
>     ```
> 
> 3.  **Generar una Contraseña de Aplicación en Gmail:**
> 
>     -   **IMPORTANTE:** No puedes usar tu contraseña normal de Gmail. Debes generar una "App Password".
>     -   Ve a la configuración de tu cuenta de Google: [myaccount.google.com](https://myaccount.google.com/)
>     -   Activa la **Verificación en 2 Pasos** si no la tienes activada.
>     -   Ve a la sección **Seguridad** y busca **Contraseñas de aplicaciones**.
>     -   Genera una nueva contraseña para una aplicación personalizada (puedes llamarla "SistemaApuestas").
>     -   Google te dará una contraseña de 16 caracteres. **Copia y pégala** en el campo `sender_password`.
> 
> ### Paso 4: Verificar la Instalación
> 
> Ejecuta el script de backtest principal. Esto descargará todos los datos necesarios y correrá las pruebas, confirmando que todo está configurado correctamente.
> 
> ```bash
> python scripts/run_backtest.py
> ```
> 
> Si la ejecución se completa sin errores y ves el resumen del backtest en la consola, ¡la instalación ha sido un éxito!
> 
> ---
> 
> ## ⚙️ (Opcional) Automatización con Cron Job
> 
> Para mantener los datos actualizados automáticamente, puedes configurar un cron job que ejecute el script `update_data.py` periódicamente.
> 
> 1.  Abre tu editor de crontab:
>     ```bash
>     crontab -e
>     ```
> 
> 2.  Añade la siguiente línea para que se ejecute todos los días a las 3:00 AM:
>     ```cron
>     0 3 * * * /usr/bin/python3 /ruta/completa/a/laliga-betting-system/scripts/update_data.py >> /ruta/completa/a/laliga-betting-system/outputs/logs/cron.log 2>&1
>     ```
> 
>     -   **Recuerda** reemplazar `/ruta/completa/a/` con la ruta absoluta a la carpeta del proyecto.
> 
> ---
> 
> ## ❓ Solución de Problemas
> 
> -   **`ImportError`**: Asegúrate de haber instalado las dependencias con `pip install -r requirements.txt`.
> -   **Error de autenticación SMTP**: Verifica que has usado una **contraseña de aplicación** de Gmail y no tu contraseña normal. Asegúrate también de que la verificación en 2 pasos esté activada.
> -   **Error de descarga de datos**: Comprueba tu conexión a internet y que `football-data.co.uk` esté accesible.


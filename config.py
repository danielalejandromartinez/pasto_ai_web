import os

class Config:
    """Clase para configurar la aplicación Flask."""
    
    # Configuración de Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    
    # --- ¡PON TUS CREDENCIALES REALES AQUÍ! ---
    # Reemplaza con tu dirección de correo de Gmail completa.
    MAIL_USERNAME = "danielpandiaco2020@gmail.com"
    
    # Reemplaza con tu contraseña de aplicación de 16 letras (sin espacios).
    MAIL_PASSWORD = "clamdlshnqpgxnci"
    # ----------------------------------------
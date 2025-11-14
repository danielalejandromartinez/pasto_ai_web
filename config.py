import os

class Config:
    """Clase para configurar la aplicación Flask."""
    
    # Configuración general de Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    
    # Configuración de credenciales inteligente
    # 1. Intenta leer la variable de entorno (para Render).
    # 2. Si no la encuentra, usa el valor que está escrito aquí (para tu PC local).
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') or "danielpandiaco2020@gmail.com"
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') or "clamdlshnqpgxnci"
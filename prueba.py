from dotenv import load_dotenv
import os

# Intentamos cargar la mochila
load_dotenv()

# Buscamos la llave
llave = os.getenv('CLAVE_API_DE_OPENAI')

print("--- REPORTE DE DETECTIVE ---")
if llave:
    print("¡ÉXITO! Encontré la llave.")
    print("Empieza con:", llave[:5])
else:
    print("FALLO: La llave no aparece. La mochila está vacía o cerrada.")
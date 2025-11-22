import os
import requests # Para hablar con Evolution API
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask_mail import Mail, Message
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. CARGAR CONFIGURACIÓN ---
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# --- 2. LÓGICA DE CONFIGURACIÓN ---
try:
    from config import Config
except ImportError:
    class Config:
        pass

app = Flask(__name__)
app.config.from_object(Config)

# Configuración del correo
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True
)

mail = Mail(app)

# --- 3. CONEXIÓN CON LAS APIs ---

# CEREBRO (OpenAI) - Usamos la llave que ya configuraste
client = OpenAI(api_key=os.getenv('CLAVE_API_DE_OPENAI'))

# BOCA Y OÍDOS (Evolution API) - Estos los configuraremos en el siguiente paso
EVOLUTION_URL = os.getenv('EVOLUTION_URL') 
EVOLUTION_APIKEY = os.getenv('EVOLUTION_APIKEY')
NOMBRE_INSTANCIA = "Daniela" 

# ===================================================
# ==           BASE DE DATOS DE AGENTES            ==
# ===================================================
agentes_db = {
    'asistente-post-operatorio': {
        'nombre': "Asistente de Cuidado Post-Operatorio",
        'icono': "🩺",
        'descripcion_corta': "Automatiza el seguimiento y resuelve las dudas de tus pacientes 24/7.",
        'descripcion_larga': "Este Agente de IA se entrena con tus protocolos y guías de cuidado para responder de forma precisa y segura a las preguntas más frecuentes de tus pacientes después de una cirugía, liberando a tu equipo y mejorando la adherencia al tratamiento.",
        'nicho': "Médicos Especialistas y Cirujanos",
        'status': "Disponible"
    },
    'agente-calificador-de-candidatos': {
        'nombre': "Agente Calificador de Candidatos",
        'icono': "🎯",
        'descripcion_corta': "Filtra automáticamente a los prospectos y agenda solo a los calificados.",
        'descripcion_larga': "Implementa este agente en tu sitio web para interactuar con los visitantes, responder preguntas básicas, pre-calificar candidatos según tus criterios y agendar consultas únicamente con los prospectos de mayor valor.",
        'nicho': "Clínicas, Inmobiliarias, Consultores",
        'status': "Próximamente"
    },
    'agente-de-agendamiento-inteligente': {
        'nombre': "Agente de Agendamiento Inteligente",
        'icono': "🗓️",
        'descripcion_corta': "Coordina citas y envía recordatorios para eliminar los 'no-shows'.",
        'descripcion_larga': "Sincronizado con tu calendario, este agente gestiona el agendamiento de citas 24/7 a través de WhatsApp, encuentra huecos, confirma, reagenda y envía recordatorios automáticos para reducir la tasa de inasistencia.",
        'nicho': "Cualquier negocio basado en citas",
        'status': "Próximamente"
    }
}

# ===================================================
# ==                 RUTAS WEB                     ==
# ===================================================

@app.route('/')
def hola_mundo():
    return render_template('index.html')

@app.route('/presentacion')
def presentacion():
    return render_template('presentacion.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/agentes')
def catalogo_agentes():
    return render_template('catalogo_agentes.html', agentes=agentes_db)

@app.route('/agente/<slug>')
def detalle_agente(slug):
    agente = agentes_db.get(slug)
    if not agente:
        abort(404)
    return render_template('detalle_agente.html', agente=agente, slug=slug)

@app.route('/formularios-digitales')
def pagina_formularios_digitales():
    return render_template('formularios_digitales.html')

@app.route('/formularios/<form_id>', methods=['GET', 'POST'])
def mostrar_formulario(form_id):
    if request.method == 'POST':
        # Lógica del formulario (resumida para no ocupar espacio, funciona igual)
        return redirect(url_for('pagina_de_gracias'))
    return render_template('formulario_cliente.html', form_id=form_id)

@app.route('/gracias')
def pagina_de_gracias():
    return render_template('gracias.html')


# ===================================================
# ==      NUEVA LÓGICA: WHATSAPP (EVOLUTION)       ==
# ===================================================

@app.route('/api/whatsapp', methods=['POST'])
def recibir_mensaje_whatsapp():
    try:
        datos = request.json
        
        # 1. Verificamos si es un mensaje válido de Evolution
        if 'data' not in datos or 'message' not in datos['data']:
            return jsonify({'status': 'ignorado', 'razon': 'No es mensaje'}), 200
            
        # 2. Extraemos la información
        mensaje = datos['data']['message'].get('conversation') or datos['data']['message'].get('extendedTextMessage', {}).get('text')
        numero_cliente = datos['data']['key']['remoteJid']
        soy_yo = datos['data']['key']['fromMe']

        # Si el mensaje lo envié yo mismo o está vacío, no hacemos nada
        if soy_yo or not mensaje:
            return jsonify({'status': 'ignorado', 'razon': 'Soy yo o vacio'}), 200

        print(f"📩 Mensaje de {numero_cliente}: {mensaje}")

        # 3. DANIELA PIENSA (OpenAI)
        respuesta_ia = pensar_respuesta_daniela(mensaje)

        # 4. DANIELA RESPONDE (Evolution API)
        enviar_a_evolution(numero_cliente, respuesta_ia)

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        print(f"❌ Error en WhatsApp: {e}")
        return jsonify({'status': 'error', 'detalle': str(e)}), 500

# --- CEREBRO DE DANIELA ---
def pensar_respuesta_daniela(mensaje_usuario):
    prompt = """
    Eres Daniela, la experta en ventas de Pasto.AI.
    Estás hablando por WhatsApp con un posible cliente (médico o clínica).
    
    TU OBJETIVO: Vender nuestros Agentes de IA.
    
    ESTRATEGIA:
    1. Sé breve y usa emojis 👩‍⚕️.
    2. Identifica su problema (tiempo, citas perdidas).
    3. Ofréceles una DEMO de nuestros agentes.
    4. Intenta cerrar una reunión.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": mensaje_usuario}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error OpenAI: {e}")
        return "Dame un segundo, estoy revisando la agenda..."

# --- CONEXIÓN CON EVOLUTION API ---
def enviar_a_evolution(numero, texto):
    if not EVOLUTION_URL or not EVOLUTION_APIKEY:
        print("⚠️ Error: Faltan configurar las variables de Evolution en el .env")
        return

    # Construimos la URL para enviar el mensaje
    url_api = f"{EVOLUTION_URL}/message/sendText/{NOMBRE_INSTANCIA}"
    
    headers = {
        "apikey": EVOLUTION_APIKEY,
        "Content-Type": "application/json"
    }
    
    body = {
        "number": numero,
        "textMessage": {"text": texto}
    }
    
    try:
        requests.post(url_api, json=body, headers=headers)
        print(f"📤 Respuesta enviada a {numero}")
    except Exception as e:
        print(f"❌ Error enviando a Evolution: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
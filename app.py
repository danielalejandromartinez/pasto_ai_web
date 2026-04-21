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
client = OpenAI(api_key=os.getenv('CLAVE_API_DE_OPENAI') or "llave_de_juguete")

# BOCA Y OÍDOS (Evolution API) - Estos los configuraremos en el siguiente paso
EVOLUTION_URL = os.getenv('EVOLUTION_URL') 
EVOLUTION_APIKEY = os.getenv('EVOLUTION_APIKEY')
NOMBRE_INSTANCIA = "Daniela" 

# ===================================================
# ==           BASE DE DATOS DE AGENTES            ==
# ===================================================
agentes_db = {
    'asistente-post-operatorio': {
        'nombre': "Asistente Médico Post-Op",
        'industria': "Salud",
        'icono': "🩺",
        'descripcion_larga': "Este Agente de IA se entrena con tus protocolos para cuidar a tus pacientes después de una cirugía, resolviendo dudas y agendando controles automáticamente.",
        'metrica': "-30% Inasistencias",
        'status': "Disponible",
        'wa_mensaje': "Hola Daniela, me interesa el sistema de Salud para mi clínica.",
        'stats': {'ventas': '124 citas', 'clientes': '45 pac.', 'ahorro': '12h/sem'},
        'conversacion': [
            {'type': 'patient', 'text': 'Hola Dr., disculpe la hora. Me duele la zona de la cirugía y no sé si deba tomarme la pastilla roja o la blanca ahora.', 'time': '11:15 p. m.'},
            {'type': 'agent', 'text': '¡Hola! Entiendo su preocupación. Soy el Asistente Virtual del Dr. Ramos. Para darle la instrucción exacta, ¿podría confirmarme su nombre completo?', 'time': '11:15 p. m.'},
            {'type': 'patient', 'text': 'Soy Carlos Pérez.', 'time': '11:16 p. m.'},
            {'type': 'agent', 'text': 'Gracias, Carlos. Según su historial de hoy, la pastilla blanca es el analgésico y debe tomarla ahora con comida. La roja es el antibiótico de la mañana. ¿Desea que le agende una llamada de control mañana a las 10:00 am?', 'time': '11:16 p. m.'},
            {'type': 'patient', 'text': '¡Ah, perfecto! Sí, por favor, a las 10:00 am está bien. Muchas gracias.', 'time': '11:17 p. m.'},
            {'type': 'agent', 'text': 'Listo, Carlos. Cita de control agendada para las 10:00 am. Siga descansando. 🌙', 'time': '11:17 p. m.'}
        ]
    },
    'ventas-gastronomia': {
        'nombre': "Agente de Ventas Gourmet",
        'industria': "Gastronomía",
        'icono': "🍰",
        'descripcion_larga': "Atiende pedidos, resuelve dudas sobre el menú y gestiona pagos automáticamente, enviando toda la data a tu panel de control.",
        'metrica': "+40% Conversión",
        'status': "Disponible",
        'wa_mensaje': "Hola Daniela, quiero el Agente de Ventas para mi Pastelería.",
        'stats': {'ventas': '$4.2M COP', 'clientes': '182 ped.', 'ahorro': '20h/sem'},
        'conversacion': [
            {'type': 'patient', 'text': 'Buenas tardes, ¿tienen disponibilidad de tortas de chocolate para hoy mismo? Es para un regalo.', 'time': '3:00 p. m.'},
            {'type': 'agent', 'text': '¡Hola! 👋 Qué buen detalle. Soy el Asistente de Pastelería Gourmet. Sí, tenemos nuestra "Selva Negra Premium" lista para salir. ¿Para cuántas personas la necesitas?', 'time': '3:00 p. m.'},
            {'type': 'patient', 'text': 'Para 15 personas. ¿Cuánto cuesta con envío al norte?', 'time': '3:01 p. m.'},
            {'type': 'agent', 'text': 'Esa tiene un valor de $45 USD y el envío al norte es de $5 USD. Incluye tarjeta de regalo personalizada. ¿Te gustaría proceder con el pago por aquí para asegurar tu reserva?', 'time': '3:01 p. m.'},
            {'type': 'patient', 'text': 'Sí, envíame los datos de pago por favor.', 'time': '3:02 p. m.'},
            {'type': 'agent', 'text': '¡Excelente! Aquí tienes el link de pago seguro. Una vez realizado, registraré tu pedido en cocina automáticamente. 👩‍🍳', 'time': '3:02 p. m.'}
        ]
    },
    'eventos-sociales': {
        'nombre': "Planner Intelligence",
        'industria': "Eventos",
        'icono': "🥂",
        'descripcion_larga': "Gestiona cotizaciones de eventos, califica prospectos y agenda visitas al salón 24/7 sin intervención humana.",
        'metrica': "Respuesta 24/7",
        'status': "Disponible",
        'wa_mensaje': "Hola Daniela, vi el Agente de Eventos y quiero implementarlo en mi salón.",
        'stats': {'ventas': '8 eventos', 'clientes': '240 cot.', 'ahorro': '35h/sem'},
        'conversacion': [
            {'type': 'patient', 'text': 'Hola, me gustaría información para celebrar una boda el próximo año.', 'time': '10:00 a. m.'},
            {'type': 'agent', 'text': '¡Felicidades por su compromiso! 💍 Soy el Planner Inteligente del Salón. Para enviarle una propuesta exacta, ¿tienen ya una fecha y cuántos invitados?', 'time': '10:00 a. m.'},
            {'type': 'patient', 'text': 'Sería para Agosto y unos 120 invitados.', 'time': '10:01 a. m.'},
            {'type': 'agent', 'text': 'Perfecto. Para 120 invitados en Agosto, el "Paquete Platinum" es el ideal. ¿Les gustaría agendar una visita guiada al salón este sábado a las 4:00 pm para verlo en vivo?', 'time': '10:01 a. m.'},
            {'type': 'patient', 'text': 'Sí, me parece muy bien a las 4:00 pm.', 'time': '10:02 a. m.'},
            {'type': 'agent', 'text': 'Cita agendada para el sábado a las 4:00 pm. Les acabo de enviar la ubicación exacta. ¡Nos vemos pronto! ✨', 'time': '10:02 a. m.'}
        ]
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

@app.route('/soluciones')
def pagina_soluciones():
    return render_template('soluciones.html')

@app.route('/formularios/<form_id>', methods=['GET', 'POST'])
def mostrar_formulario(form_id):
    if request.method == 'POST':
        # Lógica del formulario (resumida para no ocupar espacio, funciona igual)
        return redirect(url_for('pagina_de_gracias'))
    return render_template('formulario_cliente.html', form_id=form_id)

@app.route('/gracias')
def pagina_de_gracias():
    return render_template('gracias.html')

@app.route('/contacto')
def pagina_contacto():
    return render_template('contacto.html')


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
import os
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_mail import Mail, Message
from config import Config  # <-- Importamos nuestra nueva clase Config

app = Flask(__name__)

# Le decimos a Flask que cargue toda la configuración desde el objeto Config.
app.config.from_object(Config)

# Inicializamos las extensiones DESPUÉS de que la app esté configurada.
mail = Mail(app)


# ===================================================
# ==     NUESTRA "BASE DE DATOS" DE AGENTES         ==
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
# ==                 RUTAS DE LA APP               ==
# ===================================================

@app.route('/')
def hola_mundo():
    return render_template('index.html')

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
    return render_template('detalle_agente.html', agente=agente)

@app.route('/formularios-digitales')
def pagina_formularios_digitales():
    return render_template('formularios_digitales.html')

@app.route('/formularios/<form_id>', methods=['GET', 'POST'])
def mostrar_formulario(form_id):
    if request.method == 'POST':
        nombre = request.form.get('full_name')
        fecha_nacimiento = request.form.get('birth_date')
        telefono = request.form.get('phone_number')
        email = request.form.get('email')
        motivo = request.form.get('reason')

        destinatario_cliente = "paolayela55@gmail.com" # ¡RECUERDA CAMBIAR ESTO!
        
        cuerpo_del_mensaje = f"""
        NUEVO FORMULARIO DE ADMISIÓN RECIBIDO
        --------------------------------------
        Cliente: {form_id}
        DATOS DEL PACIENTE:
        - Nombre Completo: {nombre}
        - Fecha de Nacimiento: {fecha_nacimiento}
        - Teléfono: {telefono}
        - Email de Contacto: {email}
        MOTIVO DE LA CONSULTA:
        - {motivo}
        """
        
        msg = Message(
            subject=f"Nuevo Formulario Recibido de: {nombre}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[destinatario_cliente]
        )
        msg.body = cuerpo_del_mensaje
        mail.send(msg)
        return redirect(url_for('pagina_de_gracias'))

    return render_template('formulario_cliente.html', form_id=form_id)

@app.route('/gracias')
def pagina_de_gracias():
    return render_template('gracias.html')

# ===================================================
# ==      CÓDIGO PARA ARRANCAR LA APLICACIÓN       ==
# ===================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
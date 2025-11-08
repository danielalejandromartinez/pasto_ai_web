import os
from dotenv import load_dotenv # Importamos la nueva librería
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message

load_dotenv() # Cargamos las variables del archivo .env

app = Flask(__name__)

# ===================================================
# ==     CONFIGURACIÓN DE CORREO SEGURA            ==
# ===================================================
# Ahora leemos las credenciales desde el entorno, no desde el código.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# --- (El resto de las rutas no cambian) ---

@app.route('/')
def hola_mundo():
    return render_template('index.html')

@app.route('/soluciones')
def soluciones():
    return render_template('soluciones.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

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

        # Para la prueba, puedes poner tu email aquí o leerlo también de .env si quieres
        destinatario_cliente = "correo-destino-prueba@ejemplo.com" # ¡RECUERDA CAMBIAR ESTO!
        
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
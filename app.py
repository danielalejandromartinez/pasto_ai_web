from flask import Flask, render_template

app = Flask(__name__)


# --- RUTA PARA LA PÁGINA DE INICIO ---
@app.route('/')
def hola_mundo():
    return render_template('index.html')


# --- RUTA PARA LA PÁGINA DE SOLUCIONES ---
@app.route('/soluciones')
def soluciones():
    return render_template('soluciones.html')
# --- RUTA PARA LA PÁGINA DE NOSOTROS ---
@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

# --- CÓDIGO PARA ARRANCAR LA APLICACIÓN ---
if __name__ == '__main__':
    app.run(debug=True)
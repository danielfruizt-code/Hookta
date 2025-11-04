from flask import Flask, render_template, request, redirect, url_for, session
from config.db import get_db_connection

app = Flask(__name__)
app.secret_key = "hootka_secret_key"

preguntas = []

@app.route('/')
def home():
    if 'usuario' in session:
        return redirect(url_for('crear_pregunta'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND password=%s", (usuario, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session['usuario'] = usuario
                return redirect(url_for('crear_pregunta'))
            else:
                return render_template('login.html', error="Credenciales inválidas")
        else:
            return render_template('login.html', error="No se pudo conectar a la base de datos")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/crear_pregunta', methods=['GET', 'POST'])
def crear_pregunta():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        pregunta = request.form['pregunta']
        opciones = [
            request.form['opcion1'],
            request.form['opcion2'],
            request.form['opcion3'],
            request.form['opcion4'],
        ]
        correcta = request.form['correcta']

        preguntas.append({
            "pregunta": pregunta,
            "opciones": opciones,
            "correcta": correcta
        })

        return render_template('crear_pregunta.html', mensaje="✅ Pregunta guardada!", preguntas=preguntas)

    return render_template('crear_pregunta.html', preguntas=preguntas)

# 🔹 Nueva ruta para vaciar todas las preguntas
@app.route('/vaciar', methods=['POST'])
def vaciar_preguntas():
    global preguntas
    preguntas.clear()
    return redirect(url_for('crear_pregunta'))

if __name__ == "__main__":
    app.run(port=5000, debug=True)

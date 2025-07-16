from flask import Flask, render_template, request
from basedatos import db, Log, init_db, ordenar_por_fecha_y_hora
from webhook import manejar_webhook_get, manejar_webhook_post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar base de datos
init_db(app)

@app.route('/')
def index():
    registros = Log.query.all()
    ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html', registros=ordenados)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return manejar_webhook_get(request)
    elif request.method == 'POST':
        return manejar_webhook_post(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

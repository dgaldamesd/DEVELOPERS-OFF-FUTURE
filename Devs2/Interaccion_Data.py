from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://Alan:Agonzalez3@localhost/Data_base_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)

@app.route('/')
def index():
    # Obtener todos los usuarios desde la base de datos (método GET)
    usuarios = Usuario.query.all()
    return render_template('index.html', usuarios=usuarios)

@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    # Agregar un nuevo usuario a la base de datos (método POST)
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        

        nuevo_usuario = Usuario(nombre=nombre, email=email)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return "Usuario agregado correctamente"
@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    # Obtener todos los usuarios desde la base de datos y convertirlos a formato JSON
    usuarios = Usuario.query.all()
    usuarios_json = [{'id': usuario.id, 'nombre': usuario.nombre, 'email': usuario.email} for usuario in usuarios]
    
    return jsonify({'usuarios': usuarios_json})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5050, debug=True)
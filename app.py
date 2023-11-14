from flask import Flask, render_template, request, redirect, flash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SECRET_KEY'] = 'senha'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    matricula = db.Column(db.String(20), unique = True, nullable = False)
    senha = db.Column(db.String(20), nullable = False)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique = True, nullable = False)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    editora = db.Column(db.String(200), nullable=False)
    ano = db.Column(db.String(100), nullable=False)
    disponivel = db.Column(db.Boolean, default=True)
    
class Emprestimo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    data_emprestimo = db.Column(db.DateTime, default=datetime.utcnow)
    prazo_devolucao = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(days=5))
    data_devolucao = db.Column(db.DateTime)
    multa = db.Column(db.Float, default=0.0)
    finalizado = db.Column(db.Boolean)

    usuario = db.relationship('Usuario', backref=db.backref('emprestimos', lazy=True))
    livro = db.relationship('Livro', backref=db.backref('emprestimos', lazy=True))
    

@app.route('/')
def index():
    return 'Página Inicial'

    
if __name__ == '__main__':
    app.run(debug=True)
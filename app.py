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
  
#ROTAS  
#página inicial
@app.route('/')
def index():
    return render_template('login.html')

#página de login
@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == 'POST':
        matricula = request.form['matricula']
        senha = request.form['senha']
        
        usuario = Usuario.query.filter_by(matricula = matricula, senha = senha).first()
        
        if usuario:
            flash(f'Olá {usuario.nome}!')
            return redirect('/usuario')
        
        elif matricula == 'adm' and senha == '000':
            return redirect('/adm')
        
        else:
            flash('Usuário Inválido!')
            return redirect('/')
        
    return render_template('login.html')

#Página Inicial (Usuário)
@app.route('/usuario')
def pagina_usuario():
    return render_template('usuario.html')

#Página Inicial (Administrador)
@app.route('/adm')
def pagina_administrador():
    return render_template('adm.html')

#cadastrar usuario 
@app.route('/adm/usuarios/cadastrar', methods=['GET','POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        email = request.form['email']
        telefone = request.form['telefone']
        matricula = request.form['matricula']
        senha = request.form['senha']
        if nome and endereco and email and telefone and matricula and senha:
            novo_usuario = Usuario(nome=nome, endereco=endereco, email=email, telefone=telefone, matricula=matricula, senha=senha)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Usuário Cadastrado com Sucesso!')
            return redirect('/adm/usuarios/cadastrar')
    return render_template('cadastrar_usuario.html')

#cadastrar livro
@app.route('/adm/livros/cadastrar', methods=['GET','POST'])
def cadastrar_livro():
    if request.method == 'POST':
        isbn = request.form['isbn']
        titulo = request.form['titulo']
        autor = request.form['autor']
        editora = request.form['editora']
        ano = request.form['ano']
        if isbn and titulo and autor and editora and ano:
            novo_usuario = Livro(isbn=isbn, titulo = titulo, autor = autor, editora = editora, ano = ano)
            db.session.add(novo_usuario)
            db.session.commit()
            flash(f'Livro "{titulo}" Cadastrado com Sucesso!')
            return redirect('/adm/livros/cadastrar')
    return render_template('cadastrar_livro.html')

    
if __name__ == '__main__':
    app.run(debug=True)
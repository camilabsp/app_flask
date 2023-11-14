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

#Função para calcular multa
def calcular_multa(prazo_devolucao, data_atual):
    if data_atual > prazo_devolucao:
        dias = (data_atual - prazo_devolucao).days
        taxa = dias * 1  #(taxa R$1,00 real por dia de atraso)
        return taxa
    return 0
 
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

# Lista todos os usuários
@app.route('/adm/usuarios')
def lista_usuarios():
    usuarios = Usuario.query.all()  
    return render_template('lista_usuarios.html', usuarios=usuarios)

#efetuar empréstimo
@app.route('/adm/emprestimo', methods=['GET', 'POST'])
def emprestimo():
    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        livro_id = request.form.get('livro_id')

        usuario = Usuario.query.get(usuario_id)
        livro = Livro.query.get(livro_id)
        
        # Verifica se o usuário existe, se o usuário tem menos de 3 empréstimos não finalizados,
        # se o livro existe e se o livro está disponível.
        # Se todas as condições forem atendidas, prossegue com o empréstimo.
        
        if usuario and len([e for e in usuario.emprestimos if not e.finalizado]) < 3 and livro and livro.disponivel:
            
            # Cria um novo objeto de Empréstimo no banco de dados associando o usuário e o livro.
            empréstimo = Emprestimo(usuario=usuario, livro=livro)
            db.session.add(empréstimo)
            
            # Marca o livro como indisponível, já que ele está emprestado.
            livro.disponivel = False
            
            # Confirma as alterações no banco de dados
            db.session.commit()
            flash('Livro emprestado com sucesso!')
            
        # Se o usuário já tem 3 empréstimos, exibe uma mensagem informando que não é possível fazer mais empréstimos.
        elif len([e for e in usuario.emprestimos if not e.finalizado]) >= 3:
            flash('Você atingiu o limite máximo de empréstimos.')
        
        # Se nenhuma das condições anteriores for atendida.  
        else:
            flash('Não foi possível realizar o empréstimo.')

    return render_template('emprestimo.html', usuarios=Usuario.query.all(), livros=Livro.query.all())

#Exibe lista de empréstimos
@app.route('/adm/emprestimos', methods=['GET'])
def lista_emprestimos():
    emprestimos = Emprestimo.query.all()
    return render_template('lista_emprestimos.html', emprestimos=emprestimos)

# Rota para a página de devolução
@app.route('/adm/devolucao', methods=['GET', 'POST'])
def devolucao():
    if request.method == 'POST':
        emprestimo_id = request.form.get('emprestimo_id')
        data_devolucao_str = request.form.get('data_devolucao')

        if not emprestimo_id:
            flash('Selecione um empréstimo para devolver.')
        elif not data_devolucao_str:
            flash('Informe a data de devolução.')
        else:
            try:
                emprestimo = Emprestimo.query.get(int(emprestimo_id))
                data_devolucao = datetime.strptime(data_devolucao_str, '%Y-%m-%d')

                if emprestimo:
                    if data_devolucao > emprestimo.prazo_devolucao:
                        # Calcule a multa por atraso
                        taxa = calcular_multa(emprestimo.prazo_devolucao, data_devolucao)
                        emprestimo.multa = taxa
                    else:
                        taxa = 0
                        
                    emprestimo.data_devolucao = data_devolucao

                    # Marca o livro como disponível novamente 
                    
                    livro = emprestimo.livro
                    livro.disponivel = True
                    
                    # Marca o empréstimo como finalizado apenas quando o livro for devolvido
                    if livro.disponivel:
                        emprestimo.finalizado = True
                    

                    db.session.commit()

                    if taxa > 0:
                        flash(f'Livro devolvido com sucesso! Multa por atraso: R$ {taxa:.2f}')
                    else:
                        flash('Livro devolvido com sucesso!')
                else:
                    flash('Empréstimo não encontrado. Verifique as informações.')
            except ValueError:
                flash('Data de devolução inválida.')

    emprestimos = Emprestimo.query.filter_by(finalizado=None).all()
    return render_template('devolucao.html', emprestimos=emprestimos)


if __name__ == '__main__':
    app.run(debug=True)
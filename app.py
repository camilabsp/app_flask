from flask import Flask, render_template, request, redirect, flash, session, url_for
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
    quantidade_exemplares = db.Column(db.Integer, nullable=False)
    
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

#Função para calcular multa por atraso
def calcular_multa(prazo_devolucao, data_devolucao):
    if data_devolucao > prazo_devolucao:
        dias = (data_devolucao - prazo_devolucao).days
        taxa = dias * 1  #(taxa R$1,00 real por dia de atraso)
        return taxa
    return 0
 
adm_logado = False
 
#ROTAS  
#página inicial
@app.route('/')
def index():
    global adm_logado
    adm_logado = False
    return render_template('login.html')

#página de login
@app.route('/login', methods=["GET", "POST"])
def login():
    global adm_logado #usado para identificar se um administrador está ou não logado.
    if request.method == 'POST':
        matricula = request.form['matricula']
        senha = request.form['senha']

        #procura no banco de dados um usuário com matrícula e senha correspondentes aos valores fornecidos no formulário de login
        usuario = Usuario.query.filter_by(matricula=matricula, senha=senha).first()

        #se o usuário existir, ele é autenticado.
        if usuario: 
            session['usuario_id'] = usuario.id  #o id do usuário é arazenado
            return redirect('/usuario')

        #verifica se a matrícula e senha correspondem ao administrador
        elif matricula == 'adm' and senha == '000':
            adm_logado = True #adm_logado é definida como True para indicar que um administrador está logado.
            return redirect('/adm')

        #caso o usuário não esteja cadastrado e nem seja o administrador
        else:
            flash('Usuário Inválido!')
            return redirect('/')

    return render_template('login.html')

#Página Inicial (Usuário)
@app.route('/usuario')
def pagina_usuario():
    
    #verifica o id do usuário. Indica se um usuário está autenticado ou não.
    if 'usuario_id' in session:
        usuario_id = session['usuario_id'] #se o usuário estiver autenticado, salva o ID do usuário.
        usuario = Usuario.query.get(usuario_id) #realiza a consulta no banco
        return render_template('usuario.html', usuario=usuario) 
    else:
        flash('Você precisa fazer login primeiro.')
        return redirect('/')

#Página Inicial (Administrador)
@app.route('/adm')
def pagina_administrador():
    global adm_logado
    
    #verifica se um administrador está logado antes de permitir o acesso.
    if adm_logado == True:
        
        tipo_busca = request.args.get('tipo_busca', 'usuario') #obtém o parâmetro 'tipo_busca' (formulário HTML).
        termo_busca = request.args.get('termo_busca', '') #obtém o parâmetro 'termo_busca', o padrão é uma string (formulário HTML). 

        #verifica se o tipo de busca é por usuário.
        if tipo_busca == 'usuario':
            resultados = Usuario.query.filter(Usuario.nome.contains(termo_busca)).all() #faz consulta no banco para buscar usuário solicitado
            
        #verifica se o tipo de busca é por livro.
        elif tipo_busca == 'livro':
            resultados = Livro.query.filter(Livro.titulo.contains(termo_busca)).all() #faz consulta no banco para buscar livro solicitado
        
        #caso contrario, inicializa com uma lista vazia.
        else:
            resultados = []

        if request.method == 'POST':
            pass
        
        #retorna as variáveis e renderiza o template
        return render_template('adm.html', tipo_busca=tipo_busca, termo_busca=termo_busca, resultados=resultados)
    else:
        flash('Você não tem permissão para acessar essa página')
        return redirect('/')
    

#cadastrar usuario (Permitido apenas para administrador)
@app.route('/adm/usuarios/cadastrar', methods=['GET','POST'])
def cadastrar_usuario():
    global adm_logado
    
    #se o administrador nao estiver logado, redireciona para a página de login.
    if adm_logado == False:
        flash('Você não tem permissão para acessar essa página')
        return redirect('/')
    
    elif request.method == 'POST':
        
        #dados são obtidos através do formulário.
        nome = request.form['nome']
        endereco = request.form['endereco']
        email = request.form['email']
        telefone = request.form['telefone']
        matricula = request.form['matricula']
        senha = request.form['senha']
        
        #verifica se todos os campos do formulário foram preenchidos.
        if nome and endereco and email and telefone and matricula and senha:
            
            #cria um novo objeto (Usuario) com os dados fornecidos no formulário.
            novo_usuario = Usuario(nome=nome, endereco=endereco, email=email, telefone=telefone, matricula=matricula, senha=senha)
            db.session.add(novo_usuario) #adiciona o novo usuário no banco
            db.session.commit() #confirma as mudanças no banco, cadastrando o usuário
            
            flash('Usuário Cadastrado com Sucesso!')
            
            return redirect('/adm/usuarios/cadastrar')
        
    return render_template('cadastrar_usuario.html')



@app.route('/adm/usuarios/editar/<int:user_id>', methods=['GET', 'POST'])
def editar_usuario(user_id):
    
    #consulta o banco de dados para obter o usuario através do id
    usuario = Usuario.query.get(user_id)

    if request.method == 'POST':
        
        #as informações do usuário são atualizadas com os dados fornecidos no formulário.
        usuario.nome = request.form['nome']
        usuario.endereco = request.form['endereco']
        usuario.email = request.form['email']
        usuario.telefone = request.form['telefone']
        usuario.matricula = request.form['matricula']

        
        db.session.commit() #confirma as alterações no banco
        
        return redirect(url_for('lista_usuarios'))

    return render_template('editar_usuario.html', usuario=usuario)


#cadastrar livro (Administrador)
@app.route('/adm/livros/cadastrar', methods=['GET','POST'])
def cadastrar_livro():
    
    global adm_logado
    
    #se o administrador não estiver logado, redireciona para página de login
    if adm_logado == False:
        flash('Você não tem permissão para acessar essa página')
        return redirect('/')
    
    #dados obtidos através do formulário
    elif request.method == 'POST':
        
        isbn = request.form['isbn']
        titulo = request.form['titulo']
        autor = request.form['autor']
        editora = request.form['editora']
        ano = request.form['ano']
        quantidade_exemplares = request.form['quantidade_exemplares']
        
        #verifica se todos os campos estão preenchidos
        if isbn and titulo and autor and editora and ano and quantidade_exemplares:
            
            novo_livro = Livro(isbn=isbn, titulo=titulo, autor=autor, editora=editora, ano=ano, quantidade_exemplares=quantidade_exemplares, disponivel=True) #novo objeto (Livro) é criado com os dados do formulário
            db.session.add(novo_livro) #adiciona novo livro ao banco de dados
            db.session.commit() #confirma alterações
            
            flash(f'Livro "{titulo}" Cadastrado com Sucesso!')
            
            return redirect('/adm/livros/cadastrar')
        
    return render_template('cadastrar_livro.html')


#editar informações dos livros (Administrador)
@app.route('/adm/acervo/editar/<int:livro_id>', methods=['GET', 'POST'])
def editar_livro(livro_id):
    
    #consulta o banco de dados para obter o objeto (Livro) com id correspondente.
    livro = Livro.query.get(livro_id)
    
    #as informações do livro são atualizadas com os dados fornecidos no formulário.
    if request.method == 'POST':
        
        livro.isbn = request.form['isbn']
        livro.titulo = request.form['titulo']
        livro.autor = request.form['autor']
        livro.editora = request.form['editora']
        livro.ano = request.form['ano']
        livro.quantidade_exemplares = request.form['quantidade_exemplares']
        
        db.session.commit() #confirma as alterações no banco.

        return redirect('/adm/acervo')

    return render_template('editar_livro.html', livro=livro)

#renderiza um formulário de edição de informações do usuário (Usuario)
@app.route('/usuario/editar')
def editar_info():
    
    usuario_id = session.get('usuario_id') #obtem o id do usuário através da sessão.
    usuario = Usuario.query.get(usuario_id) #consulta o banco de dados e verifica usuário com o id correspondente.

    return render_template('editar_info.html', usuario=usuario)


#atualiza as informações do usuario (usuario)
@app.route('/usuario/atualizar', methods=['POST'])
def atualizar_informacoes():
    
    #verifica se o usuário está logado e obtem o id dele.
    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        usuario = Usuario.query.get(usuario_id)

        #atualiza (edita) as informações do usuário.
        usuario.nome = request.form['nome']
        usuario.endereco = request.form['endereco']
        usuario.email = request.form['email']
        usuario.telefone = request.form['telefone']
        usuario.senha = request.form['senha']

        db.session.commit() #confirma as alterações no banco de dados.

        flash('Informações do usuário atualizadas com sucesso!')

        return redirect(url_for('pagina_usuario'))

    flash('Você precisa fazer login primeiro.')
    return redirect('/login') #redireciona para a página de login se o usuário não estiver autenticado.


#lista todos os usuários (Administrador)
@app.route('/adm/usuarios')
def lista_usuarios():
    global adm_logado
    
    #verifica se o administrador está logado ou não.
    if adm_logado == True:
        usuarios = Usuario.query.all()  #consulta o banco de dados e retorna todos os usuários. 
        return render_template('lista_usuarios.html', usuarios=usuarios)
    else:
        flash('Você não tem acesso a essa página')
        return redirect('/') #redireciona para a página de login, caso o administrdor não esteja logado.
    

#Consultar o acervo (Administrador)
@app.route('/adm/acervo')
def acervo():
    global adm_logado
    
    #verifica se o administrador está logado ou não.
    if adm_logado == True:
        tipo_busca = request.args.get('tipo_busca', 'titulo')
        termo_busca = request.args.get('termo_busca', '')

        #consulta no banco de dados, a tabela de livros.
        query = Livro.query

        #determina se a busca será realizada por título ou autor.
        if tipo_busca == 'titulo':
            query = query.filter(Livro.titulo.contains(termo_busca))
        elif tipo_busca == 'autor':
            query = query.filter(Livro.autor.contains(termo_busca))

        #retorna os livros correspondentes aos critérios de busca.
        livros = query.all()

        #verifica se existe livros correspondentes aos critérios de busca.
        if not livros:
            mensagem = 'Nenhum livro encontrado com os critérios informados.'
            return render_template('acervo.html', mensagem=mensagem, tipo_busca=tipo_busca, termo_busca=termo_busca)

        return render_template('acervo.html', livros=livros, tipo_busca=tipo_busca, termo_busca=termo_busca)
    else:
        flash('Você não tem permissão para acessar essa página')
        return redirect('/')

#consultar o acervo (Usuário)
@app.route('/usuario/acervo')
def acervo_usuario():
    
    tipo_busca = request.args.get('tipo_busca', 'titulo') #obtém o valor do parâmetro tipo_busca
    termo_busca = request.args.get('termo_busca', '') #obtém o valor do parâmetro termo_busca

    #consulta no banco de dados, a tabela de livros.
    query = Livro.query

    #determina se a busca será realizada por título ou autor.
    if tipo_busca == 'titulo':
        query = query.filter(Livro.titulo.contains(termo_busca))
    elif tipo_busca == 'autor':
        query = query.filter(Livro.autor.contains(termo_busca))

    #retorna os livros correspondentes aos critérios de busca.
    livros = query.all()
    
    #caso o livro não for encontrado 
    if not livros:
        mensagem = 'Nenhum livro encontrado.'
        return render_template('acervo_usuario.html', mensagem=mensagem, tipo_busca=tipo_busca, termo_busca=termo_busca)

    return render_template('acervo_usuario.html', livros=livros, tipo_busca=tipo_busca, termo_busca=termo_busca)


#efetuar empréstimo (Administrador)
@app.route('/adm/emprestimo', methods=['GET', 'POST'])
def emprestimo():
    
    global adm_logado
    
    if not adm_logado:
        flash('Você não tem permissão para acessar essa página')
        return redirect('/')
    
    elif request.method == 'POST':
        
        livro_id = request.form.get('livro_id') #obtem o id do livro fornecido no formulario.
        matricula = request.form.get('matricula') #obtem o id do usuário fornecido no formulario.

        livro = Livro.query.get(livro_id) #obtem o objeto correspondente ao id do livro.
        usuario = Usuario.query.filter_by(matricula = matricula).first() #obtem o objeto correspondente ao id do usuário.

        #verifica se livro e usuário existem
        if livro and usuario:
            
            #verifica se há exemplares disponíveis.
            if livro.quantidade_exemplares > 0: 
                
                #verifica se o usuário atingiu o limite máximo de empréstimos (3 empréstimos).
                if len([e for e in usuario.emprestimos if not e.finalizado]) < 3:
                    
                    livro.quantidade_exemplares -= 1  #atualiza a quantidade de exemplares do livro.
                   
                    emprestimo = Emprestimo(usuario=usuario, livro=livro) #cria um novo objeto.
                    
                    db.session.add(emprestimo) #adiciona o objeto no banco de dados.
                    db.session.commit() #confirma alteração no banco.
                    
                    flash('Empréstimo realizado com sucesso!')
                    
                elif livro.quantidade_exemplares == 0:
                    livro.disponivel = False #marca o livro como indisponível
                    
                    flash('Não há exemplares disponíveis para empréstimo.')
                else:
                    flash('Você atingiu o limite máximo de empréstimos.')
            else:
                flash('O livro selecionado não está disponível para empréstimo.')
        else:
            flash('Não foi possível realizar o empréstimo. Verifique os dados fornecidos.')
    
    #filtro de busca        
    tipo_busca = request.args.get('tipo_busca', 'titulo')
    termo_busca = request.args.get('termo_busca', '')
    
    livros = []
    
    if tipo_busca == 'titulo':
        livros = Livro.query.filter(Livro.titulo.ilike(f"%{termo_busca}%")).all()
    elif tipo_busca == 'autor':
        livros = Livro.query.filter(Livro.autor.ilike(f"%{termo_busca}%")).all()
    
    usuarios = Usuario.query.all()

    return render_template('emprestimo.html', livros=livros, usuarios=usuarios, tipo_busca=tipo_busca, termo_busca=termo_busca)

#efetuar emprestimo(Usuário)
@app.route('/usuario/emprestimo', methods=['POST'])
def emprestimo_usuario():
    
    usuario_id = session.get('usuario_id') #obtem o id do usuario logado.

    #redireciona para pagina de login se usuario não estiver logado.
    if not usuario_id:
        flash('Faça o login para realizar um empréstimo.')
        return redirect('/')

    livro_id = request.form.get('livro_id') #id do livro a parir do formulário.

    usuario = Usuario.query.get(usuario_id) #retorna usuário do banco de dados com id correspondente ao informado no formulario.
    livro = Livro.query.get(livro_id) #retorna livro do banco de dados com id correspondente ao informado no formulario.

    #verifica se livro e usuario existem.
    if usuario and livro:
        
        #verifica disponibilidade de livro.
        if livro.quantidade_exemplares > 0:
            
            #verifica se o usuário atingiu o limite máximo de empréstimos (3 empréstimos).
            if len([e for e in usuario.emprestimos if not e.finalizado]) < 3:
                
                livro.quantidade_exemplares -= 1 #atualiza quantidade de exemplares do livro.
                
                emprestimo = Emprestimo(usuario=usuario, livro=livro) #cria novo objeto emprestimo.
                
                db.session.add(emprestimo) #adiciona objeto ao banco.
                db.session.commit() #confirma alteração no banco.
                
                flash('Empréstimo realizado com sucesso!')
            else:
                flash('Você atingiu o limite máximo de empréstimos.')
        else:
            flash('O livro selecionado não está disponível para empréstimo.')
    else:
        flash('Não foi possível realizar o empréstimo. Verifique os dados fornecidos.')

    return redirect('/usuario')


#Exibe relatório de empréstimos (Administrador)
@app.route('/adm/emprestimos', methods=['GET'])
def lista_emprestimos():
    global adm_logado
    
    #verifica se o administrador está logado ou não.
    if adm_logado == True:
        emprestimos = Emprestimo.query.all() #retorna todos os empréstimos registrados no banco.
        return render_template('lista_emprestimos.html', emprestimos=emprestimos)
    else:
        flash('Você não tem permissão para acessar essa página')
        return redirect('/') #redireciona para a pagina de login.
    
    
#exibe histórico de emprestimos realizados (Usuário)
@app.route('/usuario/historico')
def emprestimos_usuario():
    
    usuario_id = session.get('usuario_id') #obtem o id do usuario autenticado.

    #redireciona para o login caso não esteja autenticado.
    if not usuario_id:
        flash('Faça o login para visualizar os empréstimos.')
        return redirect('/')

    #obtem o objeto correspondente ao id do usuário autenticado.
    usuario = Usuario.query.get(usuario_id)

    #retorna os empréstimos realizados pelo usuário autenticado.
    if usuario:
        emprestimos = usuario.emprestimos
        return render_template('historico_usuario.html', emprestimos=emprestimos)
    else:
        flash('Usuário não encontrado.')
        return redirect('/')


#rota para a página de devolução (Administrador)
@app.route('/adm/devolucao', methods=['GET', 'POST'])
def devolucao():
    global adm_logado
    
    #verifica se administrador está logado ou não.
    if not adm_logado:
        flash('Você não tem permissão para acessar essa página')
        return redirect('/')
    
    elif request.method == 'POST':
        emprestimo_id = request.form.get('emprestimo_id') #obtem id do emprestimo a partir do formulario.
        data_devolucao_str = request.form.get('data_devolucao') #obtem data de devolução a partir do formulario.

        #verifica se o emprestimo e a data de devolução foram informados.
        if not emprestimo_id:
            flash('Selecione um empréstimo para devolver.')
        elif not data_devolucao_str:
            flash('Informe a data de devolução.')
            
        else:
            try:
                
                emprestimo = Emprestimo.query.get(int(emprestimo_id)) 
                data_devolucao = datetime.strptime(data_devolucao_str, '%Y-%m-%d')
                
                #verifica se a data de devolução é anterior a data do emprestimo
                if data_devolucao < emprestimo.data_emprestimo:
                    flash('Data de devolução inválida!')
                    
                #calcula a multa por atraso.
                elif emprestimo:
                    if data_devolucao > emprestimo.prazo_devolucao:
                        taxa = calcular_multa(emprestimo.prazo_devolucao, data_devolucao)
                        emprestimo.multa = taxa
                    else:
                        taxa = 0
                        
                    emprestimo.data_devolucao = data_devolucao

                    #marca o livro como disponível novamente e atualiza quantidade de exemplares.
                    livro = emprestimo.livro
                    livro.quantidade_exemplares += 1
                    livro.disponivel = True
                    
                    #marca o empréstimo como finalizado apenas quando o livro for devolvido.
                    if livro.disponivel:
                        emprestimo.finalizado = True
                    
                    db.session.commit() #salva alteração no banco.

                    #emite a multa de atraso.
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


#rota para realizar a devolução do usuário
@app.route('/usuario/devolucao', methods=['POST'])
def devolucao_usuario():
    
    usuario_id = session.get('usuario_id') #obtem o id do usuario autenticado.

    #redireciona para a página de login se usuário ão estiver logado.
    if not usuario_id:
        flash('Faça o login para acessar a devolução.')
        return redirect('/')

    emprestimo_id = request.form.get('emprestimo_id') #obtem o id do emprestimo.
    data_devolucao_str = request.form.get('data_devolucao') #obtem a data de devolução.

    #verifica se emprestimo e data de devolução foram informados.
    if not emprestimo_id or not data_devolucao_str:
        flash('Selecione um empréstimo e informe a data de devolução.')
        return redirect('/usuario/devolucao')

    try:
        emprestimo = Emprestimo.query.get(int(emprestimo_id))
        data_devolucao = datetime.strptime(data_devolucao_str, '%Y-%m-%d')

        if emprestimo:
            #verifica se a data de devolução é anterior à data de empréstimo.
            if data_devolucao < emprestimo.data_emprestimo:
                flash('Data de devolução inválida.')
            else:
                #atualiza informação do emprestimo.
                emprestimo.data_devolucao = data_devolucao
                emprestimo.finalizado = True

                #atualiza se livro está disponivel e a quantidade de exemplares.
                livro = emprestimo.livro
                livro.quantidade_exemplares += 1
                livro.disponivel = True

                #calcula a multa.
                taxa = calcular_multa(emprestimo.prazo_devolucao, emprestimo.data_devolucao)
                emprestimo.multa = taxa

                db.session.commit() #confirma alteração no banco.

                #emite multa por atraso.
                if taxa > 0:
                    flash(f'Livro devolvido com sucesso! Multa por atraso: R$ {taxa:.2f}')
                else:
                    flash('Livro devolvido com sucesso!')
        else:
            flash('Empréstimo não encontrado. Verifique as informações.')
    except ValueError:
        flash('Data de devolução inválida.')

    return render_template('usuario.html')


if __name__ == '__main__':
    app.run(debug=True)
    

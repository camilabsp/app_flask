## Sistema de Gerenciamento de Biblioteca

Este é um sistema simples de biblioteca desenvolvido em Flask.

### Pré-requisitos

Certifique-se de ter o pip instalado em seu ambiente. 

#### Ambiente Flask
- *python -m venv .venv*

- * .\.venv\Scripts\activate*

- *pip install flask*

- *pip install flask-SQLAlchemy*

Execute o aplicativo usando o seguinte comando: *flask run*

### Funcionalidades

- **Página de Login**: Os usuários podem fazer login usando suas matrículas e senhas.

- **Painel do Administrador**: Acesse com a matrícula 'adm' e senha '000'. É possível cadastrar usuários, livros e visualizar todos os empréstimos.

- **Empréstimos**: Usuários podem realizar empréstimos de até 3 livros. É emitido multa por atraso.

### Estrutura do projeto

- **app.py**: O ponto de entrada do aplicativo.

- **templates**: Armazena os modelos HTML usados pelo Flask.

- **static**: Pode conter arquivos estáticos, como CSS ou JavaScript.

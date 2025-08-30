from auth import login_required_web
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from http import HTTPStatus
from models import db, Filme, Serie, Usuario
from sqlalchemy import asc
import click
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from auth import auth_bp as auth
from datetime import datetime, timedelta

app = Flask(__name__)
jwt = JWTManager()
jwt.init_app(app)

@jwt.unauthorized_loader
def missing_token_callback(error):
    return redirect(url_for('auth.acesso_negado'))

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return redirect(url_for('auth.acesso_negado'))

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return redirect(url_for('auth.acesso_negado'))

def criando_app(__name__, intance_relative_config=True):
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///Catalogo.db',
        JWT_SECRET_KEY='super-secret'
    )
criando_app(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
jwt.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Catalogo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
jwt.init_app(app)
app.register_blueprint(auth, url_prefix='/auth')

@app.route('/')
def home():
    filmes = Filme.query.order_by(asc(Filme.titulo)).all()
    series = Serie.query.order_by(asc(Serie.titulo)).all()
    return render_template('index.html', filmes=filmes, series=series), HTTPStatus.OK

@app.route('/filmes') # type: ignore
@login_required_web # para web
#@jwt_required() # para API/postman
def listar_filmes():
    filmes = Filme.query.order_by(asc(Filme.titulo)).all()
    return render_template('listar_filmes.html', filmes=filmes), HTTPStatus.OK

@app.route('/filmes/adicionar', methods=['GET', 'POST'])
@login_required_web # para web
#@jwt_required() # para API/postman
def adicionar_filme():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        ano_lancamento = request.form.get('ano_lancamento')
        genero = request.form.get('genero')
        sinopse = request.form.get('sinopse')
        diretor_criador = request.form.get('diretor_criador')
        descricao = request.form.get('descricao')
        url_imagem = request.form.get('url_imagem')

        if not titulo or not ano_lancamento or not genero:
            flash('Título, Ano de Lançamento e Gênero são obrigatórios!', 'erro')
            return render_template('adicionar.html', tipo="filme"), HTTPStatus.BAD_REQUEST # type: ignore

        try:
            ano_lancamento = int(ano_lancamento)
        except ValueError:
            flash('Ano de Lançamento inválido!', 'erro')
            return render_template('adicionar.html', tipo="filme"), HTTPStatus.BAD_REQUEST

        novo_filme = Filme(
            titulo=titulo, # type: ignore
            ano_lancamento=ano_lancamento, # type: ignore
            genero=genero, # type: ignore
            sinopse=sinopse, # type: ignore
            diretor_criador=diretor_criador, # type: ignore
            descricao=descricao, # type: ignore
            url_imagem=url_imagem # type: ignore
        )

        db.session.add(novo_filme)
        db.session.commit()

        flash('Filme adicionado com sucesso!', 'sucesso')
        return redirect(url_for('listar_filmes')), HTTPStatus.FOUND # type: ignore

    return render_template('adicionar.html', tipo="filme"), HTTPStatus.OK

@app.route('/filmes/detalhes/<int:id>')
@login_required_web # para web
#@jwt_required() # para API/postman
def detalhes_filme(id):
    filme = Filme.query.get_or_404(id)
    return render_template('detalhes.html', item=filme, tipo="filme"), HTTPStatus.OK

@app.route('/filmes/atualizar/<int:id>', methods=['GET', 'POST'])
@login_required_web # para web
#@jwt_required() # para API/postman
def atualizar_filme(id):
    filme = Filme.query.get_or_404(id)
    if request.method == 'POST':
        try:
            titulo = request.form.get('titulo') # type: ignore
            ano_lancamento_str = request.form.get('ano_lancamento')
            genero = request.form.get('genero')
            sinopse = request.form.get('sinopse')
            diretor_criador = request.form.get('diretor_criador')
            descricao = request.form.get('descricao')
            url_imagem = request.form.get('url_imagem')

            if not titulo or not ano_lancamento_str or not genero: # type: ignore
                flash('Título, Ano de Lançamento e Gênero são obrigatórios!', 'erro')
                return render_template('atualizar.html', item=filme, tipo="filme"), HTTPStatus.BAD_REQUEST

            ano_lancamento = int(ano_lancamento_str) # type: ignore

            campos_alterados = 0 # type: ignore
            if titulo != filme.titulo:
                campos_alterados += 1
            if ano_lancamento != filme.ano_lancamento:
                campos_alterados += 1
            if genero != filme.genero:
                campos_alterados += 1
            if (sinopse or '') != (filme.sinopse or ''):
                campos_alterados += 1
            if (diretor_criador or '') != (filme.diretor_criador or ''):
                campos_alterados += 1
            if (descricao or '') != (filme.descricao or ''):
                campos_alterados += 1
            if (url_imagem or '') != (filme.url_imagem or ''):
                campos_alterados += 1

            if campos_alterados < 3:
                flash('Você deve alterar pelo menos 3 campos para atualizar.', 'erro')
                flash('Ou clique na logo para voltar', 'erro')
                return render_template('atualizar.html', item=filme, tipo="filme"), HTTPStatus.BAD_REQUEST

            filme.titulo = titulo # type: ignore
            filme.ano_lancamento = ano_lancamento
            filme.genero = genero
            filme.sinopse = sinopse
            filme.diretor_criador = diretor_criador
            filme.descricao = descricao
            filme.url_imagem = url_imagem

        except Exception as e:
            flash(f'Erro ao atualizar filme: {str(e)}', 'erro')
            return render_template('atualizar.html', item=filme, tipo="filme"), HTTPStatus.BAD_REQUEST

        db.session.commit()
        flash('Já houve uma atualização', 'sucesso')
        return redirect(url_for('detalhes_filme', id=filme.id)), HTTPStatus.FOUND

    return render_template('atualizar.html', item=filme, tipo="filme"), HTTPStatus.OK

@app.route('/filmes/atualizar_parcial/<int:id>', methods=['GET', 'POST']) # type: ignore
@login_required_web
def atualizar_parcial_filme(id):
    filme = Filme.query.get_or_404(id)
    if request.method == 'POST':
        campo = request.form.get('campo')
        if not campo:
            flash('Campo para atualização não informado!', 'erro')
            return redirect(url_for('atualizar_parcial_filme', id=id))

        valor = request.form.get(campo)
        if not valor or valor.strip() == '':
            flash(f'O campo {campo} não pode estar vazio!', 'erro')
            return redirect(url_for('atualizar_parcial_filme', id=id))

        if hasattr(filme, campo):
            if campo == 'ano_lancamento':
                try:
                    valor = int(valor)
                except ValueError:
                    flash('Ano de Lançamento inválido!', 'erro')
                    return redirect(url_for('atualizar_parcial_filme', id=id))
            setattr(filme, campo, valor)
            db.session.commit()
            flash(f'{campo} atualizado com sucesso!', 'sucesso')
        else:
            flash('Campo inválido!', 'erro')

        return redirect(url_for('detalhes_filme', id=filme.id))

    return render_template('atualizar_parcial.html', item=filme, tipo="filme")

@app.route('/filmes/deletar/<int:id>', methods=['POST']) # type: ignore
@login_required_web
def deletar_filme(id):
    filme = Filme.query.get_or_404(id)
    db.session.delete(filme)
    db.session.commit()
    flash('Filme deletado com sucesso!', 'sucesso')
    return redirect(url_for('listar_filmes')), HTTPStatus.FOUND

# Rotas Series seguem mesmo padrão
@app.route('/series')
@login_required_web
def listar_series():
    series = Serie.query.order_by(asc(Serie.titulo)).all()
    return render_template('listar_series.html', series=series), HTTPStatus.OK

@app.route('/series/adicionar', methods=['GET', 'POST'])
@login_required_web
def adicionar_serie():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        ano_lancamento = request.form.get('ano_lancamento')
        genero = request.form.get('genero')
        sinopse = request.form.get('sinopse')
        diretor_criador = request.form.get('diretor_criador')
        descricao = request.form.get('descricao')
        url_imagem = request.form.get('url_imagem')

        if not titulo or not ano_lancamento or not genero:
            flash('Título, Ano de Lançamento e Gênero são obrigatórios!', 'erro')
            return render_template('adicionar.html', tipo="serie"), HTTPStatus.BAD_REQUEST

        try:
            ano_lancamento = int(ano_lancamento)
        except ValueError:
            flash('Ano de Lançamento inválido!', 'erro')
            return render_template('adicionar.html', tipo="serie"), HTTPStatus.BAD_REQUEST

        nova_serie = Serie(
            titulo=titulo, # type: ignore
            ano_lancamento=ano_lancamento, # type: ignore
            genero=genero, # type: ignore
            sinopse=sinopse, # type: ignore
            diretor_criador=diretor_criador, # type: ignore
            descricao=descricao, # type: ignore
            url_imagem=url_imagem # type: ignore
        )

        db.session.add(nova_serie)
        db.session.commit()

        flash('Série adicionada com sucesso!', 'sucesso')
        return redirect(url_for('listar_series')), HTTPStatus.FOUND

    return render_template('adicionar.html', tipo="serie"), HTTPStatus.OK

@app.route('/series/detalhes/<int:id>')
@login_required_web
def detalhes_serie(id):
    serie = Serie.query.get_or_404(id)
    return render_template('detalhes.html', item=serie, tipo="serie"), HTTPStatus.OK

@app.route('/series/atualizar/<int:id>', methods=['GET', 'POST'])
@login_required_web
def atualizar_serie(id):
    serie = Serie.query.get_or_404(id)
    if request.method == 'POST':
        try:
            serie.titulo = request.form.get('titulo')
            serie.ano_lancamento = int(request.form.get('ano_lancamento')) # type: ignore
            serie.genero = request.form.get('genero')
            serie.sinopse = request.form.get('sinopse')
            serie.diretor_criador = request.form.get('diretor_criador')
            serie.descricao = request.form.get('descricao')
            serie.url_imagem = request.form.get('url_imagem')
        except Exception as e:
            flash(f'Erro ao atualizar série: {str(e)}', 'erro')
            return render_template('atualizar.html', item=serie, tipo="serie"), HTTPStatus.BAD_REQUEST

        db.session.commit()
        flash('Série atualizada com sucesso!', 'sucesso')
        return redirect(url_for('detalhes_serie', id=serie.id)), HTTPStatus.FOUND

    return render_template('atualizar.html', item=serie, tipo="serie"), HTTPStatus.OK

@app.route('/series/atualizar-parcial/<int:id>', methods=['GET', 'POST'])
@login_required_web
def atualizar_parcial_serie(id):
    serie = Serie.query.get_or_404(id)
    if request.method == 'POST':
        campo = request.form.get('campo')
        valor = request.form.get('valor')

        if hasattr(serie, campo): # type: ignore
            if campo == 'ano_lancamento':
                try:
                    valor = int(valor) # type: ignore
                except ValueError:
                    flash('Ano de Lançamento inválido!', 'erro')
                    return redirect(url_for('atualizar_parcial_serie', id=id)), HTTPStatus.BAD_REQUEST
            setattr(serie, campo, valor) # type: ignore
            db.session.commit()
            flash(f'{campo} atualizado com sucesso!', 'sucesso')
        else:
            flash('Campo inválido!', 'erro')

        return redirect(url_for('detalhes_serie', id=serie.id)), HTTPStatus.FOUND

    return render_template('atualizar_parcial.html', item=serie, tipo="serie"), HTTPStatus.OK

@app.route('/series/deletar/<int:id>', methods=['POST'])
@login_required_web
def deletar_serie(id):
    serie = Serie.query.get_or_404(id)
    db.session.delete(serie)
    db.session.commit()
    flash('Série deletada com sucesso!', 'sucesso')
    return redirect(url_for('listar_series')), HTTPStatus.FOUND

@app.cli.command("init-db")
def init_db():
    """Inicializa o banco de dados, criando as tabelas."""
    db.create_all()
    click.echo("Banco de dados criado com sucesso!")
    
@app.cli.command("create-admin")
def create_admin():
    from app import app
    with app.app_context():
        if not Usuario.query.filter_by(username="admin").first():
            admin = Usuario(username="admin") # type: ignore
            admin.set_password("1234")
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado com sucesso!")
        else:
            print("Usuário admin já existe.")

def deletar_usuarios_antigos():
    limite = datetime.utcnow() - timedelta(days=30)
    usuarios = Usuario.query.filter(Usuario.criado_em < limite).all()
    for usuario in usuarios:
        db.session.delete(usuario)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash
from http import HTTPStatus
from models import db, Filme, Serie 
from sqlalchemy import asc
import click

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Catalogo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route('/')
def home():
    filmes = Filme.query.order_by(asc(Filme.titulo)).all()
    series = Serie.query.order_by(asc(Serie.titulo)).all()
    return render_template('index.html', filmes=filmes, series=series), HTTPStatus.OK


@app.route('/filmes')
def listar_filmes():
    filmes = Filme.query.order_by(asc(Filme.titulo)).all()
    return render_template('listar_filmes.html', filmes=filmes), HTTPStatus.OK

@app.route('/filmes/adicionar', methods=['GET', 'POST'])
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
            # Bad request 400 ao não enviar dados obrigatórios
            return render_template('adicionar.html', tipo="filme"), HTTPStatus.BAD_REQUEST

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
        # Redirect com status 302 FOUND (padrão)
        return redirect(url_for('listar_filmes')), HTTPStatus.FOUND

    return render_template('adicionar.html', tipo="filme"), HTTPStatus.OK

@app.route('/filmes/detalhes/<int:id>')
def detalhes_filme(id):
    filme = Filme.query.get_or_404(id)
    return render_template('detalhes.html', item=filme, tipo="filme"), HTTPStatus.OK

@app.route('/filmes/atualizar/<int:id>', methods=['GET', 'POST'])
def atualizar_filme(id):
    filme = Filme.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Pegue os novos valores do form
            titulo = request.form.get('titulo')
            ano_lancamento_str = request.form.get('ano_lancamento')
            genero = request.form.get('genero')
            sinopse = request.form.get('sinopse')
            diretor_criador = request.form.get('diretor_criador')
            descricao = request.form.get('descricao')
            url_imagem = request.form.get('url_imagem')

            # Verifique se os obrigatórios estão preenchidos
            if not titulo or not ano_lancamento_str or not genero:
                flash('Título, Ano de Lançamento e Gênero são obrigatórios!', 'erro')
                return render_template('atualizar.html', item=filme, tipo="filme"), HTTPStatus.BAD_REQUEST

            # Converta ano de lançamento
            ano_lancamento = int(ano_lancamento_str)

            # Verifique quantos campos realmente mudaram (pelo menos 3 para atualizar)
            campos_alterados = 0
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

            # VAI ATUALIZANDO AE PAPAI
            filme.titulo = titulo
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


@app.route('/filmes/atualizar_parcial/<int:id>', methods=['GET', 'POST'])
def atualizar_parcial_filme(id):
    filme = Filme.query.get_or_404(id)
    if request.method == 'POST':
        campo = request.form.get('campo')
        if not campo:
            flash('Campo para atualização não informado!', 'erro')
            return redirect(url_for('atualizar_parcial_filme', id=id))

        valor = request.form.get(campo)  # Aqui pega o valor correto do campo específico

        if not valor or valor.strip() == '':
            flash(f'O campo {campo} não pode estar vazio!', 'erro')
            return redirect(url_for('atualizar_parcial_filme', id=id))

        if hasattr(filme, campo):  # type: ignore
            if campo == 'ano_lancamento':
                try:
                    valor = int(valor)  # type: ignore
                except ValueError:
                    flash('Ano de Lançamento inválido!', 'erro')
                    return redirect(url_for('atualizar_parcial_filme', id=id))
            setattr(filme, campo, valor)  # type: ignore
            db.session.commit()
            flash(f'{campo} atualizado com sucesso!', 'sucesso')
        else:
            flash('Campo inválido!', 'erro')

        return redirect(url_for('detalhes_filme', id=filme.id))

    return render_template('atualizar_parcial.html', item=filme, tipo="filme")


@app.route('/filmes/deletar/<int:id>', methods=['POST'])
def deletar_filme(id):
    filme = Filme.query.get_or_404(id)
    db.session.delete(filme)
    db.session.commit()
    flash('Filme deletado com sucesso!', 'sucesso')
    return redirect(url_for('listar_filmes')), HTTPStatus.FOUND


@app.route('/series')
def listar_series():
    series = Serie.query.order_by(asc(Serie.titulo)).all()
    return render_template('listar_series.html', series=series), HTTPStatus.OK

@app.route('/series/adicionar', methods=['GET', 'POST'])
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
            sinopse=sinopse,# type: ignore
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
def detalhes_serie(id):
    serie = Serie.query.get_or_404(id)
    return render_template('detalhes.html', item=serie, tipo="serie"), HTTPStatus.OK

@app.route('/series/atualizar/<int:id>', methods=['GET', 'POST'])
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

# fiquei com preguiça de ficar coisando no terminal
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask import Blueprint, request
from http import HTTPStatus
from models import db, Filme

app_filmes = Blueprint('filmes', __name__, url_prefix='/filmes')


@app_filmes.get('/')
def listar_filmes():
    filmes = Filme.query.all()

    if not filmes:
        return {"mensagem": "Nenhum filme cadastrado"}, HTTPStatus.OK

    resultado = []
    for f in filmes:
        resultado.append({
            "id": f.id,
            "titulo": f.titulo,
            "ano_lancamento": f.ano_lancamento,
            "genero": f.genero,
            "sinopse": f.sinopse,
            "diretor_criador": f.diretor_criador,
            "descricao": f.descricao
        })

    return {"filmes": resultado}, HTTPStatus.OK


@app_filmes.post('/adicionar')
def adicionar_filme():
    dados = request.get_json()

    campos = ['titulo', 'ano_lancamento', 'genero', 'sinopse', 'diretor_criador', 'descricao']
    if not dados or not all(campo in dados for campo in campos):
        return {"erro": "Todos os campos são obrigatórios"}, HTTPStatus.BAD_REQUEST

    novo_filme = Filme(
        titulo=dados['titulo'], # pyright: ignore[reportCallIssue]
        ano_lancamento=dados['ano_lancamento'],  # pyright: ignore[reportCallIssue]
        genero=dados['genero'], # pyright: ignore[reportCallIssue]
        sinopse=dados['sinopse'], # pyright: ignore[reportCallIssue]
        diretor_criador=dados['diretor_criador'], # pyright: ignore[reportCallIssue]
        descricao=dados['descricao'] # pyright: ignore[reportCallIssue]
    )
    db.session.add(novo_filme)
    db.session.commit()

    return {
        "mensagem": "Filme adicionado com sucesso",
        "filme": {
            "id": novo_filme.id,
            "titulo": novo_filme.titulo,
            "ano_lancamento": novo_filme.ano_lancamento,
            "genero": novo_filme.genero,
            "sinopse": novo_filme.sinopse,
            "diretor_criador": novo_filme.diretor_criador,
            "descricao": novo_filme.descricao
        }
    }, HTTPStatus.CREATED


@app_filmes.delete('/deletar/<int:id>')
def deletar_filme(id):
    filme = Filme.query.get(id)

    if not filme:
        return {"erro": "Filme não encontrado"}, HTTPStatus.NOT_FOUND

    db.session.delete(filme)
    db.session.commit()

    return {"mensagem": f"Filme com ID {id} deletado com sucesso"}, HTTPStatus.OK


@app_filmes.put('/atualizar/<int:id>')
def atualizar_filme_total(id):
    dados = request.get_json()

    campos = ['titulo', 'ano_lancamento', 'genero', 'sinopse', 'diretor_criador', 'descricao']
    if not dados or not all(campo in dados for campo in campos):
        return {"erro": "Todos os campos são obrigatórios"}, HTTPStatus.BAD_REQUEST

    filme = Filme.query.get(id)
    if not filme:
        return {"erro": "Filme não encontrado"}, HTTPStatus.NOT_FOUND

    filme.titulo = dados['titulo']
    filme.ano_lancamento = dados['ano_lancamento']
    filme.genero = dados['genero']
    filme.sinopse = dados['sinopse']
    filme.diretor_criador = dados['diretor_criador']
    filme.descricao = dados['descricao']
    db.session.commit()

    return {
        "mensagem": "Filme atualizado com sucesso",
        "filme": {
            "id": filme.id,
            "titulo": filme.titulo,
            "ano_lancamento": filme.ano_lancamento,
            "genero": filme.genero,
            "sinopse": filme.sinopse,
            "diretor_criador": filme.diretor_criador,
            "descricao": filme.descricao
        }
    }, HTTPStatus.OK


@app_filmes.patch('/atualizacao/parcial/<int:id>')
def atualizar_filme_parcial(id):
    dados = request.get_json()

    if not dados:
        return {"erro": "Dados inválidos ou incompletos"}, HTTPStatus.BAD_REQUEST

    filme = Filme.query.get(id)
    if not filme:
        return {"erro": "Filme não encontrado"}, HTTPStatus.NOT_FOUND

    if 'titulo' in dados:
        filme.titulo = dados['titulo']
    if 'ano_lancamento' in dados:
        filme.ano_lancamento = dados['ano_lancamento']
    if 'genero' in dados:
        filme.genero = dados['genero']
    if 'sinopse' in dados:
        filme.sinopse = dados['sinopse']
    if 'diretor_criador' in dados:
        filme.diretor_criador = dados['diretor_criador']
    if 'descricao' in dados:
        filme.descricao = dados['descricao']

    db.session.commit()

    return {
        "mensagem": "Filme atualizado com sucesso",
        "filme": {
            "id": filme.id,
            "titulo": filme.titulo,
            "ano_lancamento": filme.ano_lancamento,
            "genero": filme.genero,
            "sinopse": filme.sinopse,
            "diretor_criador": filme.diretor_criador,
            "descricao": filme.descricao
        }
    }, HTTPStatus.OK

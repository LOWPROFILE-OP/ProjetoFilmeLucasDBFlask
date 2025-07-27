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
            "nome": f.nome,
            "descricao": f.descricao,
            "data": f.data.isoformat() if f.data else None
        })

    return {"filmes": resultado}, HTTPStatus.OK


@app_filmes.post('/adicionar')
def adicionar_filme():
    dados = request.get_json()

    if not dados or 'nome' not in dados:
        return {"erro": "Nome é obrigatório"}, HTTPStatus.BAD_REQUEST

    nome = dados['nome']
    descricao = dados.get('descricao', '')

    novo_filme = Filme(nome=nome, descricao=descricao)
    db.session.add(novo_filme)
    db.session.commit()

    return {
        "mensagem": "Filme adicionado com sucesso",
        "filme": {
            "id": novo_filme.id,
            "nome": novo_filme.nome,
            "descricao": novo_filme.descricao,
            "data": novo_filme.data.isoformat() if novo_filme.data else None
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

    if not dados or 'nome' not in dados or 'descricao' not in dados:
        return {"erro": "Nome e descrição são obrigatórios"}, HTTPStatus.BAD_REQUEST

    filme = Filme.query.get(id)
    if not filme:
        return {"erro": "Filme não encontrado"}, HTTPStatus.NOT_FOUND

    filme.nome = dados['nome']
    filme.descricao = dados['descricao']
    db.session.commit()

    return {
        "mensagem": "Filme atualizado com sucesso",
        "filme": {
            "id": filme.id,
            "nome": filme.nome,
            "descricao": filme.descricao
        }
    }, HTTPStatus.OK


@app_filmes.patch('/atualizacao/parcial/<int:id>')
def atualizar_filme_parcial(id):
    dados = request.get_json()

    if not dados or ('nome' not in dados and 'descricao' not in dados):
        return {"erro": "Dados inválidos ou incompletos"}, HTTPStatus.BAD_REQUEST

    filme = Filme.query.get(id)
    if not filme:
        return {"erro": "Filme não encontrado"}, HTTPStatus.NOT_FOUND

    if 'nome' in dados:
        filme.nome = dados['nome']
    if 'descricao' in dados:
        filme.descricao = dados['descricao']

    db.session.commit()

    return {
        "mensagem": "Filme atualizado com sucesso",
        "filme": {
            "id": filme.id,
            "nome": filme.nome,
            "descricao": filme.descricao
        }
    }, HTTPStatus.OK

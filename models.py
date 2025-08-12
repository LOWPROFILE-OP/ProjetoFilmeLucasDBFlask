from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Filme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    ano_lancamento = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    sinopse = db.Column(db.Text)
    diretor_criador = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    url_imagem = db.Column(db.String(250))

class Serie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    ano_lancamento = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    sinopse = db.Column(db.Text)
    diretor_criador = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    url_imagem = db.Column(db.String(250))

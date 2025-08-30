from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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

    def __repr__(self):
        return f"<Filme {self.titulo}>"

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "ano_lancamento": self.ano_lancamento,
            "genero": self.genero,
            "sinopse": self.sinopse,
            "diretor_criador": self.diretor_criador,
            "descricao": self.descricao,
            "url_imagem": self.url_imagem
        }

class Serie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    ano_lancamento = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    sinopse = db.Column(db.Text)
    diretor_criador = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    url_imagem = db.Column(db.String(250))

    def __repr__(self):
        return f"<Serie {self.titulo}>"

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "ano_lancamento": self.ano_lancamento,
            "genero": self.genero,
            "sinopse": self.sinopse,
            "diretor_criador": self.diretor_criador,
            "descricao": self.descricao,
            "url_imagem": self.url_imagem
        }

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "criado_em": self.criado_em.isoformat()
        }

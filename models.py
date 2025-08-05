from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Filme(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    ano_lancamento: Mapped[int] = mapped_column(nullable=False)
    genero: Mapped[str] = mapped_column(db.String(50), nullable=False)
    sinopse: Mapped[str] = mapped_column(db.String(300), nullable=True)
    diretor_criador: Mapped[str] = mapped_column(db.String(100), nullable=True)
    descricao: Mapped[str] = mapped_column(db.String(200), nullable=True)

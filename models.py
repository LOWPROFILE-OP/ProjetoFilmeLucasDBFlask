from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Filme(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    descricao: Mapped[str] = mapped_column(db.String(200))
    data: Mapped[datetime] = mapped_column(default=datetime.utcnow)

import os
import click
from flask import Flask
from models import db
from routes import app_filmes

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///filmes.sqlite',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(app_filmes)

    @app.cli.command("init-db")
    def init_db():
        with app.app_context():
            db.create_all()
            click.echo("Banco de dados inicializado!")

    return app

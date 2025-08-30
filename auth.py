from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from datetime import timedelta, datetime
from models import db, Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')


# PROTEÇÃO PARA ROTAS WEB
def login_required_web(f):
    """Protege rotas web (Jinja templates)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Checa se usuário está logado
            flash("Faça login primeiro!", "erro")
            return redirect(url_for("auth.login_web_page"))
        return f(*args, **kwargs)
    return decorated_function


# PÁGINA DE LOGIN WEB
@auth_bp.route('/login_web', methods=['GET'])
def login_web_page():
    """Página de login web"""
    return render_template('login.html')

# LOGIN VIA FORMULÁRIO WEB
@auth_bp.route('/login_web', methods=['POST'])
def login_web():
    """Login via formulário web"""
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Username e senha são obrigatórios!', 'erro')
        return redirect(url_for('auth.login_web_page'))

    usuario = Usuario.query.filter_by(username=username).first()
    if usuario and usuario.check_password(password):
        session['user_id'] = usuario.id
        session['username'] = usuario.username
        flash('Login realizado com sucesso!', 'sucesso')
        return redirect(url_for('listar_filmes'))  # ou rota inicial

    flash('Usuário ou senha inválidos!', 'erro')
    return redirect(url_for('auth.login_web_page'))


# LOGOUT VIA WEB
@auth_bp.route('/logout_web', methods=['GET'])
def logout_web():
    """Logout web"""
    session.clear()  # Limpa toda a sessão
    flash("Logout realizado com sucesso!", "sucesso")
    return redirect(url_for('auth.login_web_page'))


# PÁGINA DE ACESSO NEGADO

@auth_bp.route('/acesso_negado', methods=['GET'])
def acesso_negado():
    """Página de acesso negado"""
    return render_template('acesso_negado.html')



# ROTAS API (POSTMAN)
@auth_bp.route('/register', methods=['POST'])
def register():
    """Registro via API//postman"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {"error": "Username e senha obrigatórios"}, 400

    if Usuario.query.filter_by(username=username).first():
        return {"error": "Usuário já existe"}, 400

    user = Usuario(username=username) # type: ignore
    user.set_password(password)
    user.criado_em = datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return {"message": "Usuário criado com sucesso"}, 201

@auth_bp.route('/login_API', methods=['POST'])
def login_api():
    """Login via API//postman"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {"error": "Username e senha obrigatórios"}, 400

    usuario = Usuario.query.filter_by(username=username).first()
    if usuario and usuario.check_password(password):
        access_token = create_access_token(identity=usuario.id, expires_delta=timedelta(days=30))
        return {"access_token": access_token}, 200

    return {"error": "Usuário ou senha inválidos"}, 401

@auth_bp.route('/Eu', methods=['GET'])
@jwt_required()
def me():
    """Retorna informações do usuário logado via API/Postman"""
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(user_id)
    if usuario:
        return {"id": usuario.id, "username": usuario.username}, 200
    return {"error": "Usuário não encontrado"}, 404

@auth_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Deletar usuário via API/Postman"""
    user = Usuario.query.get(user_id)
    if not user:
        return {"error": "Usuário não encontrado"}, 404
    try:
        db.session.delete(user)
        db.session.commit()
        return {"message": f"Usuário {user.username} deletado com sucesso"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


# JWT INICIALIZAÇÃO
def init_jwt(app):
    """Inicializa JWT para API"""
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"error": "Faça login primeiro!"}, 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"error": "Token expirado!"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"error": "Token inválido!"}, 401

    return jwt

# CRIAÇÃO DE ADMIN VIA CLI MESMA COISA NO APP
def create_admin(app):
    """Criação de admin via CLI ou script"""
    with app.app_context():
        if not Usuario.query.filter_by(username="admin").first():
            admin = Usuario(username="admin") # type: ignore
            admin.set_password("1234")
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado com sucesso!")
        else:
            print("Usuário admin já existe.")

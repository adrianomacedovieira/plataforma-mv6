import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, redirect, url_for, session
from src.models.user import db, User
from src.routes.auth import auth_bp
from src.routes.client import client_bp
from src.routes.admin import admin_bp
from src.routes.chat import chat_bp
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plataforma_mv6.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados
db.init_app(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(client_bp, url_prefix='/client')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(chat_bp, url_prefix='/chat')

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('client.dashboard'))
    return redirect(url_for('auth.login'))

# Criar tabelas do banco de dados
with app.app_context():
    db.create_all()
    
    # Verificar se já existe um usuário administrador
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        # Criar usuário administrador
        admin = User(
            nome='Administrador',
            email='admin@plataformamv6.com',
            telefone='(11) 99999-9999',
            cpf='000.000.000-00',
            role='admin',
            status='ativo'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

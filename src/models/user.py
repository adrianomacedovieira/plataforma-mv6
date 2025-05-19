from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(10), default='ativo')
    role = db.Column(db.String(10), default='client')  # 'admin' ou 'client'
    
    # Relacionamentos
    credenciais = db.relationship('CredencialMT5', backref='user', lazy=True)
    conta = db.relationship('ContaCliente', backref='user', lazy=True)
    aceites = db.relationship('AceiteTermos', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class CredencialMT5(db.Model):
    __tablename__ = 'credenciais_mt5'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    login_mt5 = db.Column(db.String(50), nullable=False)
    senha_mt5 = db.Column(db.String(200), nullable=False)  # Armazenada criptografada
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CredencialMT5 {self.login_mt5}>'


class ContaCliente(db.Model):
    __tablename__ = 'contas_cliente'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    saldo = db.Column(db.Float, default=0.0)
    valor_investido = db.Column(db.Float, default=0.0)
    rendimento_dia = db.Column(db.Float, default=0.0)
    premio_acumulado = db.Column(db.Float, default=0.0)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContaCliente {self.id}>'


class Termo(db.Model):
    __tablename__ = 'termos'
    
    id = db.Column(db.Integer, primary_key=True)
    versao = db.Column(db.String(10), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    aceites = db.relationship('AceiteTermos', backref='termo', lazy=True)
    
    def __repr__(self):
        return f'<Termo {self.versao}>'


class AceiteTermos(db.Model):
    __tablename__ = 'aceites_termos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    termo_id = db.Column(db.Integer, db.ForeignKey('termos.id'), nullable=False)
    data_aceite = db.Column(db.DateTime, default=datetime.utcnow)
    ip_aceite = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f'<AceiteTermos {self.id}>'

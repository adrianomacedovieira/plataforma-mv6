from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models.user import db, User, ContaCliente
from datetime import datetime
import functools

client_bp = Blueprint('client', __name__)

# Decorator para verificar se o usuário está logado
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@client_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    conta = ContaCliente.query.filter_by(user_id=user_id).first()
    
    # Dados fictícios para demonstração
    # Em um ambiente real, esses dados viriam de uma API ou banco de dados
    operacoes = [
        {
            'data': '2025-05-16',
            'tipo': 'Compra',
            'ativo': 'PETR4',
            'quantidade': 100,
            'valor': 28.45,
            'resultado': '+R$ 245,00'
        },
        {
            'data': '2025-05-15',
            'tipo': 'Venda',
            'ativo': 'VALE3',
            'quantidade': 50,
            'valor': 68.32,
            'resultado': '+R$ 132,50'
        },
        {
            'data': '2025-05-14',
            'tipo': 'Compra',
            'ativo': 'ITUB4',
            'quantidade': 200,
            'valor': 32.18,
            'resultado': '-R$ 87,00'
        }
    ]
    
    return render_template('client/dashboard.html', user=user, conta=conta, operacoes=operacoes)

@client_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        
        user.nome = nome
        user.telefone = telefone
        db.session.commit()
        
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('client.perfil'))
    
    return render_template('client/perfil.html', user=user)

@client_bp.route('/operacoes')
@login_required
def operacoes():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Dados fictícios para demonstração
    operacoes = [
        {
            'data': '2025-05-16',
            'tipo': 'Compra',
            'ativo': 'PETR4',
            'quantidade': 100,
            'valor': 28.45,
            'resultado': '+R$ 245,00'
        },
        {
            'data': '2025-05-15',
            'tipo': 'Venda',
            'ativo': 'VALE3',
            'quantidade': 50,
            'valor': 68.32,
            'resultado': '+R$ 132,50'
        },
        {
            'data': '2025-05-14',
            'tipo': 'Compra',
            'ativo': 'ITUB4',
            'quantidade': 200,
            'valor': 32.18,
            'resultado': '-R$ 87,00'
        },
        {
            'data': '2025-05-13',
            'tipo': 'Venda',
            'ativo': 'BBDC4',
            'quantidade': 150,
            'valor': 22.75,
            'resultado': '+R$ 178,50'
        },
        {
            'data': '2025-05-12',
            'tipo': 'Compra',
            'ativo': 'ABEV3',
            'quantidade': 300,
            'valor': 15.22,
            'resultado': '+R$ 93,00'
        }
    ]
    
    return render_template('client/operacoes.html', user=user, operacoes=operacoes)

@client_bp.route('/termos', methods=['GET', 'POST'])
@login_required
def termos():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        aceite = request.form.get('aceite')
        
        if aceite:
            # Em um ambiente real, registraríamos o aceite no banco de dados
            flash('Termos aceitos com sucesso!', 'success')
            return redirect(url_for('client.dashboard'))
        else:
            flash('Você precisa aceitar os termos para continuar.', 'danger')
    
    return render_template('client/termos.html', user=user)

@client_bp.route('/btg-onboarding')
@login_required
def btg_onboarding():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    return render_template('client/btg_onboarding.html', user=user)

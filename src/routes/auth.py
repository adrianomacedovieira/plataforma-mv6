from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from src.models.user import db, User, CredencialMT5, ContaCliente
from datetime import datetime
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            user.ultimo_acesso = datetime.utcnow()
            db.session.commit()
            
            # Verificar se o usuário já aceitou os termos
            if not user.aceites:
                return redirect(url_for('client.termos'))
            
            return redirect(url_for('client.dashboard'))
        else:
            flash('Email ou senha inválidos. Por favor, tente novamente.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/primeiro-acesso', methods=['GET', 'POST'])
def primeiro_acesso():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        cpf = request.form.get('cpf')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        login_mt5 = request.form.get('login_mt5')
        senha_mt5 = request.form.get('senha_mt5')
        
        # Validações básicas
        if not all([nome, email, telefone, cpf, password, confirm_password, login_mt5, senha_mt5]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('auth/primeiro_acesso.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/primeiro_acesso.html')
        
        # Verificar se o email ou CPF já estão cadastrados
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'danger')
            return render_template('auth/primeiro_acesso.html')
        
        if User.query.filter_by(cpf=cpf).first():
            flash('Este CPF já está cadastrado.', 'danger')
            return render_template('auth/primeiro_acesso.html')
        
        # Criar novo usuário
        new_user = User(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf,
            status='ativo'
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.flush()  # Para obter o ID do usuário
        
        # Criar credenciais MT5
        # Criptografar a senha do MT5 antes de armazenar
        mt5_credentials = CredencialMT5(
            user_id=new_user.id,
            login_mt5=login_mt5,
            senha_mt5=generate_password_hash(senha_mt5)
        )
        
        # Criar conta do cliente
        client_account = ContaCliente(
            user_id=new_user.id
        )
        
        db.session.add(mt5_credentials)
        db.session.add(client_account)
        db.session.commit()
        
        # Autenticar o usuário
        session['user_id'] = new_user.id
        
        flash('Cadastro realizado com sucesso! Agora vamos orientá-lo na abertura da sua conta no BTG Pactual.', 'success')
        return redirect(url_for('client.btg_onboarding'))
    
    return render_template('auth/primeiro_acesso.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('public.index'))

@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Em um ambiente real, enviaríamos um email com um link para redefinir a senha
            # Para simplificar, vamos apenas simular isso
            flash('Enviamos um email com instruções para redefinir sua senha.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Email não encontrado.', 'danger')
    
    return render_template('auth/recuperar_senha.html')

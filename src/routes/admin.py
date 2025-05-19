from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models.user import db, User, ContaCliente, CredencialMT5, AceiteTermos, Termo
from datetime import datetime
import functools

admin_bp = Blueprint('admin', __name__)

# Decorator para verificar se o usuário é administrador
def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'danger')
            return redirect(url_for('auth.login'))
        
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        # Verificar se o usuário é administrador (role = 'admin')
        if not user or not user.role == 'admin':
            flash('Você não tem permissão para acessar esta área.', 'danger')
            return redirect(url_for('client.dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Contagem de usuários
    total_users = User.query.count()
    active_users = User.query.filter_by(status='ativo').count()
    
    # Últimos usuários cadastrados
    recent_users = User.query.order_by(User.data_criacao.desc()).limit(5).all()
    
    # Estatísticas de contas
    total_invested = db.session.query(db.func.sum(ContaCliente.valor_investido)).scalar() or 0
    total_balance = db.session.query(db.func.sum(ContaCliente.saldo)).scalar() or 0
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users,
                          active_users=active_users,
                          recent_users=recent_users,
                          total_invested=total_invested,
                          total_balance=total_balance)

@admin_bp.route('/clientes')
@admin_required
def clientes():
    # Listar todos os clientes
    users = User.query.filter(User.role != 'admin').order_by(User.nome).all()
    return render_template('admin/clientes.html', users=users)

@admin_bp.route('/cliente/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def cliente_detalhes(user_id):
    user = User.query.get_or_404(user_id)
    conta = ContaCliente.query.filter_by(user_id=user_id).first()
    
    if request.method == 'POST':
        # Atualizar dados da conta
        conta.saldo = float(request.form.get('saldo', 0))
        conta.valor_investido = float(request.form.get('valor_investido', 0))
        conta.rendimento_dia = float(request.form.get('rendimento_dia', 0))
        conta.premio_acumulado = float(request.form.get('premio_acumulado', 0))
        conta.data_atualizacao = datetime.utcnow()
        
        # Atualizar status do usuário
        user.status = request.form.get('status', 'ativo')
        
        db.session.commit()
        
        flash('Dados do cliente atualizados com sucesso!', 'success')
        return redirect(url_for('admin.cliente_detalhes', user_id=user_id))
    
    return render_template('admin/cliente_detalhes.html', user=user, conta=conta)

@admin_bp.route('/notificacoes', methods=['GET', 'POST'])
@admin_required
def notificacoes():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        mensagem = request.form.get('mensagem')
        destinatarios = request.form.getlist('destinatarios')
        
        # Em um sistema real, enviaríamos notificações para os usuários
        # Para simplificar, apenas simulamos o envio
        
        if 'todos' in destinatarios:
            # Enviar para todos os usuários
            users = User.query.filter(User.role != 'admin').all()
            count = len(users)
        else:
            # Enviar para usuários específicos
            users = User.query.filter(User.id.in_(destinatarios)).all()
            count = len(users)
        
        flash(f'Notificação enviada com sucesso para {count} usuários!', 'success')
        return redirect(url_for('admin.notificacoes'))
    
    # Listar todos os usuários para seleção
    users = User.query.filter(User.role != 'admin').order_by(User.nome).all()
    return render_template('admin/notificacoes.html', users=users)

@admin_bp.route('/operacoes')
@admin_required
def operacoes():
    # Em um sistema real, buscaríamos operações do banco de dados
    # Para simplificar, usamos dados fictícios
    
    operacoes = [
        {
            'id': 1,
            'cliente': 'João Silva',
            'data': '2025-05-16',
            'tipo': 'Compra',
            'ativo': 'PETR4',
            'quantidade': 100,
            'valor': 28.45,
            'resultado': '+R$ 245,00'
        },
        {
            'id': 2,
            'cliente': 'Maria Souza',
            'data': '2025-05-15',
            'tipo': 'Venda',
            'ativo': 'VALE3',
            'quantidade': 50,
            'valor': 68.32,
            'resultado': '+R$ 132,50'
        },
        {
            'id': 3,
            'cliente': 'Pedro Santos',
            'data': '2025-05-14',
            'tipo': 'Compra',
            'ativo': 'ITUB4',
            'quantidade': 200,
            'valor': 32.18,
            'resultado': '-R$ 87,00'
        }
    ]
    
    return render_template('admin/operacoes.html', operacoes=operacoes)

@admin_bp.route('/termos', methods=['GET', 'POST'])
@admin_required
def termos():
    if request.method == 'POST':
        versao = request.form.get('versao')
        texto = request.form.get('texto')
        
        # Desativar termos anteriores
        Termo.query.update({Termo.ativo: False})
        
        # Criar novo termo
        novo_termo = Termo(
            versao=versao,
            texto=texto,
            ativo=True
        )
        
        db.session.add(novo_termo)
        db.session.commit()
        
        flash('Novos termos e condições criados com sucesso!', 'success')
        return redirect(url_for('admin.termos'))
    
    # Buscar termos ativos
    termo_ativo = Termo.query.filter_by(ativo=True).first()
    
    # Listar todos os termos
    termos = Termo.query.order_by(Termo.data_criacao.desc()).all()
    
    return render_template('admin/termos.html', termo_ativo=termo_ativo, termos=termos)

@admin_bp.route('/relatorios')
@admin_required
def relatorios():
    return render_template('admin/relatorios.html')

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.user import db, User
from src.models.chat import ChatMessage
from datetime import datetime
import functools

chat_bp = Blueprint('chat', __name__)

# Decorator para verificar se o usuário está logado
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@chat_bp.route('/cliente')
@login_required
def cliente():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Buscar mensagens do usuário
    messages = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at).all()
    
    # Marcar mensagens do admin como lidas
    unread_messages = ChatMessage.query.filter_by(user_id=user_id, is_from_admin=True, is_read=False).all()
    for msg in unread_messages:
        msg.is_read = True
    
    db.session.commit()
    
    return render_template('client/chat.html', user=user, messages=messages)

@chat_bp.route('/enviar', methods=['POST'])
@login_required
def enviar():
    user_id = session.get('user_id')
    message_text = request.form.get('message')
    
    if not message_text:
        flash('A mensagem não pode estar vazia.', 'danger')
        return redirect(url_for('chat.cliente'))
    
    # Criar nova mensagem
    new_message = ChatMessage(
        user_id=user_id,
        message=message_text,
        is_from_admin=False,
        is_read=False
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    flash('Mensagem enviada com sucesso!', 'success')
    return redirect(url_for('chat.cliente'))

@chat_bp.route('/admin')
@login_required
def admin():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Verificar se o usuário é administrador
    if not user or not user.role == 'admin':
        flash('Você não tem permissão para acessar esta área.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    # Buscar todos os usuários que têm mensagens
    users_with_messages = db.session.query(User).join(ChatMessage, User.id == ChatMessage.user_id).distinct().all()
    
    # Contar mensagens não lidas para cada usuário
    for u in users_with_messages:
        u.unread_count = ChatMessage.query.filter_by(user_id=u.id, is_from_admin=False, is_read=False).count()
    
    return render_template('admin/chat.html', users=users_with_messages)

@chat_bp.route('/admin/conversa/<int:user_id>')
@login_required
def admin_conversa(user_id):
    admin_id = session.get('user_id')
    admin = User.query.get(admin_id)
    
    # Verificar se o usuário é administrador
    if not admin or not admin.role == 'admin':
        flash('Você não tem permissão para acessar esta área.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    # Buscar o cliente
    cliente = User.query.get_or_404(user_id)
    
    # Buscar mensagens do cliente
    messages = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at).all()
    
    # Marcar mensagens do cliente como lidas
    unread_messages = ChatMessage.query.filter_by(user_id=user_id, is_from_admin=False, is_read=False).all()
    for msg in unread_messages:
        msg.is_read = True
    
    db.session.commit()
    
    return render_template('admin/conversa.html', cliente=cliente, messages=messages)

@chat_bp.route('/admin/responder', methods=['POST'])
@login_required
def admin_responder():
    admin_id = session.get('user_id')
    admin = User.query.get(admin_id)
    
    # Verificar se o usuário é administrador
    if not admin or not admin.role == 'admin':
        flash('Você não tem permissão para acessar esta área.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    user_id = request.form.get('user_id')
    message_text = request.form.get('message')
    
    if not user_id or not message_text:
        flash('Dados inválidos.', 'danger')
        return redirect(url_for('chat.admin'))
    
    # Criar nova mensagem
    new_message = ChatMessage(
        user_id=user_id,
        admin_id=admin_id,
        message=message_text,
        is_from_admin=True,
        is_read=False
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    flash('Resposta enviada com sucesso!', 'success')
    return redirect(url_for('chat.admin_conversa', user_id=user_id))

@chat_bp.route('/check-new-messages')
@login_required
def check_new_messages():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if user.role == 'admin':
        # Para administradores, verificar se há novas mensagens de clientes
        unread_count = ChatMessage.query.filter_by(is_from_admin=False, is_read=False).count()
    else:
        # Para clientes, verificar se há novas mensagens de administradores
        unread_count = ChatMessage.query.filter_by(user_id=user_id, is_from_admin=True, is_read=False).count()
    
    return jsonify({'unread_count': unread_count})

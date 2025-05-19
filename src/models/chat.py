from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models.user import db, User, ContaCliente
from datetime import datetime
import functools

# Modelo para mensagens de chat
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_from_admin = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', foreign_keys=[user_id], backref='sent_messages')
    admin = db.relationship('User', foreign_keys=[admin_id], backref='admin_messages')
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>'

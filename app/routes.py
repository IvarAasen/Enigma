from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Message
from . import db

routes = Blueprint('routes', __name__)

@routes.route('/')
@login_required
def chat():
    users = User.query.filter(User.id != current_user.id).all()
    selected_user_id = request.args.get('user')
    selected_user = None
    messages = []

    if selected_user_id:
        selected_user = User.query.get(int(selected_user_id))

        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == selected_user.id)) |
            ((Message.sender_id == selected_user.id) & (Message.recipient_id == current_user.id))
        ).order_by(Message.timestamp.asc()).all()

    return render_template('chat.html', users=users, selected_user=selected_user, messages=messages)

@routes.route('/send', methods=['POST'])
@login_required
def send_message():
    recipient_id = int(request.form.get('recipient_id'))
    content = request.form.get('content')

    if content:
        new_message = Message(sender_id=current_user.id, recipient_id=recipient_id, content=content)
        db.session.add(new_message)
        db.session.commit()

    return redirect(url_for('routes.chat', user=recipient_id))

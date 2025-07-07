from flask import render_template, request, redirect, url_for, session, current_app, Blueprint
from flask_login import login_required, current_user
from .models import User, Message, FriendRequest
from . import db
from app.enigma_machine import enigma, initialize_machine_from_password
import os
from werkzeug.utils import secure_filename

routes = Blueprint("routes", __name__)


@routes.route('/')
@login_required
def chat():
    users = User.query.filter(User.id != current_user.id).all()
    selected_user_id = request.args.get('user')
    selected_user = None
    messages = []
    decrypted_messages = []

    if selected_user_id:
        selected_user = User.query.get(int(selected_user_id))
        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == selected_user.id)) |
            ((Message.sender_id == selected_user.id) & (Message.recipient_id == current_user.id))
        ).order_by(Message.timestamp.asc()).all()

        password = session.get("chat_password")
        if password:
            try:
                rotor_a, rotor_b, rotor_c, reflector = initialize_machine_from_password(password)
                for msg in messages:
                    decrypted = enigma(msg.content, rotor_a, rotor_b, rotor_c, reflector)
                    decrypted_messages.append({
                        "sender_id": msg.sender_id,
                        "content": decrypted
                    })
            except:
                decrypted_messages = [{"sender_id": msg.sender_id, "content": "[Decryption failed]"} for msg in messages]
        else:
            decrypted_messages = [{"sender_id": msg.sender_id, "content": "[Encrypted]"} for msg in messages]

    return render_template("chat.html", users=users, selected_user=selected_user, messages=decrypted_messages, password_set=bool(session.get("chat_password")))

@routes.route('/set_password/<int:user>', methods=['POST'])
@login_required
def set_password(user):
    password = request.form.get("password")
    session["chat_password"] = password
    return redirect(url_for('routes.chat', user=user))

@routes.route('/search', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('q')
    results = []
    if query:
        results = User.query.filter(User.username.ilike(f"%{query}%")).all()
    return render_template("search.html", results=results, query=query)

@routes.route('/add_friend/<int:user_id>')
@login_required
def add_friend(user_id):
    existing = FriendRequest.query.filter_by(from_user_id=current_user.id, to_user_id=user_id).first()
    if not existing:
        req = FriendRequest(from_user_id=current_user.id, to_user_id=user_id)
        db.session.add(req)
        db.session.commit()
    return redirect(url_for('routes.search_users'))

@routes.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        file = request.files.get('profile_pic')
        if file:
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.root_path, 'static/profile_pics', filename)
            file.save(save_path)
            current_user.profile_picture = filename
            db.session.commit()
    return render_template("profile.html")

@routes.route('/friend_requests')
@login_required
def friend_requests():
    pending = FriendRequest.query.filter_by(to_user_id=current_user.id, status='pending').all()
    return render_template("friend_requests.html", requests=pending)

@routes.route('/accept_friend/<int:req_id>')
@login_required
def accept_friend(req_id):
    req = FriendRequest.query.get(req_id)
    if req and req.to_user_id == current_user.id:
        req.status = 'accepted'
        db.session.commit()
    return redirect(url_for('routes.friend_requests'))

@routes.route('/decline_friend/<int:req_id>')
@login_required
def decline_friend(req_id):
    req = FriendRequest.query.get(req_id)
    if req and req.to_user_id == current_user.id:
        req.status = 'declined'
        db.session.commit()
    return redirect(url_for('routes.friend_requests'))

@routes.route('/send_message', methods=['POST'])
@login_required
def send_message():
    recipient_id = int(request.form.get('recipient_id'))
    content = request.form.get('content')
    password = request.form.get('password')

    if content and password:
        rotor_a, rotor_b, rotor_c, reflector = initialize_machine_from_password(password)
        encrypted = enigma(content, rotor_a, rotor_b, rotor_c, reflector)

        new_message = Message(sender_id=current_user.id, recipient_id=recipient_id, content=encrypted)
        db.session.add(new_message)
        db.session.commit()

    return redirect(url_for('routes.chat', user=recipient_id))

from flask_socketio import emit, join_room
from flask_login import current_user
from . import socketio

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)

@socketio.on('send_message')
def handle_message(data):
    emit('receive_message', data, room=data['room'])

import uuid

from flask import session
from flask_socketio import emit, join_room, leave_room
from markupsafe import Markup

from .. import socketio

active_users = {}

@socketio.on('joined', namespace='/chat')
def joined(message):
    global active_users
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    session['uid'] = str(uuid.uuid4())
    join_room(room)
    join_room(session.get("uid"))
    active_users[session.get('name')] = session.get("uid")
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)
    emit('status', {'msg': 'You are waiting for private messages.'}, room=session.get("uid"))


@socketio.on('text', namespace='/chat')
def text(message):
    global active_users
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    msg = message['msg']
    if msg.split(' ', 1)[0][0:1] == "#":
        if len(msg.split(' ')) > 1:
            to = msg.split(' ', 1)[0][1:]
            msg = msg.split(' ', 1)[1]
            if to in active_users:
                emit('message', {'msg': '(To) ' + to + ': ' + Markup.escape(msg)})
                emit('message', {'msg': '(From) ' + session.get('name') + ': ' + Markup.escape(msg)}, room=active_users[to])
    else:
        room = session.get('room')
        emit('message', {'msg': session.get('name') + ': ' + Markup.escape(msg)}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)


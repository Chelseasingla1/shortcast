from flask_socketio import emit
from .views import live_podcast

from app import socketio
# # Define your live podcast events here
# @live_podcast.before_app_first_request
# def setup_socketio():

#
# @socketio.on('connect')
# def handle_connect():
#     print("A user has connected")
#     emit('message', {'data': 'Connected to the live podcast stream!'})
#
# @socketio.on('disconnect')
# def handle_disconnect():
#     print("A user has disconnected")
#
# @socketio.on('new_message')
# def handle_message(data):
#     # Handle live podcast chat messages or other interactions
#     print(f"Received message: {data}")
#     emit('new_message', data, broadcast=True)  # Broadcast the message to all clients

from flask import Flask
from .slack.routes import slack


server = Flask(__name__)
server.register_blueprint(slack)

@server.route('/')
def print_welcome_page():
  return 'Welcome to the Cloud Webhook by Kevocde'

def create_app():
  return server

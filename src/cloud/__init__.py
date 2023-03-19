from flask import Flask


server = Flask(__name__)

@server.route('/')
def welcome_page():
  return 'Welcome to the Cloud Webhook by Kevocde'

def create_app():
  return server

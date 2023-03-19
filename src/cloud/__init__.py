from flask import Flask, request


server = Flask(__name__)

@server.route('/')
def welcome_page():
  return 'Welcome to the Cloud Webhook by Kevocde'

@server.route('/slack/validation', methods=['POST'])
def validate_slack_app():
  data = request.get_json()
  return data['challenge']

def create_app():
  return server

from flask import Flask


Webhook = Flask(__name__)

@Webhook.route('/')
def welcome_page():
  return 'Welcome to the Cloud Webhook by Kevocde'

def create_app():
  return Webhook

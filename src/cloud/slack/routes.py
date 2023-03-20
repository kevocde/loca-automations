from flask import Blueprint, request
from ..authentication import Autentication


slack = Blueprint('slack', __name__)

@slack.route('/webhooks/slack', methods=['POST'])
@Autentication.slack_auth
def validate_slack_app():
    data = request.get_json()
    return data['challenge']

from flask import Blueprint, request


slack = Blueprint('slack', __name__)

@slack.route('/webhooks/slack', methods=['POST'])
def validate_slack_app():
    data = request.get_json()
    return data['challenge']

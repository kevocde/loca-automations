from flask import request, abort
import os

class Autentication:
    _authentication_keys = {
        value.split(":")[0]: value.split(":")[1] for value in os.environ.get("CLOUD_AUTHS", "").split(",") if value
    }

    @classmethod
    def authenticate_by_header(cls, header='Authorization', kind="Bearer", value=""):
        auth_header = request.headers.get(header)

        if not auth_header or auth_header != "{} {}".format(kind, value):
            abort(401, "No authentication header provided")

    @classmethod
    def slack_auth(cls, f):
        def decorated(*args, **kwargs):
            Autentication.authenticate_by_header(value=Autentication._authentication_keys.get("slack"))
            return f(*args, **kwargs)
        return decorated

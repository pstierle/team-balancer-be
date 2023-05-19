import requests
import jwt
import uuid
from google_auth_oauthlib.flow import Flow
from os import path, environ
from flask import session, redirect, request, Blueprint
from util import get_or_create, get_date
from database import db, User

auth_router = Blueprint('auth_router', __name__)

client_secrets_file = path.abspath(
    path.join(path.dirname(__file__), "..", "..", "client_secret.json"))

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_uri="http://127.0.0.1:3000/auth/google/callback"
)

environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@auth_router.route('/auth/google/login')
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth_router.route('/auth/google/callback')
def google_callback():
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    response = requests.get(
        "https://oauth2.googleapis.com/tokeninfo?id_token=" + credentials.id_token)
    response_dict = response.json()
    email = response_dict.get('email')
    user = get_or_create(db.session, User, email=email, id=str(uuid.uuid4()))
    token = jwt.encode(
        {"user_id": user.id, "expires_at": get_date(1)}, environ["jwt_key"], algorithm="HS256")
    redirect_url = 'http://localhost:4200/auth/' + token
    return redirect(redirect_url, code=302)

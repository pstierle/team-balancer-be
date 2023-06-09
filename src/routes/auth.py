import requests
import jwt
import uuid
from google_auth_oauthlib.flow import Flow
from os import environ
from flask import session, redirect, request, Blueprint
from util import get_date
from database import db, User

auth_router = Blueprint("auth_router", __name__)

flow = Flow.from_client_config(
    client_config={
        "web": {
            "client_id": environ["oauth_client_id"],
            "project_id": environ["oauth_project_id"],
            "auth_uri": environ["oauth_auth_uri"],
            "token_uri": environ["oauth_token_uri"],
            "auth_provider_x509_cert_url": environ["oauth_auth_provider_x509_cert_url"],
            "client_secret": environ["oauth_client_secret"],
            "redirect_uris": [environ["oauth_redirect_uri"]],
            "javascript_origins": [environ["oauth_javascript_origin"]],
        }
    },
    scopes=["https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri=environ["oauth_redirect_uri"],
)

environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@auth_router.route("/auth/google/login")
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth_router.route("/auth/google/callback")
def google_callback():
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    response = requests.get(
        "https://oauth2.googleapis.com/tokeninfo?id_token=" + credentials.id_token
    )
    response_dict = response.json()
    email = response_dict.get("email")
    user = User.query.filter(User.email == email).first()
    if user == None:
        user = User(email=email, id=str(uuid.uuid4()))
        db.session.add(user)
        db.session.commit()
    token = jwt.encode(
        {"user_id": user.id, "expires_at": get_date(1)},
        environ["jwt_key"],
        algorithm="HS256",
    )
    redirect_url = f'{environ["frontend_url"]}/auth/{token}'
    return redirect(redirect_url, code=302)

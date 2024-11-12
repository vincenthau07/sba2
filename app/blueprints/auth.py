import flask
from app.helpers import *
import app.error_message as error_msg
from datetime import datetime
from config import TIME_ZONE
# from google_auth_oauthlib.flow import Flow
import json
from authlib.integrations.flask_client import OAuth

with open("app/client_secret.json", "r") as jfile:
    OAUTH = json.load(jfile)

oauth = OAuth()
google = oauth.register(
    name='google',
    client_id="486522423247-paab3n7imi4182bnioupbgn2tvkk1tba.apps.googleusercontent.com",
    client_secret="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",
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


# GOOGLE_CLIENT_ID = OAUTH['web']['client_id']
# flow = Flow.from_client_secrets_file(
#     client_secrets_file="app/client_secret.json",
#     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
# )

blueprint = flask.Blueprint("auth", __name__)

@blueprint.before_request
def make_session_permanent():
    flask.session.permanent = True
    flask.session.modified = True


@blueprint.route('/')
def main():
    if sessionValidity(session=flask.session):
        return flask.redirect('/home')
    else:
        return flask.render_template('main.html')
@blueprint.route('/login', methods=["GET"])
def login():
    if sessionValidity(session=flask.session):
        return flask.redirect('/home')
    else:
        return flask.render_template('login.html')
        

@blueprint.route('/login', methods=["POST"], endpoint= "login post")
def login_POST():
    if "google-btn" in flask.request.form:
        # authorization_url, state = flow.authorization_url()
        # flask.session["state"] = state
        # return flask.redirect(authorization_url)
        redirect_uri = flask.url_for('auth.callback', _external=True)
        return google.authorize_redirect(redirect_uri)

    else:
        user = flask.request.form["userid"]
        pw = flask.request.form["password"]
        #print(get_by_primary_key("user", user, "PASSWORD"))
        if user == '':
            error = error_msg.login.empty_username
        elif pw == '':
            error = error_msg.login.empty_password
        else:
            try:
                if pw == get_by_primary_key("user", user, "PASSWORD"):
                    flask.session['UID'] = user
                    flask.session.permanent = True
                    sql("INSERT INTO login (UID, IP, TIME) VALUES (?,?,?)", user, flask.request.environ.get('HTTP_X_REAL_IP', flask.request.remote_addr), str(datetime.now(TIME_ZONE).replace(tzinfo=None)), commit=True)
                    return flask.jsonify({})
            finally:
                error = error_msg.login.invalid_account
        
        return flask.jsonify({'error': error})

@blueprint.route('/callback', endpoint='callback')
def callback():
    token = google.authorize_access_token()
    email = google.get('userinfo').json()['email']
    result = sql("SELECT UID FROM user WHERE EMAIL = ?", email).result
    if len(result) == 0:
        return flask.redirect('/login')
    else:
        user = result[0][0]
        flask.session['UID'] = user
        flask.session.permanent = True
        sql("INSERT INTO login (UID, IP, TIME) VALUES (?,?,?)", user, flask.request.environ.get('HTTP_X_REAL_IP', flask.request.remote_addr), str(datetime.now(TIME_ZONE).replace(tzinfo=None)), commit=True)
        return flask.redirect('/home')

@blueprint.route('/logout')
@verifySession(flask.session)
def logout(permission):
    flask.session.clear()
    return flask.redirect('/login')
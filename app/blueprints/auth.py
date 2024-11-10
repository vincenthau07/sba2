import flask
from app.helpers import *
from datetime import datetime
from config import TIME_ZONE
# import modules.sql as sql

blueprint = flask.Blueprint("login", __name__)

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
    user = flask.request.form["userid"]
    pw = flask.request.form["password"]
    #print(get_by_primary_key("user", user, "PASSWORD"))
    if user == '':
        error = "Empty username"
    elif pw == '':
        error = "Empty password"
    else:
        try:
            if pw == get_by_primary_key("user", user, "PASSWORD"):
                flask.session['UID'] = user
                flask.session.permanent = True
                sql("INSERT INTO login (UID, IP, TIME) VALUES (?,?,?)", user, flask.request.environ.get('HTTP_X_REAL_IP', flask.request.remote_addr), str(datetime.now(TIME_ZONE).replace(tzinfo=None)), commit=True)
                return flask.jsonify({'success': True})
        finally:
            error = "Invalid username or password"
    
    return flask.jsonify({'success': False, 'msg': error})

@blueprint.route('/logout')
@verifySession(flask.session)
def logout(permission):
    del flask.session['UID']
    flask.session.permanent = False
    return flask.redirect('/login')
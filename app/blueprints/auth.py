import flask
from app.helpers import *
from datetime import datetime
# import modules.sql as sql

blueprint = flask.Blueprint("login", __name__)

@blueprint.route('/')
@blueprint.route('/login', methods=["GET","POST"])
def login():
    if flask.request.method == 'POST':
        user = flask.request.form["userid"]
        pw = flask.request.form["password"]
        #print(get_by_primary_key("user", user, "PASSWORD"))
        if user == '':
            error = "Empty username"
        elif pw == '':
            error = "Empty password"
        else:
            if pw == get_by_primary_key("user", user, "PASSWORD"):
                flask.session['UID'] = user
                flask.session['password'] = pw
                flask.session.permanent = True
                sql("INSERT INTO login (UID, IP, TIME) VALUES (?,?,?)", user, flask.request.remote_addr, str(datetime.now()), commit=True)
                return flask.redirect('/home')
            error = "Invalid username or password"
        
        return flask.render_template('login.html', error=error)
    
    elif flask.request.method == 'GET':
        if sessionValidity(session=flask.session):
            return flask.redirect('/home')
        else:
            return flask.render_template('login.html')
        
@blueprint.route('/logout')
@verifySession(flask.session)
def logout(permission):
    del flask.session['UID']
    del flask.session['password']
    flask.session.permanent = False
    return flask.redirect('/login')
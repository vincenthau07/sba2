from __main__ import app
import flask
import modules.sql as sql

@app.route('/')
def root():
    return flask.redirect('/login')

@app.route('/login', methods=["GET","POST"])
def login():
    if flask.request.method == 'POST':
        user = flask.request.form["userid"]
        pw = flask.request.form["password"]
        if user == '':
            error = "Empty username"
        elif pw == '':
            error = "Empty password"
        else:
            if pw == sql.commands.userPassword(user):
                flask.session['UID'] = user
                flask.session['password'] = pw
                flask.session.permanent = True
                return flask.redirect('/home')
            error = "Invalid username or password"
        return flask.render_template('login.html', error=error)
    
    elif flask.request.method == 'GET':
        if sql.commands.sessionValidity(session=flask.session):
            return flask.redirect('/home')
        else:
            return flask.render_template('login.html')
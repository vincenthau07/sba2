from __main__ import app
import flask
import modules.sql as sql

@app.route('/logout')
def logout():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    del flask.session['UID']
    del flask.session['password']
    flask.session.permanent = False
    return flask.redirect('/login')
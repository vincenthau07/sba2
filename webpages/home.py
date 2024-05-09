from __main__ import app
import flask
import modules.sql as sql

@app.route('/home')
def home():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    
    permission = sql.commands.rolePermissions(flask.session.get('UID'))
    
    return flask.render_template('home.html', permission = permission, username = sql.commands.userName(flask.session.get('UID')))
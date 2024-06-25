import flask
import modules.sql as sql

home_bp = flask.Blueprint("home", __name__)

@home_bp.route('/home')
def home():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    
    permission = sql.commands.rolePermissions(flask.session.get('UID'))
    
    return flask.render_template('home.html', permission = permission, username = sql.commands.userName(flask.session.get('UID')))
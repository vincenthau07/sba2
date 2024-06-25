import flask
import modules.sql as sql

logout_bp = flask.Blueprint("logout", __name__)

@logout_bp.route('/logout')
def logout():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    del flask.session['UID']
    del flask.session['password']
    flask.session.permanent = False
    return flask.redirect('/login')
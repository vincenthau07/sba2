import flask
from app.helpers import *
from config import TIME_ZONE

blueprint = flask.Blueprint("home", __name__)

@blueprint.route('/home')
@verifySession(flask.session)
def home(permission):   
    return flask.render_template('home.html', permission = permission, username = get_by_primary_key("user", flask.session['UID'], "UNAME"), tz=TIME_ZONE)
import flask
from app.helpers import *
from datetime import datetime
from config import TIME_ZONE
import app.error_message as error_msg
# import modules.sql as sql

blueprint = flask.Blueprint("myAccount", __name__)

@blueprint.route('/account', methods=["GET"])
@verifySession(flask.session)
def account(permission):
    data = get_by_primary_key('user', flask.session["UID"], ('UID', 'SEX', 'EMAIL', 'UNAME'))
    return flask.render_template('account.html', data = data, permission = permission, tz=TIME_ZONE)

@blueprint.route('/account/update1', methods=["POST"], endpoint = "accountPersonalInfo")
@verifySession(flask.session)
def accountPersonalInfo(permission):
    try:
        email = None if flask.request.form["EMAIL"] == '' else flask.request.form["EMAIL"]
        sql("UPDATE user SET SEX=?, EMAIL=?, UNAME=? WHERE UID = ?",flask.request.form["SEX"] ,email ,flask.request.form['UNAME'], flask.session["UID"], commit=True)
        return flask.jsonify({'data': get_by_primary_key('user', flask.session["UID"], ('UID', 'SEX', 'EMAIL', 'UNAME'))})
    except Exception as error:
        return flask.jsonify({'error': str(error)})

@blueprint.route('/account/update2', methods=["POST"], endpoint = "accountPW")
@verifySession(flask.session)
def accountPW(permission):
    if flask.request.form['OLD_PASSWORD'] != get_by_primary_key("user", flask.session['UID'], "PASSWORD"):
        return flask.jsonify({"error": error_msg.account.incorrect_current_password})
    if len(flask.request.form['PASSWORD1']) < 8:
        return flask.jsonify({"error": error_msg.account.weak_new_password})
    if flask.request.form['PASSWORD1'] != flask.request.form['PASSWORD2']:
        return flask.jsonify({"error": error_msg.account.new_passwords_not_match})
    sql("UPDATE user SET PASSWORD=? WHERE UID = ?", flask.request.form['PASSWORD1'], flask.session["UID"], commit=True)
    return flask.jsonify({})
import flask
from app.helpers import *
from config import TIME_ZONE

blueprint = flask.Blueprint("sql", __name__)

@blueprint.route('/sql', methods = ["GET"])
@verifySession(flask.session, role = "ADMIN")
def sqlWeb(permission):
    return flask.render_template('sql.html', 
                                 permission = permission, 
                                 tz = TIME_ZONE)
    
@blueprint.route('/sql', methods = ['POST'])
@verifySession(flask.session, role = "ADMIN")
def sqlResult(permission):
    cmds = flask.request.form["sql"]
    results = []
    for cmd in cmds.split(";"):
        if cmd.isspace() or len(cmd) == 0:
            continue
        try:
            result = sql(cmd, commit = True)

            if result.field:
                results.append([True, cmd, {'columns': result.field, 
                                          'data': result.result}]
                               )
            else:
                results.append([True, cmd]
                               )
        except Exception as error:
            results.append([False, cmd, str(error)])
    return flask.jsonify({"results": results})
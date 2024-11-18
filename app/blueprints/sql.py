import flask, datetime
from app.helpers import *
from config import TIME_ZONE

blueprint = flask.Blueprint("sql", __name__)

@blueprint.route('/sql', methods=["GET"])
@verifySession(flask.session, role="ADMIN")
def sqlWeb(permission):
    return flask.render_template('sql.html', permission=permission, tz=TIME_ZONE)
    
@blueprint.route('/sql', methods = ['POST'])
@verifySession(flask.session, role="ADMIN")
def sqlResult(permission):
    cmd = flask.request.form["sql"]
    code = ""
    results = []
    for i in cmd.split(";"):
        if i.isspace() or len(i) == 0:
            continue
        try:
            result = sql(i, commit=True)

            if result.field:
                results.append([True,i,{'columns': result.field, 'data': result.result}])
            else:
                results.append([True,i])
        except Exception as error:
            results.append([False,i,str(error)])
    return flask.jsonify({"results": results})
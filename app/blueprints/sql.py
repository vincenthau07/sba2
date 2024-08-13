import flask, datetime
from app.helpers import *

blueprint = flask.Blueprint("sql", __name__)

@blueprint.route('/sql', methods=["GET"])
@verifySession(flask.session, role="ADMIN")
def sqlWeb(permission):
    return flask.render_template('sql.html', permission=permission)
    
@blueprint.route('/sql', methods = ['POST'], endpoint = "sqlPOST")
@verifySession(flask.session, role="ADMIN")
def sqlResult(permission):
    cmd = flask.request.form["sql"]
    code = ""
    j = 1
    for i in cmd.split(";"):
        if i.isspace() or len(i) == 0:
            continue
        code+= f"<span id='badge'>statement #{j}</span>"
        try:
            result = sql.sql(i, commit=True)
            code+=f"{i}<span id='badge' style='background-color:#20c836'>Succeed</span>"
            if result.field:
                code+=html.table(result.field,result.result)
        except Exception as error:
            code+=f"{i}<span id='badge' style='background-color:#c82036'>Failed</span>"
            code+=html.linebreak()
            code+=f"Error: {error}"
        code+="<br>"
        j+=1
    return flask.jsonify({"code": code})
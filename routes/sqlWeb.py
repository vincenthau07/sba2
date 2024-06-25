import flask, datetime
import modules.sql as sql
import modules.html as html

sql_bp = flask.Blueprint("sql", __name__)

@sql_bp.route('/sql', methods=["GET", "POST"])

def sqlWeb():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))
    if permission["ROLE"]!="ADMIN":
        return flask.redirect('/home')
    
    if flask.request.method == 'POST':
        cmd = flask.request.form["sql"]
        code = ""

        j = 1
        for i in cmd.split(";"):
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
        return flask.render_template('sql.html', permission=permission, code=code, cmd = cmd)
    
    elif flask.request.method == 'GET':
        return flask.render_template('sql.html', permission=permission)
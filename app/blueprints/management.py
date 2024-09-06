import flask, datetime
from app.helpers import *
from database.schema import SCHEMA

blueprint = flask.Blueprint("management", __name__)

def input_format(tname: str):
    rtn = {}
    for field in SCHEMA[tname].fields:
        if SCHEMA[tname].fields[field].foreignKey:
            rtn[field] = ["select", [row[0] for row in sql(f"""SELECT {SCHEMA[tname].fields[field].foreignKey[1]} FROM {SCHEMA[tname].fields[field].foreignKey[0]} 
                                                           ORDER BY {SCHEMA[tname].fields[field].foreignKey[1]}""").result]]
        elif SCHEMA[tname].fields[field].options:
            rtn[field] = ["select", SCHEMA[tname].fields[field].options]
        elif SCHEMA[tname].fields[field].command:
            rtn[field] = ["select", [row[0] for row in sql(*SCHEMA[tname].fields[field].command).result]]
        elif SCHEMA[tname].fields[field].datatype is int:
            rtn[field] = ["number"]
        elif SCHEMA[tname].fields[field].datatype is bool:
            rtn[field] = ["checkbox"]
        elif SCHEMA[tname].fields[field].datatype is datetime.datetime:
            rtn[field] = ["datetime"]
    return rtn

def info(tname, tableOnly = False):
    info = sql(f"SELECT * FROM {tname} ORDER BY {SCHEMA[tname].primaryKey}",tupleToList=True)

    for i in info.result:
        i.append(html.input({"name": i[info.field.index(SCHEMA[tname].primaryKey)], "type": "submit", "value": "Edit"}))
        i.append(html.input({"name": i[info.field.index(SCHEMA[tname].primaryKey)], "type": "submit", "value": "Delete"}))
    #info.field_display.append("#Edit")
    field = info.field_name()
    field.append("")
    field.append("")
    
    table = html.table(field, info.result, {"class": "sortable"}) + html.input({"name": "add", "type": "submit", "value": "+"})

    if not tableOnly:
        return table, info.field, input_format(tname)
    else:
        return table


@blueprint.route('/management/<tname>', methods=["GET"])
@verifySession(flask.session, "EDIT{0}")
def management(tname, permission):

    table, field, input_format = info(tname)

    return flask.render_template('management.html', permission=permission, tname=tname, table=table, field=field, input_format=input_format)


@blueprint.route('/management/<tname>/<action>', methods=["POST"], endpoint = "managementPOST")
@verifySession(flask.session, "EDIT{0}")
def managementPOST(tname, action, permission):
    try:
        if action in ("update", "delete"):
            sql(f"DELETE FROM {tname} WHERE {SCHEMA[tname].primaryKey} = ?", flask.request.form.get("id"), commit=True)

        if action in ("update", "insert"):
            length = len(flask.request.form.getlist("data[]"))
            placeholders = ','.join(['?'] * length)
            sql(f"INSERT INTO {tname} VALUES ({placeholders})", *map(lambda i: None if i == 'None' else i, flask.request.form.getlist("data[]")), commit=True)
    except Exception as e:
        return flask.jsonify({"error": e})

    table = info(tname, tableOnly=True)
    
    if action == "reload":
        return flask.jsonify(table=table)
    else:
        return flask.jsonify({"table": table, "error": "Succeed."})
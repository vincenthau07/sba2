import flask, datetime
from app.helpers import *
from database.schema import SCHEMA
from config import TIME_ZONE

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

def get_fields(tname):
    return [SCHEMA[tname].fields[key].displayName if SCHEMA[tname].fields[key].displayName else key for key in SCHEMA[tname].fields]

def info(tname, tableOnly = False):
    info = sql(f"SELECT * FROM {tname} ORDER BY {SCHEMA[tname].primaryKey}",tupleToList=True)

    
    return info.result


@blueprint.route('/management/<tname>', methods=["GET"])
@verifySession(flask.session, "EDIT{0}")
def management(tname, permission):
    
    in_format = input_format(tname)
    columns = get_fields(tname)
    pk_index = list(SCHEMA[tname].fields.keys()).index(SCHEMA[tname].primaryKey)
    fields = list(SCHEMA[tname].fields.keys())

    return flask.render_template('management.html', pk_index=pk_index, fields=fields, permission=permission, tname=tname, columns=columns, input_format=in_format, tz=TIME_ZONE)

@blueprint.route('/management/<tname>', methods=["POST"], endpoint = "managementPOST2")
@verifySession(flask.session, "EDIT{0}")
def management(tname, permission):
    return flask.jsonify(data=info(tname))

@blueprint.route('/management/<tname>/<action>/', methods=["POST"], endpoint = "managementPOST3")
@blueprint.route('/management/<tname>/update/<id>', methods=["POST"], endpoint = "managementPOST")
@verifySession(flask.session, "EDIT{0}")
def managementPOST(tname, permission, action='update', id=''):
    try:
        if action in ("update", "delete"):
            sql(f"DELETE FROM {tname} WHERE {SCHEMA[tname].primaryKey} = ?", id, commit=True)
        
        if action in ("update", "insert"):
            length = len(flask.request.form.getlist("data[]"))
            placeholders = ','.join(['?'] * length)
            sql(f"INSERT INTO {tname} VALUES ({placeholders})", *map(lambda i: None if i == 'None' else i, flask.request.form.getlist("data[]")), commit=True)
    except Exception as e:
        return flask.jsonify({"error": str(e)})
    return flask.jsonify({})
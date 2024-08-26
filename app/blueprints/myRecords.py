import flask, datetime
from app.helpers import *

blueprint = flask.Blueprint("myRecords", __name__)



def info(tname, part):

    availability = part in ("approved", "appealing")
    approved = part in ("approved", "denied")

    info = sql(f"""SELECT BID, STIME, ETIME, a.{tname[0].upper()}ID, {tname[0].upper()}NAME, DESCRIPTION, NAME 
               FROM {tname+"_record"} a, {tname} b, school_unit c 
               WHERE a.{tname[0].upper()}ID = b.{tname[0].upper()}ID AND a.UNIT = c.UNIT AND
               a.AVAILABILITY = ? AND APPROVED_BY IS {'NOT' if approved else ''} NULL AND
               ETIME > ?""", availability, str(datetime.datetime.now()), tupleToList=True)
    
    if len(info.result):
        print(info.field_name())
        value = "Restore" if part == "cancelled" else "Cancel"
        for i in info.result:
            i.append(html.input({"name": i[info.field.index(SCHEMA[tname+"_record"].primaryKey)], "type": "submit", "value": value}))
        field = info.field_name()
        field.append("")
        return html.table(field, info.result, {"class": "sortable"})
    else:
        return "No record at this moment."

@blueprint.route('/records/<tname>', methods=["GET"])
@verifySession(flask.session)
def records(tname, permission):

    table = {
        part: info(tname, part) for part in ("approved", "denied", "appealing", "cancelled")
    }
    return flask.render_template('records.html', tname = tname, table=table, permission = permission)

@blueprint.route('/records/<tname>/<action>', methods=["POST"], endpoint="recordsUpdate")
@verifySession(flask.session)
def records(tname, action, permission):
    if action == "cancel":
        sql(f"UPDATE {tname+'_record'} SET AVAILABILITY = ?, APPROVED_BY = ? WHERE BID = ?",
             False, None, flask.request.form.get("BID"), commit = True)
    else:
        sql(f"UPDATE {tname+'_record'} SET AVAILABILITY = ?, APPROVED_BY = ? WHERE BID = ?",
             True, flask.session["UID"] if permission["EDIT"+tname.upper()+"_RECORD"] else None, flask.request.form.get("BID"), commit = True)
    table = {
        part: info(tname, part) for part in ("approved", "denied", "appealing", "cancelled")
    }
    return flask.jsonify({"table": table, "error": "Succeed."})
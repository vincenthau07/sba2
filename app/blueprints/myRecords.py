import flask, datetime
from app.helpers import *
from config import BOOK_TIME
blueprint = flask.Blueprint("myRecords", __name__)

def info(tname, uid, part):

    availability = part in ("approved", "pending")
    approved = part in ("approved", "denied")

    info = sql(f"""SELECT BID, STIME, ETIME, a.{tname[0].upper()}ID, {tname[0].upper()}NAME, DESCRIPTION, NAME 
               FROM {tname+"_record"} a, {tname} b, school_unit c 
               WHERE a.{tname[0].upper()}ID = b.{tname[0].upper()}ID AND a.UNIT = c.UNIT AND
               a.AVAILABILITY = ? AND APPROVED_BY IS {'NOT' if approved else ''} NULL AND
               ETIME > ? AND a.UID = ?""", availability, str(datetime.datetime.now()),uid, tupleToList=True)
    
    if len(info.result):
        #print(info.field_name())
        value = "Restore" if part == "cancelled" else "Cancel"
        for i in info.result:
            i.append(html.input({"name": i[info.field.index(SCHEMA[tname+"_record"].primaryKey)], "type": "submit", "value": value}))
        field = info.field_name()
        field.append("")
        return html.table(field, info.result, {"class": "sortable filterable"})
    else:
        return "No record at this moment."

@blueprint.route('/records/<tname>', methods=["GET"])
@verifySession(flask.session)
def records(tname, permission):

    table = {
        part: info(tname, flask.session["UID"], part) for part in ("approved", "denied", "pending", "cancelled")
    }
    return flask.render_template('records.html', tname = tname, table=table, permission = permission)

@blueprint.route('/records/<tname>/<action>', methods=["POST"], endpoint="recordsUpdate")
@verifySession(flask.session)
def records(tname, action, permission):
    try:
        if action == "cancel":
            sql(f"UPDATE {tname+'_record'} SET AVAILABILITY = ?, APPROVED_BY = ? WHERE BID = ?",
                False, None, flask.request.form.get("BID"), commit = True)
        else:
            stime,etime = sql(f"SELECT STIME, ETIME FROM {tname+'_record'} WHERE BID = ?", flask.request.form.get("BID")).result[0]
            if len(sql(f"SELECT * FROM {tname+'_record'} WHERE AVAILABILITY AND STIME < ? AND ETIME > ?", etime, stime).result) > 0:
                return flask.jsonify({"error": "Error: Selected session is occupied by others."})
            elif permission["EDIT"+tname.upper()+"_RECORD"]:
                sql(f"UPDATE {tname+'_record'} SET AVAILABILITY = ?, APPROVED_BY = ? WHERE BID = ?",
                    True, flask.session["UID"], flask.request.form.get("BID"), commit = True)
            elif strToDate(sql(f"SELECT STIME FROM {tname}_record WHERE BID = ?", flask.request.form.get("BID")).result[0][0]) - datetime.datetime.now() >= BOOK_TIME:
                sql(f"UPDATE {tname+'_record'} SET AVAILABILITY = ?, APPROVED_BY = ? WHERE BID = ?",
                    True, None, flask.request.form.get("BID"), commit = True)
            else:
                return flask.jsonify({"error": "Error: You can only book rooms after a week."})
        table = {
            part: info(tname, flask.session["UID"], part) for part in ("approved", "denied", "pending", "cancelled")
        }
    except Exception as error:
        return flask.jsonify({"error": error})
    return flask.jsonify({"table": table, "error": "Succeed."})
import flask, datetime
from app.helpers import *
from database.schema import SCHEMA
from datetime import datetime

blueprint = flask.Blueprint("approve", __name__)

def info(tname):
    info = sql(f"""SELECT BID, a.{tname[0].upper()}ID, {tname[0].upper()}NAME, UID, STIME, ETIME, NAME, DESCRIPTION 
               FROM {tname}_record a, school_unit b, {tname} d
               WHERE a.{tname[0].upper()}ID = d.{tname[0].upper()}ID AND a.UNIT = b.UNIT 
               AND a.AVAILABILITY AND APPROVED_BY IS NULL AND ETIME>? ORDER BY {SCHEMA[tname+"_record"].primaryKey}""",str(datetime.now()),tupleToList=True)
    if len(info.result) == 0:
        return "No record is pending at this moment."
    for i in info.result:
        i.append(html.input({"name": i[info.field.index(SCHEMA[tname+"_record"].primaryKey)], "type": "submit", "value": "Approve"}))
        i.append(html.input({"name": i[info.field.index(SCHEMA[tname+"_record"].primaryKey)], "type": "submit", "value": "Deny"}))
    #info.field_display.append("#Edit")
    field = info.field_name()
    
    field.append("")
    field.append("")
    
    table = html.table(field, info.result, {"class": "sortable filterable"})

    return table

@blueprint.route('/approve/<tname>', methods=["GET"])
@verifySession(flask.session, "EDIT{0}_RECORD")
def approve(tname, permission):

    table = info(tname)

    return flask.render_template('approve.html', permission=permission, tname=tname, table=table)

@blueprint.route('/approve/<tname>/<action>', methods=["POST"], endpoint = "approvePOST")
@verifySession(flask.session, "EDIT{0}_RECORD")
def approvePOST(tname, action, permission):
    try:
        if action == "approve":
            sql(f"UPDATE {tname}_record SET APPROVED_BY = ? WHERE BID = ?", flask.session["UID"], flask.request.form.get("id"), commit=True)
        else:
            sql(f"UPDATE {tname}_record SET AVAILABILITY = 0, APPROVED_BY = ? WHERE BID = ?", flask.session["UID"], flask.request.form.get("id"), commit=True)
    except Exception as e:
        return flask.jsonify({"error": e})
    table = info(tname)
    
    return flask.jsonify({"table": table, "error": "Succeed."})
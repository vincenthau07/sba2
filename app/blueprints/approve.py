import flask
import datetime
from app.helpers import *
from database.schema import SCHEMA
from datetime import datetime
from config import TIME_ZONE

blueprint = flask.Blueprint("approve", __name__)

def retrieve_pending_records(tname):
    info = sql(f"""SELECT BID, a.{tname[0].upper()}ID, {tname[0].upper()}NAME, UID, STIME, ETIME, NAME, DESCRIPTION 
               FROM {tname}_record a, school_unit b, {tname} d
               WHERE a.{tname[0].upper()}ID = d.{tname[0].upper()}ID AND a.UNIT = b.UNIT 
               AND a.AVAILABILITY AND APPROVED_BY IS NULL AND ETIME>? ORDER BY {SCHEMA[tname+"_record"].primaryKey}""",str(getDatetimeNow()),tupleToList=True)

    #append approve and cancel button
    for i in info.result:
        i.append(html.input(
            {"class": "btn btn-outline-primary", 
             "name": i[info.field.index(SCHEMA[tname+"_record"].primaryKey)], 
             "type": "submit", 
             "value": "Approve"}
            )
        )
        i.append(html.input(
            {"class": "btn btn-outline-danger", 
             "name": i[info.field.index(SCHEMA[tname+"_record"].primaryKey)], 
             "type": "submit", 
             "value": "Deny"}
            )
        )
    return info.result

@blueprint.route('/approve/<tname>', methods = ["GET"])
@verifySession(flask.session, "EDIT{0}_RECORD")
def approve(tname, permission):
    return flask.render_template('approve.html', 
                                 permission = permission, 
                                 tname = tname, 
                                 tz = TIME_ZONE)

@blueprint.route('/approve/<tname>/update', methods = ["GET"])
@verifySession(flask.session, "EDIT{0}_RECORD")
def approveUpdate(tname, permission):
    return flask.jsonify(data = retrieve_pending_records(tname))

@blueprint.route('/approve/<tname>', methods = ["POST"])
@verifySession(flask.session, "EDIT{0}_RECORD")
def approvePOST(tname, permission):
    try:
        if flask.request.form["type"] == "approve":
            sql(f"UPDATE {tname}_record SET APPROVED_BY = ? WHERE BID = ?", 
                flask.session["UID"], 
                flask.request.form.get("id"), 
                commit = True)
        else:
            sql(f"UPDATE {tname}_record SET AVAILABILITY = 0, APPROVED_BY = ? WHERE BID = ?", 
                flask.session["UID"], 
                flask.request.form.get("id"), 
                commit = True)
    except Exception as error:
        return flask.jsonify({"error": str(error)})

    
    return flask.jsonify({})
import flask, datetime
from app.helpers import *
from database.schema import SCHEMA
from datetime import datetime
from config import TIME_ZONE

blueprint = flask.Blueprint("approve", __name__)

def info(tname):
    info = sql(f"""SELECT BID, a.{tname[0].upper()}ID, {tname[0].upper()}NAME, UID, STIME, ETIME, NAME, DESCRIPTION 
               FROM {tname}_record a, school_unit b, {tname} d
               WHERE a.{tname[0].upper()}ID = d.{tname[0].upper()}ID AND a.UNIT = b.UNIT 
               AND a.AVAILABILITY AND APPROVED_BY IS NULL AND ETIME>? ORDER BY {SCHEMA[tname+"_record"].primaryKey}""",str(datetime.now(TIME_ZONE).replace(tzinfo=None)),tupleToList=True)

    for i in info.result:
        i.append(html.input({"class": "btn btn-outline-primary", "name": i[info.field.index(SCHEMA[tname+"_record"].primaryKey)], "type": "submit", "value": "Approve"}))
        i.append(html.input({"class": "btn btn-outline-danger", "name": i[info.field.index(SCHEMA[tname+"_record"].primaryKey)], "type": "submit", "value": "Deny"}))
    return info.result

@blueprint.route('/approve/<tname>', methods=["GET"])
@verifySession(flask.session, "EDIT{0}_RECORD")
def approve(tname, permission):
    return flask.render_template('approve.html', permission=permission, tname=tname)

@blueprint.route('/approve/<tname>', methods=["POST"], endpoint = "approvePOST2")
@verifySession(flask.session, "EDIT{0}_RECORD")
def approve(tname, permission):
    return flask.jsonify(data=info(tname))

@blueprint.route('/approve/<tname>/<action>', methods=["POST"], endpoint = "approvePOST")
@verifySession(flask.session, "EDIT{0}_RECORD")
def approvePOST(tname, action, permission):
    try:
        if action == "approve":
            sql(f"UPDATE {tname}_record SET APPROVED_BY = ? WHERE BID = ?", flask.session["UID"], flask.request.form.get("id"), commit=True)
        else:
            sql(f"UPDATE {tname}_record SET AVAILABILITY = 0, APPROVED_BY = ? WHERE BID = ?", flask.session["UID"], flask.request.form.get("id"), commit=True)
    except Exception as error:
        return flask.jsonify({"error": str(error)})

    
    return flask.jsonify({})
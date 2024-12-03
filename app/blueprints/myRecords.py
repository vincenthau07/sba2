import flask
import error_message as error_msg
from app.helpers import *
from config import BOOK_TIME, TIME_ZONE
blueprint = flask.Blueprint("myRecords", __name__)

def info(tname, uid, part):

    availability = part in ("approved", "pending")
    approved = part in ("approved", "denied")

    info = sql(f"""SELECT BID, STIME, ETIME, a.{tname[0].upper()}ID, {tname[0].upper()}NAME, DESCRIPTION, NAME 
               FROM {tname+"_record"} a, {tname} b, school_unit c 
               WHERE a.{tname[0].upper()}ID = b.{tname[0].upper()}ID AND a.UNIT = c.UNIT AND
               a.AVAILABILITY = ? AND APPROVED_BY IS {'NOT' if approved else ''} NULL AND
               ETIME > ? AND a.UID = ?""", availability, str(getDatetimeNow()),uid, tupleToList=True)
    
    value = "Restore" if part == "cancelled" else "Cancel"
    color = "btn btn-outline-primary" if part == "cancelled" else "btn btn-outline-danger"
    for i in info.result:
        i.append(html.input({"class": color,
                             "name": i[info.field.index(SCHEMA[tname+"_record"].primaryKey)], 
                             "type": "submit", 
                             "value": value})
                 )

    return info.result


@blueprint.route('/records/<tname>', methods = ["GET"])
def redirect(tname):
    return flask.redirect(f'/records/{tname}/approved')

@blueprint.route('/records/<tname>/<path>', methods = ["GET"])
@verifySession(flask.session)
def records(tname,  permission, path):

    return flask.render_template('records.html', 
                                 tname = tname, 
                                 permission = permission, 
                                 tz=TIME_ZONE)

@blueprint.route('/records/<tname>/<path>/update', methods=["GET"])
@verifySession(flask.session)
def recordsPOST(tname,  permission, path):
    result = info(tname, flask.session["UID"], path)
    return flask.jsonify(data = result)

@blueprint.route('/records/<tname>/<path>', methods = ["POST"])
@verifySession(flask.session)
def recordsPOST2(tname, permission, path="approved"):
    try:
        if path != "cancelled":
            sql(f"UPDATE {tname+'_record'} SET AVAILABILITY = ?, APPROVED_BY = ? WHERE BID = ? AND UID = ?",
                False, None, 
                flask.request.form['id'], 
                flask.session['UID'], 
                commit = True)
        else:
            stime, etime = sql(f"SELECT STIME, ETIME FROM {tname+'_record'} WHERE BID = ?", 
                                    flask.request.form['id']
                               ).result[0]
            if len(sql(f"SELECT * FROM {tname+'_record'} WHERE AVAILABILITY AND STIME < ? AND ETIME > ?",
                       etime, stime).result
                   ) > 0:
                return flask.jsonify({"error": error_msg.booking.occupied_time_session})
            
            elif permission["EDIT"+tname.upper()+"_RECORD"]:
                sql(f"UPDATE {tname+'_record'} SET AVAILABILITY = ?, APPROVED_BY = ? WHERE BID = ? AND UID = ?",
                    True, flask.session["UID"], 
                    flask.request.form['id'], 
                    flask.session['UID'],
                    commit = True)
                
            elif strToDate(sql(f"SELECT STIME FROM {tname}_record WHERE BID = ?", 
                               flask.request.form['id']).result[0][0]
                           ) - getDatetimeNow() >= BOOK_TIME:
                sql(f"UPDATE {tname+'_record'} SET AVAILABILITY = ?, APPROVED_BY = ? WHERE BID = ? AND UID = ?",
                    True, None, 
                    flask.request.form['id'], 
                    flask.session['UID'],
                    commit = True)
                
            else:
                return flask.jsonify({"error": "You can only book rooms after a week."})
            
    except Exception as error:
        return flask.jsonify({"error": str(error)})
    
    return flask.jsonify({})
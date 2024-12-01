import flask
from app.helpers import *
import datetime, random
from config import BOOK_TIME, TIME_ZONE
import error_message as error_msg

blueprint = flask.Blueprint('booking', __name__)

WEEKDAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

def checkAvailability(func):
    def decorator(*args,**kwargs):
        try:
            if not get_by_primary_key(kwargs['tname'], kwargs['id'], ('AVAILABILITY')):
                return flask.redirect(f"/booking/{kwargs['tname']}")
        except:
            flask.abort(403)    #403 Forbidden
        return func(*args, **kwargs)
    decorator.__name__ = func.__name__
    return decorator

def getInfo(table, **kwargs):
    field = [i for i in SCHEMA[table].fields 
             if i != "AVAILABILITY"]
    rtn = sql(f"SELECT {', '.join(field)} FROM {table} WHERE AVAILABILITY ORDER BY {SCHEMA[table].primaryKey}", **kwargs)
    return rtn

def getEvents(table, id: str, 
              date: datetime.date = None, 
              stime: None = None, 
              etime: None = None, **kwargs) -> sql:
    field = [i for i in SCHEMA[table+"_record"].fields 
             if i not in ("AVAILABILITY", "UNIT")]
    if date is not None:
        stime = datetime.datetime.combine(date, datetime.datetime.min.time())
        etime = stime + datetime.timedelta(days = 1)
    result = sql(f"""SELECT {', '.join(field)}, NAME FROM {table+'_record'} r, school_unit s
                   WHERE r.UNIT = s.UNIT AND AVAILABILITY AND {table[0].upper()+"ID"}=? 
                   AND STIME < ? AND ETIME > ? ORDER BY STIME ASC""", 
                   id, str(etime), str(stime), 
                   tupleToList = True,
                   **kwargs)

    rtn = []

    for row in result.result:
        row[result.field.index("STIME")] = max(strToDate(row[result.field.index("STIME")]), 
                                               stime)
        row[result.field.index("ETIME")] = min(strToDate(row[result.field.index("ETIME")]), 
                                               etime)
        if row[result.field.index("APPROVED_BY")] is None:
            background_color = f"rgb(192,192,192)"
        else:
            random.seed(row[result.field.index("NAME")])
            background_color = f"hsl({random.randint(0,359)}, 25%, 46%)"
        rtn.append({
            "weekday": row[result.field.index("STIME")].weekday(),
            "start": str(row[result.field.index("STIME")])[11:16],
            "end": str(row[result.field.index("ETIME")])[11:16],
            "background_color": background_color,
            "title": row[result.field.index("NAME")],
            "content": f"""
                <h2>
                    Booked by: {row[result.field.index("UID")]} - {get_by_primary_key("user", row[result.field.index("UID")], "UNAME")}
                </h2>
                 <p> Description: {"(NOT APPROVED)" if row[result.field.index("APPROVED_BY")] is None else ""}</p>
                 <p>
                     {row[result.field.index("DESCRIPTION")]}
                 </p>"""
        })
    return rtn

def fieldHTML(dates: list):
    
    rtn = ""
    for i in range(7):
        rtn += html.div(str(dates[i]) 
                        + html.linebreak() 
                        + WEEKDAYS[i],
                        {"class": "field"})
    return rtn

def addRecord(table, stime, etime, 
              uid, primary_key, unit,
              description, approved = False):
    sql(f'''INSERT INTO {table+"_record"}
            (STIME,ETIME,UID,{SCHEMA[table].primaryKey},UNIT,DESCRIPTION,AVAILABILITY,APPROVED_BY)
            VALUES (?,?,?,?,?,?,1,?)''',
            str(stime), str(etime),
            uid, primary_key, unit,
            description, uid if approved else None,
            commit = True)

#flask
@blueprint.route('/booking/<tname>')
@verifySession(flask.session)
def booking(tname, permission):
    rf_info = getInfo(tname, tupleToList = True)
    if 'FLOOR' in SCHEMA[tname].fields:
        num_to_floor(rf_info.result, rf_info.field.index('FLOOR'))
    text_to_link(rf_info.result, f"/booking/{tname}/{{}}", rf_info.field.index(SCHEMA[tname].primaryKey))

    return flask.render_template('booking.html', 
                                 tname = tname, 
                                 columns = rf_info.field_name(), 
                                 data = rf_info.result, 
                                 permission = permission, 
                                 tz = TIME_ZONE)

@blueprint.route('/booking/<tname>/<id>', methods=["GET"])
@checkAvailability
@verifySession(flask.session)
def booking2(tname, id, permission):
    name = get_by_primary_key(tname, id, tname[0].upper()+"NAME")

    
    minweek = dateToWeekNumber(getDatetimeNow().date())

    #exact dates of week
    dates = weekNumToDate(minweek)

    #events in this weekD
    data = []
    for i in range(len(dates)):
        data.extend(getEvents(tname, id, dates[i]))
            
    categories = [row[0] for row in sql("SELECT CATEGORY FROM school_category").result]
    units = [row for row in sql("SELECT UNIT, NAME, CATEGORY FROM school_unit").result]

    return flask.render_template('booking2.html', 
                                 tname = tname, 
                                 id = id,
                                 name = name, 
                                 permission = permission,
                                 col = list(map(str,dates)), 
                                 minweek = minweek, 
                                 data = data, 
                                 categories = categories, 
                                 units = units, 
                                 tz = TIME_ZONE)

@blueprint.route('/booking/<tname>/<id>', methods = ["POST"])
@verifySession(flask.session)
@checkAvailability
def bksubmitform(tname, id, permission):
    try:
        if (len(flask.request.form.get("stime")) == 0  
                or len(flask.request.form.get("etime")) == 0 
                or len(flask.request.form.get("description")) == 0 
                or flask.request.form.get("unit") is None):
            return flask.jsonify({"error": error_msg.booking.empty_input})
        else:
            stime = strToDate(flask.request.form.get("stime"))
            etime = strToDate(flask.request.form.get("etime"))
            if etime <= stime:
                return flask.jsonify({"error": error_msg.booking.end_time_before_start_time})
            elif len(getEvents(tname, id, 
                               stime = stime+datetime.timedelta(seconds = 1), 
                               etime = etime-datetime.timedelta(seconds = 1))
                    ) > 0:
                return flask.jsonify({"error": error_msg.booking.occupied_time_session})
            
            elif permission[f"EDIT{tname.upper()}_RECORD"]:
                if stime < getDatetimeNow():
                    return flask.jsonify({"error": error_msg.booking.start_time_in_the_past})
                else:
                    try:
                        addRecord(tname, 
                                  stime, etime, 
                                  flask.session.get('UID'), id, 
                                  flask.request.form.get("unit"), 
                                  flask.request.form.get("description"), True)
                        return flask.jsonify({})
                    except Exception as error:
                        return flask.jsonify({"error": str(error)})
            else:
                if stime < getDatetimeNow() + BOOK_TIME:
                    return flask.jsonify({"error": error_msg.booking.book_after_a_period_of_time})
                else:
                    try:
                        addRecord(tname, stime, etime, 
                                  flask.session.get('UID'), id,
                                  flask.request.form.get("unit"), 
                                  flask.request.form.get("description"))
                        return flask.jsonify({})
                    except Exception as error:
                        return flask.jsonify({"error": str(error)})
    except Exception as error:
        return flask.jsonify({"error": str(error)})


@blueprint.route('/booking/<tname>/<id>/update', methods = ["POST"])
@verifySession(flask.session)
@checkAvailability
def bkupdate(tname, id, permission):

    dates = weekNumToDate(flask.request.form.get('week'))
    week = flask.request.form.get('week')
    if 'next' in flask.request.form:
        week = dateToWeekNumber(dates[0] + datetime.timedelta(days = 7))
        dates = weekNumToDate(week)
    elif ('previous' in flask.request.form and
            dates[0] > getDatetimeNow().date()):
        week = dateToWeekNumber(dates[0] - datetime.timedelta(days = 7))
        dates = weekNumToDate(week)
        
    data = []
    for date in dates:
        data.extend(getEvents(tname, id, date))

    return flask.jsonify({"col": list(map(str, dates)),
                          "data": data, 
                          'week': week})
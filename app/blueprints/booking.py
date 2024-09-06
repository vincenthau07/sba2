import flask
from app.helpers import *
import datetime, random
from config import BOOK_TIME
blueprint = flask.Blueprint('booking', __name__)

#convert between html weekpicker data & python datetime

def getInfo(table, floorNumToFloor=True, hyperLink = True, **kwargs):
    field = [i for i in SCHEMA[table].fields if i != "AVAILABILITY"]
    rtn = sql(f"SELECT {', '.join(field)} FROM {table} WHERE AVAILABILITY ORDER BY {SCHEMA[table].primaryKey}", **kwargs)
    if hyperLink:
        for row in rtn.result:
            row[field.index(SCHEMA[table].primaryKey)] = html.hyperlink(row[0], f"/booking/{table}/{row[0]}")
    if floorNumToFloor and "floor" in field:
        for row in rtn.result:
            f = field.index("floor")
            row[f] = f"{row[f]}/F" if row[f] > 0 else f"B{-row[f]}/F" if row[f] < 0 else "G/F"
    return rtn

def getEvents(table, id: str, date: datetime.date=None, stime: None=None, etime: None=None, **kwargs) -> sql:
    field = [i for i in SCHEMA[table+"_record"].fields if i not in ("AVAILABILITY", "UNIT")]
    if date is not None:
        stime = datetime.datetime.combine(date, datetime.datetime.min.time())
        etime = stime + datetime.timedelta(days=1)
    rtn = sql(f"""SELECT {', '.join(field)}, NAME FROM {table+'_record'} r, school_unit s
                   WHERE r.UNIT = s.UNIT AND AVAILABILITY AND {table[0].upper()+"ID"}=? 
                   AND STIME < ? AND ETIME > ?""", id, str(etime), str(stime), tupleToList=True,**kwargs)
    for row in rtn.result:
        row[rtn.field.index("STIME")] = max(strToDate(row[rtn.field.index("STIME")]), stime)
        row[rtn.field.index("ETIME")] = min(strToDate(row[rtn.field.index("ETIME")]), etime)
    return rtn

def eventHTML(result: sql, id) -> str:
    rtn = ""
    for record in result.result:
        top = (record[result.field.index("STIME")] - datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())).total_seconds() % 86400 * 80 / 3600 + 80
        height = (record[result.field.index("ETIME")] - record[result.field.index("STIME")]).total_seconds() * 80 / 3600

        
        if record[result.field.index("APPROVED_BY")] is None:
            background_color = f"rgb(192,192,192)"
        else:
            random.seed(record[result.field.index("NAME")])
            background_color = f"hsl({random.randint(0,359)}, 65%, 50%)"
        rtn += f'''
        <div class = "event-box" style = "top: {top}px; height: {height}px">
            <div class = "mask"></div>
            <div class = "event" style = "height: {height}px; background-color: {background_color}">
                <h3>{str(record[result.field.index("STIME")])[11:16]} - {str(record[result.field.index("ETIME")])[11:16]}
                <h2>{record[result.field.index("NAME")]}</h2>
            </div>
            <div class = "close-button"></div>
            <div class = "description">
                <h1>Booked by: {record[result.field.index("UID")]} - {get_by_primary_key("user", record[result.field.index("UID")], "UNAME")}</h1>
                
                <p> Description: {"(NOT APPROVED)" if record[result.field.index("APPROVED_BY")] is None else ""}</p>
                <p>
                    {record[result.field.index("DESCRIPTION")]}
                </p>
            </div>
        </div>'''
    return rtn

def fieldHTML(dates: list):
    weekdays = ["MON","TUE","WED","THU","FRI","SAT","SUN"]
    rtn = ""
    for i in range(7):
        rtn += html.div(str(dates[i]) + html.linebreak() + weekdays[i], {"class": "field"})
    return rtn

def addRecord(table,stime,etime,uid,primary_key,unit,description,approved=False):
    sql(f'''INSERT INTO {table+"_record"}
               (STIME,ETIME,UID,{SCHEMA[table].primaryKey},UNIT,DESCRIPTION,AVAILABILITY,APPROVED_BY)
               VALUES (?,?,?,?,?,?,1,?)''',
               str(stime),str(etime),uid,primary_key,unit,description,uid if approved else None,commit=True)

#flask
@blueprint.route('/booking/<tname>')
@verifySession(flask.session)
def booking(tname, permission):
    roomInfo = getInfo(tname, tupleToList=True)
    table = html.table(roomInfo.field_name(),roomInfo.result,{"class": "sortable"})

    return flask.render_template('booking.html', tname=tname, table=table, permission = permission)

@blueprint.route('/booking/<tname>/<id>', methods=["GET"], endpoint = "booking2")
@verifySession(flask.session)
def booking2(tname, id, permission):

    name = get_by_primary_key(tname, id, tname[0].upper()+"NAME")

    #minweek value
    minweek = dateToWeekNumber(datetime.date.today())

    #exact dates of week
    dates = weekNumToDate(minweek)
    field_bar = html.div(fieldHTML(dates), {"class": "field-bar"})

    #events in this week
    eventsql = []
    for date in dates:
        eventsql.append(getEvents(tname, id, date))
    events = []
    for i in range(len(eventsql)):
        events.append(eventHTML(eventsql[i],i))

    categories = [row[0] for row in sql("SELECT CATEGORY FROM school_category").result]
    units = [row for row in sql("SELECT UNIT, NAME, CATEGORY FROM school_unit").result]

    return flask.render_template('booking2.html', tname=tname, id = id,
                                  name = name, permission = permission,
                                  field_bar=field_bar, minweek = minweek, 
                                  events=events, categories=categories, units=units)

@blueprint.route('/booking/<tname>/<id>', methods=["POST"], endpoint="bksubmitform")
@verifySession(flask.session)
def bksubmitform(tname, id, permission):    
    if len(flask.request.form.get("stime")) == 0  or len(flask.request.form.get("etime")) == 0 or len(flask.request.form.get("description")) == 0 or flask.request.form.get("unit") is None:
        return flask.jsonify({"message": "Error: Some information is missing."})
    else:
        stime = strToDate(flask.request.form.get("stime"))
        etime = strToDate(flask.request.form.get("etime"))
        if etime<=stime:
            return flask.jsonify({"message": "Ending time must be after starting time."})
        
        elif len(getEvents(tname, id,stime = stime+datetime.timedelta(seconds=1), etime = etime-datetime.timedelta(seconds=1)).result)>0:
            return flask.jsonify({"message": "Error: Selected session is occupied by others."})
        elif permission[f"EDIT{tname.upper()}_RECORD"]:
            if stime < datetime.datetime.today():
                return flask.jsonify({"message": "Error: You cannot book rooms in the past."})
            else:
                try:
                    addRecord(tname,stime,etime,flask.session.get('UID'),id,flask.request.form.get("unit"),flask.request.form.get("description"), True)
                    return flask.jsonify({"message": "Succeed."})
                except Exception as error:
                    return flask.jsonify({"message": f"Error: {error}"})
        else:
            if stime < datetime.datetime.today() + BOOK_TIME:
                return flask.jsonify({"message": "Error: You can only book rooms after a week."})
            else:
                try:
                    addRecord(tname,stime,etime,flask.session.get('UID'),id,flask.request.form.get("unit"),flask.request.form.get("description"))
                    return flask.jsonify({"message": "Succeed."})
                except Exception as error:
                    return flask.jsonify({"message": f"Error: {error}"})


@blueprint.route('/booking/<tname>/<id>/update', methods=["POST"], endpoint="bkupdate")
@verifySession(flask.session)
def bkupdate(tname, id, permission):
    dates = weekNumToDate(flask.request.form.get('week'))
    week = flask.request.form.get('week')
    if 'previous' in flask.request.form:
        if dates[0] > datetime.date.today():
            week = dateToWeekNumber(dates[0] - datetime.timedelta(days=7))
            dates = weekNumToDate(week)
    elif 'next' in flask.request.form:
        week = dateToWeekNumber(dates[0] + datetime.timedelta(days=7))
        dates = weekNumToDate(week)
        
    field = fieldHTML(dates)
    eventsql = []
    for date in dates:
        eventsql.append(getEvents(tname,id,date))
    events = []
    for i in range(len(eventsql)):
        events.append(eventHTML(eventsql[i],i))
    return flask.jsonify({"field": field, "events": events, "week": week})
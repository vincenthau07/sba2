import flask
import modules.sql as sql
import modules.html as html
import modules.datetime as dt
import datetime
import colorsys
import random

booking_bp = flask.Blueprint('booking', __name__)

#convert between html weekpicker data & python datetime
def dateToWeekNumber(date: datetime.datetime) -> str:
    date += datetime.timedelta(days=4-datetime.date.isoweekday(date))
    date2 = datetime.date(date.year,1,1)
    date2 += datetime.timedelta(days=(11-datetime.date.isoweekday(date2))%7-3)
    return f"{date.year}-W{(date-date2).days//7+1:02d}"

def weekNumToDate(week) -> list:
    year = int(week[:4])
    week = int(week[-2:])
    date = datetime.date(year,1,1)
    date += datetime.timedelta(days=(11-datetime.date.isoweekday(date))%7-3)
    date += datetime.timedelta(days=(week-1)*7)
    d = datetime.timedelta(days=1)
    rtn = []
    for i in range(7):
        rtn.append(date)
        date += d
    return rtn

def getRoomInfo(floorNumToFloor=True, RIDHyperLink = True, **kwargs):
    rtn = sql.sql(f"SELECT RID, RNAME, FLOOR, AREA, CAPACITY FROM room WHERE AVAILABILITY ORDER BY RID", **kwargs)
    if RIDHyperLink:
        for row in rtn.result:
            row[0] = html.hyperlink(row[0], f"/booking/room/{row[0]}")
    if floorNumToFloor:
        for row in rtn.result:
            row[2] = f"{row[2]}/F" if row[2] != 0 else f"G/F"
    return rtn

def getFacitlityInfo(FIDHyperLink= True, **kwargs):
    rtn = sql.sql(f"SELECT FID, FNAME FROM facility WHERE AVAILABILITY ORDER BY FID", **kwargs)
    if FIDHyperLink:
        for row in rtn.result:
            row[0] = html.hyperlink(row[0], f"/booking/facility/{row[0]}")
    return rtn

def getEventsOfRoom(rid: str, date: datetime.date=None, stime: None=None, etime: None=None, **kwargs) -> sql.sql:

    if date is not None:
        stime = datetime.datetime.combine(date, datetime.datetime.min.time())
        etime = stime + datetime.timedelta(days=1)
    rtn = sql.sql("""SELECT UID, STIME, ETIME, NAME, DESCRIPTION, APPROVED_BY FROM roomrecord r, schoolunit s
                   WHERE r.UNIT = s.UNIT AND AVAILABILITY AND RID=? 
                   AND STIME < ? AND ETIME > ?""", rid, str(etime), str(stime), tupleToList=True,**kwargs)
    for row in rtn.result:
        row[1] = max(dt.strToDate(row[1]), stime)
        row[2] = min(dt.strToDate(row[2]), etime)
    return rtn

def getEventsOfFacility(rid: str, date: datetime.date=None, stime: None=None, etime: None=None, **kwargs) -> sql.sql:

    if date is not None:
        stime = datetime.datetime.combine(date, datetime.datetime.min.time())
        etime = stime + datetime.timedelta(days=1)
    rtn = sql.sql("""SELECT UID, STIME, ETIME, NAME, DESCRIPTION, APPROVED_BY FROM facilityrecord f, schoolunit s
                   WHERE f.UNIT = s.UNIT AND AVAILABILITY AND FID=? 
                   AND STIME < ? AND ETIME > ?""", rid, str(etime), str(stime), tupleToList=True,**kwargs)
    for row in rtn.result:
        row[1] = max(dt.strToDate(row[1]), stime)
        row[2] = min(dt.strToDate(row[2]), etime)
    return rtn

def eventHTML(result: sql.sql, id) -> str:
    rtn = ""
    for record in result.result:
        top = (record[1] - datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())).total_seconds() % 86400 * 80 / 3600 + 80
        height = (record[2] - record[1]).total_seconds() * 80 / 3600

        
        if record[5] is None:
            background_color = f"rgb(192,192,192)"
        else:
            random.seed(record[3])
            background_color = f"hsl({random.randint(0,359)}, 65%, 50%)"
        rtn += f'''
        <div class = "event-box" style = "top: {top}px; height: {height}px">
            <div class = "mask"></div>
            <div class = "event" style = "height: {height}px; background-color: {background_color}">
                <h3>{str(record[1])[11:16]} - {str(record[2])[11:16]}
                <h2>{record[3]}</h2>
            </div>
            <div class = "close-button"></div>
            <div class = "description">
                <h1>Booked by: {record[0]} - {sql.commands.userName(record[0])}</h1>
                
                <p> Description: {"(NOT APPROVED)" if record[5] is None else ""}</p>
                <p>
                    {record[4]}
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

def getAllCategoriesOfSkuUnit():
    rtn = []
    for i in sql.sql("SELECT DISTINCT CATEGORY FROM schoolunit").result:
        rtn.append(i[0])
    return rtn

def getSkuUnit():
    return sql.sql("SELECT * FROM schoolunit",tupleToList=True).result

def addRoomRecord(stime,etime,uid,rid,unit,description,approved=False):
    sql.sql('''INSERT INTO roomrecord
               (STIME,ETIME,UID,RID,UNIT,DESCRIPTION,AVAILABILITY,APPROVED_BY)
               VALUES (?,?,?,?,?,?,1,?)''',
               str(stime),str(etime),uid,rid,unit,description,uid if approved else None,commit=True)
def addFacilityRecord(stime,etime,uid,fid,unit,description,approved=False):
    sql.sql('''INSERT INTO facilityrecord
               (STIME,ETIME,UID,FID,UNIT,DESCRIPTION,AVAILABILITY,APPROVED_BY)
               VALUES (?,?,?,?,?,?,1,?)''',
               str(stime),str(etime),uid,fid,unit,description,uid if approved else None,commit=True)

#flask
@booking_bp.route('/booking/facility')
def facilitybooking():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))

    roomInfo = getFacitlityInfo(tupleToList=True)
    table = html.table(roomInfo.field_display,roomInfo.result,{"class": "sortable"})

    return flask.render_template('facilityBooking.html', table=table, permission = permission)


@booking_bp.route('/booking/room')
def roombooking():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))

    roomInfo = getRoomInfo(tupleToList=True)
    table = html.table(roomInfo.field_display,roomInfo.result,{"class": "sortable"})

    return flask.render_template('roomBooking.html', table=table, permission = permission)

@booking_bp.route('/booking/room/<rid>', methods=["GET"])
def roombooking2(rid):
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))

    rname = sql.commands.roomName(rid)

    #minweek value
    minweek = dateToWeekNumber(datetime.date.today())

    #exact dates of week
    dates = weekNumToDate(minweek)
    field_bar = html.div(fieldHTML(dates), {"class": "field-bar"})

    #events in this week
    eventsql = []
    for date in dates:
        eventsql.append(getEventsOfRoom(rid,date))
    events = []
    for i in range(len(eventsql)):
        events.append(eventHTML(eventsql[i],i))

    categories = getAllCategoriesOfSkuUnit()
    units = getSkuUnit()

    return flask.render_template('roomBooking2.html', rid = rid,
                                  rname = rname, permission = permission,
                                  field_bar=field_bar, minweek = minweek, 
                                  events=events, categories=categories, units=units)

@booking_bp.route('/booking/room/<rid>', methods=["POST"])
def rmbksubmitform(rid):
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    
    if len(flask.request.form.get("stime")) == 0  or len(flask.request.form.get("etime")) == 0 or len(flask.request.form.get("description")) == 0 or flask.request.form.get("unit") is None:
        return flask.jsonify({"message": "Error: Some information is missing."})
    else:
        stime = dt.strToDate(flask.request.form.get("stime"))
        etime = dt.strToDate(flask.request.form.get("etime"))
        permission = sql.commands.rolePermissions(flask.session.get('UID'))
        if etime<=stime:
            return flask.jsonify({"message": "Ending time must be after starting time."})
        
        elif len(getEventsOfRoom(rid,stime = stime+datetime.timedelta(seconds=1), etime = etime-datetime.timedelta(seconds=1)).result)>0:
            return flask.jsonify({"message": "Error: Selected session is occupied by others."})
        elif permission["EDITROOMRECORD"]:
            if stime < datetime.datetime.today():
                return flask.jsonify({"message": "Error: You cannot book rooms in the past."})
            else:
                try:
                    addRoomRecord(stime,etime,flask.session.get('UID'),rid, flask.request.form.get("unit"),flask.request.form.get("description"), True)
                    return flask.jsonify({"message": "Succeed."})
                except Exception as error:
                    return flask.jsonify({"message": f"Error: {error}"})
        else:
            if stime < datetime.datetime.today() + datetime.timedelta(days=7):
                return flask.jsonify({"message": "Error: You can only book rooms after a week."})
            else:
                try:
                    addRoomRecord(stime,etime,flask.session.get('UID'),rid, flask.request.form.get("unit"),flask.request.form.get("description"))
                    return flask.jsonify({"message": "Succeed."})
                except Exception as error:
                    return flask.jsonify({"message": f"Error: {error}"})


@booking_bp.route('/booking/room/<rid>/update', methods=["POST"])
def rmbkupdate(rid):
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
        eventsql.append(getEventsOfRoom(rid,date))
    events = []
    for i in range(len(eventsql)):
        events.append(eventHTML(eventsql[i],i))
    return flask.jsonify({"field": field, "events": events, "week": week})

@booking_bp.route('/booking/facility/<fid>', methods=["GET"])
def facilitybooking2(fid):
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))

    fname = sql.commands.facilityName(fid)

    #minweek value
    minweek = dateToWeekNumber(datetime.date.today())

    #exact dates of week
    dates = weekNumToDate(minweek)
    field_bar = html.div(fieldHTML(dates), {"class": "field-bar"})

    #events in this week
    eventsql = []
    for date in dates:
        eventsql.append(getEventsOfFacility(fid,date))
    events = []
    for i in range(len(eventsql)):
        events.append(eventHTML(eventsql[i],i))

    categories = getAllCategoriesOfSkuUnit()
    units = getSkuUnit()

    return flask.render_template('facilityBooking2.html', fid = fid,
                                  fname = fname, permission = permission,
                                  field_bar=field_bar, minweek = minweek, 
                                  events=events, categories=categories, units=units)

@booking_bp.route('/booking/facility/<fid>/update', methods=["POST"])
def fcbkupdate(fid):
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
        eventsql.append(getEventsOfFacility(fid,date))
    events = []
    for i in range(len(eventsql)):
        events.append(eventHTML(eventsql[i],i))
    return flask.jsonify({"field": field, "events": events, "week": week})

@booking_bp.route('/booking/facility/<fid>', methods=["POST"])
def fcbksubmitform(fid):
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    
    if len(flask.request.form.get("stime")) == 0  or len(flask.request.form.get("etime")) == 0 or len(flask.request.form.get("description")) == 0 or flask.request.form.get("unit") is None:
        return flask.jsonify({"message": "Error: Some information is missing."})
    else:
        stime = dt.strToDate(flask.request.form.get("stime"))
        etime = dt.strToDate(flask.request.form.get("etime"))
        permission = sql.commands.rolePermissions(flask.session.get('UID'))
        if etime<=stime:
            return flask.jsonify({"message": "Ending time must be after starting time."})
        
        elif len(getEventsOfFacility(fid,stime = stime+datetime.timedelta(seconds=1), etime = etime-datetime.timedelta(seconds=1)).result)>0:
            return flask.jsonify({"message": "Error: Selected session is occupied by others."})
        elif permission["EDITFACILITYRECORD"]:
            if stime < datetime.datetime.today():
                return flask.jsonify({"message": "Error: You cannot book facilities in the past."})
            else:
                try:
                    addFacilityRecord(stime,etime,flask.session.get('UID'),fid, flask.request.form.get("unit"),flask.request.form.get("description"), True)
                    return flask.jsonify({"message": "Succeed."})
                except Exception as error:
                    return flask.jsonify({"message": f"Error: {error}"})
        else:
            if stime < datetime.datetime.today() + datetime.timedelta(days=7):
                return flask.jsonify({"message": "Error: You can only book rooms after a week."})
            else:
                try:
                    addFacilityRecord(stime,etime,flask.session.get('UID'),fid, flask.request.form.get("unit"),flask.request.form.get("description"))
                    return flask.jsonify({"message": "Succeed."})
                except Exception as error:
                    return flask.jsonify({"message": f"Error: {error}"})
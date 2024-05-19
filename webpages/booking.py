from __main__ import app
import flask
import modules.sql as sql
import modules.html as html
import modules.datetime as dt
import datetime

@app.route('/booking')
def booking():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    
    permission = sql.commands.rolePermissions(flask.session.get('UID'))

    result = sql.sql(f"SELECT RID, RNAME, FLOOR, AREA, CAPACITY FROM room WHERE AVAILABILITY ORDER BY RID", tupleToList=True)
    for i in range(len(result.result)):
        result.result[i][0] = html.hyperlink(result.result[i][0],f"/booking/{result.result[i][0]}")
        result.result[i][2] = (str(result.result[i][2]) if result.result[i][2] else 'G') + "/F"
    table = html.table(result.field_display,result.result,{"class": "sortable"})

    return flask.render_template('booking.html', table=table, permission = permission)


@app.route('/booking/<rid>', methods=["GET", "POST"])
def booking2(rid):
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))

    rname = sql.commands.roomName(rid)
    minweek = dt.dateToWeekNum(datetime.date.today())
    error = ''
    
    if flask.request.method == 'POST':
        #
        if "submit" in flask.request.form or len(flask.request.form["purpose"])>0 and len(flask.request.form["etime"]) > 0 and len(flask.request.form["purpose"]) > 0:
            week = flask.request.form["week"]
            if len(flask.request.form["stime"]) > 0  and len(flask.request.form["etime"]) > 0 and len(flask.request.form["purpose"]) > 0:
                stime = dt.strToDate(flask.request.form["stime"])
                etime = dt.strToDate(flask.request.form['etime'])
                if etime<=stime:
                    error = "Ending time must be after starting time."
                elif stime < datetime.datetime.today() + datetime.timedelta(days=1):
                    error = "Only section after 24 hours is available for booking."
                elif len(sql.commands.recordInfo(rid,str(stime+datetime.timedelta(seconds=1)),str(etime-datetime.timedelta(seconds=1))).result)>0:
                    error = "Selected time section is occupied by another booking."
                else:
                    if permission["EDITRECORD"]:
                        sql.sql('''INSERT INTO bookingrecord
                                   (STIME,ETIME,UID,RID,PURPOSE,PENDING,AVAILABILITY)
                                   VALUES (?,?,?,?,?,0,1)''',
                                   str(stime),str(etime),flask.session.get('UID'),rid,flask.request.form["purpose"],commit=True)
                    else:
                        sql.sql('''INSERT INTO bookingrecord
                                   (STIME,ETIME,UID,RID,PURPOSE,PENDING,AVAILABILITY)
                                   VALUES (?,?,?,?,?,1,0)''',
                                   str(stime),str(etime),flask.session.get('UID'),rid,flask.request.form["purpose"],commit=True)
                        error = "Succeed."
            else:
                error = "Please fill in everything."
        elif "next" in flask.request.form:
            week = dt.dateToWeekNum(dt.weekNumToDate(flask.request.form["week"])[0]+datetime.timedelta(days=7))
        elif "previous" in flask.request.form:
            if minweek!=flask.request.form["week"]:
                week = dt.dateToWeekNum(dt.weekNumToDate(flask.request.form["week"])[0]-datetime.timedelta(days=7))
            else:
                week = minweek
        else:
            week = flask.request.form["week"]
        
            
    else:
        week = minweek
    date = dt.weekNumToDate(week)
    code = []
    
    for i in range(len(date)):
        code.append([])
        if datetime.date.today()<=date[i]:
            t1 = datetime.datetime.combine(date[i], datetime.datetime.min.time())
            t2 = t1 + datetime.timedelta(days=1)
            if datetime.date.today()==date[i]:
                height = (datetime.datetime.now()-t1).total_seconds()/datetime.timedelta(hours=24).total_seconds()*30*24
                code[i].append({
                    "color": "0,0,0",
                    "height": height,
                    "top": 50,
                    "text": ""
                })
                result = sql.commands.recordInfo(rid,str(datetime.datetime.today())[:19],str(date[i])+" 23:59:59")
            else:
                result = sql.commands.recordInfo(rid,str(date[i])+" 00:00:00",str(date[i])+" 23:59:59")
            for j in result.result:
                j = list(j)
                j[0] = datetime.datetime.strptime(j[0], '%Y-%m-%d %H:%M:%S')
                j[1] = datetime.datetime.strptime(j[1], '%Y-%m-%d %H:%M:%S')
                j[0] = max(j[0], t1, datetime.datetime.now())
                j[1] = min(j[1], t2)
                if j[0]==j[1]:
                    continue
                top = (j[0]-t1).total_seconds()/datetime.timedelta(hours=24).total_seconds()*30*24+50
                height = (j[1]-j[0]).total_seconds()/datetime.timedelta(hours=24).total_seconds()*30*24
                code[i].append({
                    "color": "0,255,0",
                    "height": height,
                    "top": top,
                    "text": j[2]
                })
                if j[3]:
                    code[i][-1]["color"] = "255,0,0"
        else:
            code[i].append({
                    "color": "0,0,0",
                    "height": 720,
                    "top": 50,
                    "text": ""
                })
            code[i]+="<div class = 'box' style = 'top: 50px; height: 720px; border-color: black; background-color: rgba(0,0,0,0.4)'></div>"
    
    table = ""
    if datetime.date.today() >= date[0]:
        result = sql.commands.recordInfo(rid,str(datetime.datetime.today())[:19],str(date[6])+" 23:59:59")
    else:
        result = sql.commands.recordInfo(rid,str(date[0])+" 00:00:00",str(date[6])+" 23:59:59")
    if result.result:
        for i in range(len(result.result)):
            result.result[i][3] = ["Approved","Pending"][result.result[i][3]]
        table = html.table(result.field_display,result.result,{"class": "sortable"})
    return flask.render_template('booking2.html',rid=rid,rname=rname,minweek=minweek, week=week, date=date, code=code, table=table,error=error, permission = permission)

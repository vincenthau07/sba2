import flask, os
import datetime
from server import *
import dbsql as sql
# html initialise
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=2)

def get_week_num(date):
    date += datetime.timedelta(days=4-datetime.date.isoweekday(date))
    date2 = datetime.date(date.year,1,1)
    date2 += datetime.timedelta(days=(11-datetime.date.isoweekday(date2))%7-3)
    return f"{date.year}-W{(date-date2).days//7+1:02d}"

def get_whole_week(week):
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

def checkSessionAvai(session):
    if 'UID' not in session or 'password' not in session:
        return False
    pw = sql.getPassword(session["UID"])
    if pw is None or pw!=session["password"]:
        return False
    return True



@app.route('/')
def root():
    return flask.redirect('/login')


#return errors / redirect home page
@app.route('/login', methods=["GET","POST"])
def login():
    if flask.request.method == 'POST':
        user = flask.request.form["userid"]
        pw = flask.request.form["password"]
        if user == '':
            error = "Empty username"
        elif pw == '':
            error = "Empty password"
        else:
            if pw == sql.getPassword(user):
                flask.session['UID'] = user
                flask.session['password'] = pw
                flask.session.permanent = True
                return flask.redirect('/home')
            error = "Invalid username or password"
        return flask.render_template('login.html', error=error)
    elif flask.request.method == 'GET':
        if not checkSessionAvai(flask.session):
            return flask.render_template('login.html')
        else:
            return flask.redirect('/home')

@app.route('/home')
def home():
    if not checkSessionAvai(flask.session):
        return flask.redirect('/login')
    
    permission = sql.getPermission(flask.session.get('UID'))
    return flask.render_template('home.html', permission = permission, username = sql.getUsername(flask.session.get('UID')))

@app.route('/logout')
def logout():
    del flask.session['UID']
    del flask.session['password']
    flask.session.permanent = False
    return flask.redirect('/login')

@app.route('/booking')
def booking():
    if not checkSessionAvai(flask.session):
        return flask.redirect('/login')
    permission = sql.getPermission(flask.session.get('UID'))

    result = sql.sql(f"SELECT RID, RNAME, FLOOR, AREA, CAPACITY FROM room WHERE AVAILABILITY ORDER BY RID")

    return flask.render_template('booking.html', result = result, permission = permission)


@app.route('/booking/<rid>', methods=["GET", "POST"])
def booking2(rid):
    if not checkSessionAvai(flask.session):
        return flask.redirect('/login')
    permission = sql.getPermission(flask.session.get('UID'))

    rname = sql.getRoomName(rid)
    minweek = get_week_num(datetime.date.today())
    error = ''
    
    if flask.request.method == 'POST':
        if "submit" in flask.request.form or len(flask.request.form["purpose"])>0 and len(flask.request.form["etime"]) > 0 and len(flask.request.form["purpose"]) > 0:
            week = flask.request.form["week"]
            if len(flask.request.form["stime"]) > 0  and len(flask.request.form["etime"]) > 0 and len(flask.request.form["purpose"]) > 0:
                stime = flask.request.form["stime"]
                etime = flask.request.form['etime']
                stime = datetime.datetime(int(stime[:4]),int(stime[5:7]),int(stime[8:10]),int(stime[11:13]),int(stime[14:16]))
                etime = datetime.datetime(int(etime[:4]),int(etime[5:7]),int(etime[8:10]),int(etime[11:13]),int(etime[14:16]))
                if etime<=stime:
                    error = "Ending time must be after starting time."
                elif stime < datetime.datetime.today() + datetime.timedelta(minutes=10):
                    error = "Only section after 10 min is available for booking."
                elif len(sql.getSchedule(rid,str(stime+datetime.timedelta(seconds=1)),str(etime-datetime.timedelta(seconds=1))))>0:
                    error = "Selected time section is occupied by another booking."
                else:
                    sql.modify('''INSERT INTO bookingrecord
                               (STIME,ETIME,UID,RID,PURPOSE)
                               VALUES (?,?,?,?,?)''',
                               str(stime),str(etime),flask.session.get('UID'),rid,flask.request.form["purpose"])
                    error = "Succeed."
            else:
                error = "Please fill in everything."
        elif "next" in flask.request.form:
            week = get_week_num(get_whole_week(flask.request.form["week"])[0]+datetime.timedelta(days=7))
        elif "previous" in flask.request.form:
            if minweek!=flask.request.form["week"]:
                week = get_week_num(get_whole_week(flask.request.form["week"])[0]-datetime.timedelta(days=7))
            else:
                week = minweek
        else:
            week = flask.request.form["week"]
        
            
    else:
        week = minweek
    date = get_whole_week(week)
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
                result = sql.getSchedule(rid,str(datetime.datetime.today())[:19],str(date[i])+" 23:59:59")
            else:
                result = sql.getSchedule(rid,str(date[i])+" 00:00:00",str(date[i])+" 23:59:59")
            for j in result:
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
                    "color": "255,0,0",
                    "height": height,
                    "top": top,
                    "text": j[2]
                })
        else:
            code[i].append({
                    "color": "0,0,0",
                    "height": 720,
                    "top": 50,
                    "text": ""
                })
            code[i]+="<div class = 'box' style = 'top: 50px; height: 720px; border-color: black; background-color: rgba(0,0,0,0.4)'></div>"
    
    if datetime.date.today() >= date[0]:
        result = sql.getSchedule(rid,str(datetime.datetime.today())[:19],str(date[6])+" 23:59:59")
    else:
        result = sql.getSchedule(rid,str(date[0])+" 00:00:00",str(date[6])+" 23:59:59")

    return flask.render_template('booking2.html',rid=rid,rname=rname,minweek=minweek, week=week, date=date, code=code, result=result,error=error, permission = permission)

@app.route('/records', methods=["GET", "POST"])

def records():
    if not checkSessionAvai(flask.session):
        return flask.redirect('/login')
    permission = sql.getPermission(flask.session.get('UID'))
    if not permission["ADDRECORD"]:
        return flask.redirect('/home')
    remark = ''
    if flask.request.method == 'POST':
        for i in flask.request.form:
            try:
                sql.modify(f"DELETE FROM bookingrecord WHERE UID = '{flask.session.get('UID')}' AND BID = {i}")
                remark = "Deletion succeed."
            except Exception as e:
                remark = e
    
    rcds = sql.sql(f"SELECT BID, STIME, ETIME, a.RID, RNAME, PURPOSE FROM bookingrecord a, room b WHERE UID = \'{flask.session.get('UID')}\' AND a.RID = b.RID AND ETIME>=?", str(datetime.datetime.today()))
    return flask.render_template('records.html', remark=remark, rcds = rcds, permission = permission)

@app.route('/sql', methods=["GET", "POST"])

def sqlpage():
    if not checkSessionAvai(flask.session):
        return flask.redirect('/login')
    permission = sql.getPermission(flask.session.get('UID'))
    if permission["ROLE"]!="ADMIN":
        return flask.redirect('/home')
    if flask.request.method == 'POST':
        cmd = flask.request.form["sql"]
        result = []
        column = []
        
        
        for i in cmd.split(";"):
            try:
                temp = sql.modify(i)
                if sql.cur.description == None:
                    temp = f"\"{i}\" succeed."
                    column.append("")
                else:
                    column.append([field[0] for field in sql.cur.description])
                result.append(temp)
                
            except Exception as error:
                result.append(error)
                column.append("")
        return flask.render_template('sql.html', permission=permission, column=column, result=result, cmd = cmd)
    elif flask.request.method == 'GET':
        return flask.render_template('sql.html', permission=permission)

if __name__ == '__main__':
    app.debug=False
    app.run(host=IP,PORT=10000)
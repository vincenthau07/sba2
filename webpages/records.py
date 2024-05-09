from __main__ import app
import flask, datetime
import modules.sql as sql

@app.route('/records', methods=["GET", "POST"])

def records():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))
    if not permission["ADDRECORD"]:
        return flask.redirect('/home')
    remark = ''
    if flask.request.method == 'POST':
        for i in flask.request.form:
            try:
                sql.sql(f"DELETE FROM bookingrecord WHERE UID = '{flask.session.get('UID')}' AND BID = {i}",commit=True)
                remark = "Deletion succeed."
            except Exception as e:
                remark = e
    
    rcds = sql.sql(f"SELECT BID, STIME, ETIME, a.RID, RNAME, PURPOSE FROM bookingrecord a, room b WHERE UID = \'{flask.session.get('UID')}\' AND a.RID = b.RID AND ETIME>=?", str(datetime.datetime.today())).result
    return flask.render_template('records.html', remark=remark, rcds = rcds, permission = permission)
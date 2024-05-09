from __main__ import app
import flask, datetime
import modules.sql as sql
import modules.html as html

@app.route('/users', methods=["GET", "POST"])
def users():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))
    if not permission["VIEWUSER"]:
        return flask.redirect('/home')
    
    error = ""
    
    if flask.request.method == 'POST':
        form = dict(flask.request.form)
        if all((form[x] for x in form)):
            del form["submit"]

            try:
                sql.sql(f"INSERT INTO user ({','.join((x for x in form))}) VALUES ({','.join(('?' for x in form))})", *(form[x] for x in form),commit=True)
                error = "Succeed"
            except Exception as e:
                error = e
        else:
            error = "Please fill in all required information."

    elif flask.request.method == 'GET':
        pass

    users = sql.sql("SELECT * FROM user")
    column = users.field
    users = users.result
    role = [i[0] for i in sql.sql("SELECT ROLE FROM roles").result]

    return flask.render_template('users.html', permission=permission, users=users, column=column, role=role, error=error)

@app.route('/users/<uid>', methods=["GET", "POST"])
def users2(uid):
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))
    if not permission["EDITUSER"]:
        return flask.redirect('/home')

    error = ""
    print(dict(flask.request.form))
    if flask.request.method == 'POST':
        if "delete" in flask.request.form:
            try:
                sql.sql("DELETE FROM user WHERE UID = ?",uid,commit=True)
                return flask.redirect('/users')
            except Exception as e:
                error = e

        else:
            form = dict(flask.request.form)
            
            if all((form[x] for x in form)):
                del form["submit"]

                try:
                    sql.sql(f"UPDATE user SET {','.join((x+'=?' for x in form))} WHERE UID = ?", *(form[x] for x in form),uid,commit=True)
                    error = "Succeed"
                    return flask.redirect(f'/users/{form["UID"]}')
                except Exception as e:
                    error = str(e)
            else:
                error = "Please fill in all required information."
    elif flask.request.method == 'GET':
        pass

    user = sql.sql("SELECT * FROM user WHERE UID = ?", uid).result
    column = [field[0] for field in sql.cur.description]
    role = [i[0] for i in sql.sql("SELECT ROLE FROM roles").result]

    return flask.render_template('users2.html', permission=permission, user=user[0], column=column, role = role, error = error, uid=uid)
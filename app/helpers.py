import sqlite3, flask, re, datetime
from typing import Union

conn = sqlite3.connect("database/database.sqlite", check_same_thread=False)
cur = conn.cursor()
from database.schema import SCHEMA

#sql
class sql():
    def __init__(self,command: str,*params,commit=False, tupleToList=False) -> None:

        #execute sql command
        cur.execute(command, params)
        if commit:
            conn.commit()
        self.result = cur.fetchall()

        #find which table(s) is/are in use
        if cur.description:
            self.table = []
            for word in re.split(',| |\n', command):
                if word.lower() in SCHEMA:
                    self.table.append(word.lower())


        if tupleToList:
            self.result = [list(arr) for arr in self.result]

        self.field = [i[0] for i in cur.description] if cur.description else None
        #self.description = copy.deepcopy(cur.description)
    
    def field_name(self):
        rtn = []
        for f in self.field:
            for t in self.table:
                if f in SCHEMA[t].fields:
                    rtn.append(SCHEMA[t].fields[f].displayName if SCHEMA[t].fields[f].displayName else f)
                    break
        return rtn
    
    def data_type(self):
        rtn = []
        for f in self.field:
            for t in self.table:
                if f in SCHEMA[t]:
                    rtn.append(SCHEMA[t].fields[f].datatype if SCHEMA[t].fields[f].datatype else f)
                    break
        return rtn

def get_by_primary_key(table: str, primary_key, required_field: Union[str, list]="*", **args):
    rtn = sql(f"""SELECT {required_field if type(required_field) is str else ','.join(required_field)} FROM {table} 
               WHERE {SCHEMA[table].primaryKey} = ?""", primary_key, **args).result[0]
    return rtn[0] if type(required_field) is str else rtn

def sessionValidity(session):
    if 'UID' not in session or 'password' not in session:
        return False
    try:
        pw = get_by_primary_key("user", session['UID'], "PASSWORD")
    except TypeError:
        return False
    if pw==session["password"]:
        return True
    return False

def role_permissions(uid=None,role=None):
    if uid:
        result = sql("""SELECT * FROM roles 
                        WHERE ROLE = (SELECT ROLE FROM user WHERE UID = ?)
                        """, uid)
        
    if role:
        result = sql("""SELECT * FROM roles 
                        WHERE ROLE = ?
                        """, role)
    permissions = {}
    field = result.field
    for i in range(len(field)):
        permissions[field[i]] = result.result[0][i]
    return permissions

def verifySession(session, permission: str=None, role=None):
    def wrapper(func):
        def decorator(*args, **kwargs):
            if not sessionValidity(session):
                return flask.redirect('/login')
            permission_li = role_permissions(uid = session["UID"])
            if permission and not permission_li[permission.format(*map(lambda x: x.upper(), kwargs.values()))] or role and permission_li[SCHEMA["roles"].primaryKey]!=role:
                return flask.redirect('/home')
            kwargs["permission"] = permission_li
            return func(*args, **kwargs)
        return decorator
    return wrapper 

class html:
    def table(field: list, cell: list, params: dict={}):
        rtn = "<table"
        for key in params:
            rtn+=f" {key}=\"{params[key]}\""
        rtn+=">"
        rtn+="<thead>"
        rtn+="<tr>"
        for i in field:
            rtn+=f"<th>{i}</th>"
        rtn+="</tr>"
        rtn+="</thead>"
        rtn+="<tbody>"
        for i in cell:
            rtn+="<tr>"
            for j in i:
                rtn+=f"<td>{j}</td>"
            rtn+="</tr>"
        rtn+="</tbody>"
        rtn+="</table>"
        return rtn

    def hyperlink(text: str, link: str, params: dict={}):
        rtn = f"<a href=\"{link}\""
        for key in params:
            rtn += f" {key}=\"{params[key]}\""
        rtn+= ">"
        rtn+= text
        rtn+= "</a>"
        return rtn

    def linebreak():
        return "<br>"

    def div(text: str, params: dict={}):
        rtn = f"<div"
        for key in params:
            rtn += f" {key}=\"{params[key]}\""
        rtn+= ">"
        rtn+= text
        rtn+= "</div>"
        return rtn

    def input(params: dict={}):
        rtn = f"<input"
        for key in params:
            rtn += f" {key}=\"{params[key]}\""
        rtn += ">"
        return rtn

def num_to_floor(li: list, column_index: int):
    for i in range(len(li)):
        floornum = li[i][column_index]
        li[i][column_index] = "G/F" if floornum == 0 else f"{floornum}/F" if floornum > 0 else f"B{floornum}/F"
    return li

def text_to_link(li: list, path: str, column_index: int):
    for i in range(len(li)):
        li[i][column_index] = html.hyperlink(li[i][column_index], path.format(li[i][column_index]))
    return li

def strToDate(string):
    if len(string) > 16:
        return datetime.datetime(int(string[:4]),int(string[5:7]),int(string[8:10]),int(string[11:13]),int(string[14:16]),int(string[17:19]))
    else:
        return datetime.datetime(int(string[:4]),int(string[5:7]),int(string[8:10]),int(string[11:13]),int(string[14:16]))
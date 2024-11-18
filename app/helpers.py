import sqlite3, flask, re, datetime
from typing import Union
import threading

conn = sqlite3.connect("database/database.sqlite", check_same_thread=False)
cur = conn.cursor()
from database.schema import SCHEMA

#lock is used to prevent error "Recursive use of cursors not allowed"
_lock = threading.Lock()

#sql
class sql():
    """
    Execute SQL command, storing return table field and values in `self.result` and `self.field` respectively

    Parameters
    ----
    command (str)
        SQL command
    *params: (any, optional)
        Substitute value
    commit (bool, optional)
        If yes, update values in database after executing the command (e.g. UPDATE, INSERT)
    tupleToList (bool, optional)
        If yes, convert result from tuple to list
    """
    def __init__(self,command: str,*params,commit=False, tupleToList=False) -> None:
        try:
            _lock.acquire(True)
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
        finally:
            _lock.release()
    
    def field_name(self):
        """
        Return an array of displaying names of each field by searching in `SCHEMA` from /database/schema.py

        Return
        ----
        list Display names of each field
        """
        rtn = []
        for f in self.field:
            for t in self.table:
                if f in SCHEMA[t].fields:
                    rtn.append(SCHEMA[t].fields[f].displayName if SCHEMA[t].fields[f].displayName else f)
                    break
        return rtn
    
    def data_type(self):
        """
        Return an array of data types of each field by searching in `SCHEMA` from /database/schema.py4

        Return
        ----
        list Data types of each field
        """
        rtn = []
        for f in self.field:
            for t in self.table:
                if f in SCHEMA[t]:
                    rtn.append(SCHEMA[t].fields[f].datatype if SCHEMA[t].fields[f].datatype else f)
                    break
        return rtn

def get_by_primary_key(table: str, primary_key, required_field: Union[str, list]="*", **args):
    """
    Return a record with input (a) field(s) or all fields matching a specific primary key

    Parameters
    ---
    table (str)
        table name
    primary_key (any)
        primary key
    required_field (str, tuple, list, optional)
        field(s) that will be returned
    **args (any)
        conditions of 'sql'

    Return
    ----
    tuple: a record
    """
    rtn = sql(f"""SELECT {required_field if type(required_field) is str else ','.join(required_field)} FROM {table} 
               WHERE {SCHEMA[table].primaryKey} = ?""", primary_key, **args).result[0]
    return rtn[0] if type(required_field) is str else rtn

def sessionValidity(session):
    """
    Return True if session is valid else False

    Parameters
    ---
    session (flask.session)
        user's session
    
    Return
    ---
    bool: session validity
    """
    if 'UID' not in session:
        return False
    try:
        get_by_primary_key("user", session['UID'])
    except TypeError:
        return False
    return True

def role_permissions(uid=None,role=None):
    """
    Get all permissions of a user or a role

    Parameters
    ---
    uid (str, optional)
        User's ID
    role (str, optional)
        User's role
    
    Return
    ---
    dict: an array of each permission
    """
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
    """
    A decorator. Check if session is valid and user is allowed to browse this webpage. If session is not valid, redirect to /login. If user is not allowed, redirect to /home.
    
    Parameters
    ---
    session (flask.session)
        User's session
    permission (str, optional)
        Permission required to browse this webpage
    role
        Role required to browse this webpage
    """
    def wrapper(func):
        def decorator(*args, **kwargs):
            if not sessionValidity(session):
                return flask.redirect('/login')
            permission_li = role_permissions(uid = session["UID"])
            if permission and not permission_li[permission.format(*map(lambda x: x.upper(), kwargs.values()))] or role and permission_li[SCHEMA["roles"].primaryKey]!=role:
                return flask.redirect('/home')
            kwargs["permission"] = permission_li
            return func(*args, **kwargs)
        decorator.__name__ = func.__name__
        return decorator
    return wrapper 

def dateToWeekNumber(date: datetime.datetime) -> str:
    """
    Return which week the date is in

    Parameter
    ---
    date (datetime.datetime)
        date

    Return
    ---
    str: week number

    Example:
    >>> dataToWeekNumber(datetime.datetime(2024, 1, 1))
    2024-W01
    """
    date += datetime.timedelta(days=4-datetime.date.isoweekday(date))
    date2 = datetime.date(date.year,1,1)
    date2 += datetime.timedelta(days=(11-datetime.date.isoweekday(date2))%7-3)
    return f"{date.year}-W{(date-date2).days//7+1:02d}"

def weekNumToDate(week) -> list:
    """
    Return the whole week with a week number

    Parameter
    ---
    week (str)
        week number

    Return
    ---
    list: an array of 7 dates in that week

    Example:
    >>> dataToWeekNumber('2024-W01')
    [datetime.date(2024, 1, 1), datetime.date(2024, 1, 2), datetime.date(2024, 1, 3), datetime.date(2024, 1, 4), datetime.date(2024, 1, 5), datetime.date(2024, 1, 6), datetime.date(2024, 1, 7)]
    """
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

class html:
    def table(field: list, cell: list, params: dict={}):
        """
        Return a table in html code
        """
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
        """
        Return a hyperlink in html code
        """
        rtn = f"<a href=\"{link}\""
        for key in params:
            rtn += f" {key}=\"{params[key]}\""
        rtn+= ">"
        rtn+= text
        rtn+= "</a>"
        return rtn

    def linebreak():
        """
        Return a line break in html code
        """
        return "<br>"

    def div(text: str, params: dict={}):
        """
        Return a div in html code
        """
        rtn = f"<div"
        for key in params:
            rtn += f" {key}=\"{params[key]}\""
        rtn+= ">"
        rtn+= text
        rtn+= "</div>"
        return rtn

    def input(params: dict={}):
        """
        Return an <input> in html code
        """
        rtn = f"<input"
        for key in params:
            rtn += f" {key}=\"{params[key]}\""
        rtn += ">"
        return rtn

    def button(text, params: dict={}):
        """
        Return a <button> in html code
        """
        rtn = f"<button"
        for key in params:
            rtn += f" {key}=\"{params[key]}\""
        rtn += ">" + text + "</button>"
        return rtn

def num_to_floor(li: list, column_index: int):
    """
    Convert number in a column to floor number

    Parameters
    ---
    li (list or tuple)
        a 2D array
    column_index (int)
        column which will be converted
    
    Return
    ---
    list: Updated array
    """
    for i in range(len(li)):
        floornum = li[i][column_index]
        li[i][column_index] = "G/F" if floornum == 0 else f"{floornum}/F" if floornum > 0 else f"B{floornum}/F"
    return li

def text_to_link(li: list, path: str, column_index: int):
    """
    Convert text in a column to a hyperlink

    Parameters
    ---
    li (list or tuple)
        a 2D array
    path (str)
        redirect link
    column_index (int)
        column which will be converted
    
    Return
    ---
    list: Updated array
    """
    for i in range(len(li)):
        li[i][column_index] = html.hyperlink(li[i][column_index], path.format(li[i][column_index]))
    return li

def strToDate(string):
    """
    Convert from `str` to `datetime.datetime`
    """
    if len(string) > 16:
        return datetime.datetime(int(string[:4]),int(string[5:7]),int(string[8:10]),int(string[11:13]),int(string[14:16]),int(string[17:19]))
    else:
        return datetime.datetime(int(string[:4]),int(string[5:7]),int(string[8:10]),int(string[11:13]),int(string[14:16]))
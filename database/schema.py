from datetime import datetime

class field:
    def __init__(self, datatype, displayName: str=None, foreignKey: tuple=None, options: tuple = None, command: tuple=None):
        self.displayName = displayName
        self.datatype = datatype
        self.foreignKey = foreignKey
        self.options = options
        self.command = command

class table:
    def __init__(self, fields: dict, primaryKey: tuple, canBeManaged=False):
        self.fields = fields
        self.primaryKey = primaryKey
        self.canBeManaged = canBeManaged

SCHEMA = {
    "facility": table(
        {
            "FID": field(str),
            "FNAME": field(str, "Facility Name"),
            "AVAILABILITY": field(bool, "Availability")
        }, ("FID"), True
    ),
    "facility_record": table(
        {
            "BID": field(int),
	        "STIME": field(datetime, "Start Datetime"),
	        "ETIME": field(datetime, "End Datetime"),
	        "UID": field(str, foreignKey=("user", "UID")),
	        "FID": field(str, foreignKey=("facility", "FID")),
	        "UNIT":	field(int, "Unit", foreignKey=("school_unit", "UNIT")),
	        "DESCRIPTION": field(str, "Description"),
	        "AVAILABILITY":	field(bool, "Availability"),
	        "APPROVED_BY":	field(str, "Approved by", command=["SELECT UID FROM user WHERE ROLE IN (SELECT ROLE FROM roles WHERE EDITROOM_RECORD)"]),
        }, ("BID"), True
    ),
    "login": table(
        {
            "UID": field(str),
            "IP": field(str),
            "TIME": field(datetime)
        }, ("IP", "TIME")
    ),
    "roles": table(
        {
            "ROLE": field(str),
            "EDITUSER": field(bool),
	        "EDITROOM": field(bool),
	        "ADDRECORD": field(bool),
	        "EDITROOM_RECORD": field(bool),
	        "EDITFACILITY": field(bool),
            "EDITSCHOOL_CATEGORY": field(bool),
	        "EDITSCHOOL_UNIT": field(bool),
	        "EDITFACILITY_RECORD": field(bool),
	        "EDITROLES": field(bool)
        }, ("ROLE"), True
    ),
    "room": table(
        {
            "RID": field(str),
            "RNAME": field(str, "Room Name"),
            "FLOOR": field(int, "Floor"),
	        "AREA":	field(float, "Area"),
	        "CAPACITY":	field(int, "Capacity"),
	        "AVAILABILITY": field(bool, "Availability")
        }, ("RID"), True
    ),
    "room_record": table(
        {
            "BID": field(int),
	        "STIME": field(datetime, "Start Datetime"),
	        "ETIME": field(datetime, "End Datetime"),
	        "UID": field(str, foreignKey=("user", "UID")),
	        "RID": field(str, foreignKey=("room", "RID")),
	        "UNIT":	field(int, "Unit", foreignKey=("school_unit", "UNIT")),
	        "DESCRIPTION": field(str, "Description"),
	        "AVAILABILITY":	field(bool, "Availability"),
	        "APPROVED_BY":	field(str, "Approved by", command=["SELECT UID FROM user WHERE ROLE IN (SELECT ROLE FROM roles WHERE EDITROOM_RECORD) UNION SELECT 'None'"]),
        }, ("BID"), True
    ),
    "school_category": table(
        {"CATEGORY": field(str, "Category")}, ("CATEGORY"), True
    ),
    "school_unit": table(
        {
            "UNIT": field(str, "Unit"),
            "NAME": field(str, "Unit Name"),
            "CATEGORY": field(str, "Category", foreignKey=("school_category", "CATEGORY"))
        }, ("UNIT"), True
    ),
    "user": table(
        {
            "UID": field(str),
            "PASSWORD": field(str, "Password"),
            "ROLE": field(str, "Role", foreignKey=("roles", "ROLE")),
            "SEX": field(str, "Sex", options = ('M',"F")),
            "EMAIL": field(str, "Email"),
            "UNAME": field(str, "User Name")
        }, ("UID"), True
    )
}
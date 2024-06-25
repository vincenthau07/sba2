import modules.sql as sql
sql.sql("""INSERT INTO roomrecord
("STIME", "ETIME", "UID", "RID", "UNIT", "DESCRIPTION", "AVAILABILITY", "APPROVED_BY")
VALUES ('2024-06-18 14:00:00', '2024-06-18 16:00:00', 'S190377', 'C001', 31, 'abc', 1, 'S190377');""", commit=True)
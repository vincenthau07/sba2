from dbsql import *
print(modify("insert into user values ('bbc', '12345678', 'TEACHER', 'M', 'no@no.com', 'Mr Chow')"))
print(cur.description)
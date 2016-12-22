#coding:utf8
import dbutil
conn = dbutil.DB('spare_parts','10.1.1.7','root','root')
conn.connect()
sql = 'select * from big_class'
tmp = conn.execute(sql)
print tmp

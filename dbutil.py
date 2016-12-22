#!/usr/bin/env python
#coding=utf-8

import MySQLdb as mysql


class DB():
    def __init__(self,db,host,user,passwd):
        self.db = db
        self.host = host
        self.user = user
        self.passwd = passwd
        self.connect()
    def connect(self):
        self.con = mysql.connect(db=self.db,charset='utf8',host=self.host,user=self.user,passwd=self.passwd)
        self.cursor = self.con.cursor()
        self.con.autocommit(True)
    def execute(self,sql):
        try:
            self.cursor.execute(sql)
        except:
            try:
                self.con.close()
                self.cursor.close()
            except:
                pass
            try:
                self.connect()
                self.cursor.execute(sql)
            except Exception as e:
                print e
                return 'error'
        res = self.cursor.fetchall()
        #print res
        return res
            






if __name__ == '__main__':
    db = DB('spare_parts','10.1.1.7','root','root')
    db.connect()


    
                      
    

    

from base import base
import pymysql
import hashlib
import datetime


class report(base):
    def __init__(self):
        self.setup('Reports')
    
    def hashPassword(self,pw):
        salt = 'xyz'
        return hashlib.md5(pw.encode('utf-8')).hexdigest()

    def verify_insert(self,n=0):
        self.errors = []
        if self.data[n]['User_ID'] == '':
            self.errors.append('User_ID cannot be blank.')
        e = report()
        e.getByField('User_ID', self.data[n]['User_ID'])
        if len(e.data) > 0:
            #self.errors.append('User_ID already in use')
            return True
        if len(self.errors) == 0:
            return True
        else:
            return False
        
    def verify_update(self,n=0):
        self.errors = []
        if self.data[n]['User_ID'] == '':
            self.errors.append('User_ID cannot be blank.')
        e = report()
        e.getByField('User_ID', self.data[n]['User_ID'])
        if len(e.data) > 0 and e.data[0]['Report_ID'] != self.data[n]['Report_ID']:
            #self.errors.append("User_ID already in use")
            return True
        if len(self.errors) == 0:
            return True
        else:
            return False
    
    def getChoices(self):
        #self.connect()
        #sql = f"SELECT * FROM `{self.tn}` WHERE `email` = %s AND `password` = %s;"
        #self.cur.execute(sql,email,hpw)
        self.getAll('Report_Name')
        choices=[]
        for row in self.data:
            value = row['Report_ID']
            text = row['Report_Name']
            choices.append([value,text])
    
            
    
    def allByFK(self, uid):
        self.connect()
        self.data=[]
        #sql = f"SELECT * FROM `Reports` WHERE  `User_ID` = %s AND `Report_Sponsor_ID` = %s;"
        sql = f"SELECT * FROM `{self.tn}` WHERE `User_ID` = %s OR `Report_Sponsor_ID` = %s"
        print(sql,(uid,uid))
        self.cur.execute(sql,(uid,uid))
        for row in self.cur:
            self.data.append(row) 
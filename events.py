from base import base
import pymysql
import hashlib
import datetime


class event(base):
    def __init__(self):
        self.setup('Events')
        self.status = ['Sent', 'Recieved', 'Viewed']
        self.reps_list=[]
    def hashPassword(self,pw):
        salt = 'xyz'
        return hashlib.md5(pw.encode('utf-8')).hexdigest()

    def verify_insert(self,n=0):
        self.errors = []
        if self.data[n]['Report_ID'] == '':
            self.errors.append('Report_ID cannot be blank.')
        e = event()
        e.getByField('Report_ID', self.data[n]['Report_ID'])
        if len(e.data) > 3:
            self.errors.append('Report_ID already in use')
        if len(self.errors) == 0:
            return True
        else:
            return False
        
    def verify_update(self,n=0):
        self.errors = []
        if self.data[n]['Report_ID'] == '':
            self.errors.append('Report_ID cannot be blank.')
        e = event()
        e.getByField('Report_ID', self.data[n]['Report_ID'])
        if len(e.data) > 3 and e.data[0]['Event_ID'] != self.data[n]['Event_ID']:
            self.errors.append("Report_ID already in use")
        if len(self.errors) == 0:
            return True
        else:
            return False
            
            
    def getChoicesByReport(self):
        #self.connect()
        #sql = f"SELECT * FROM `{self.tn}` WHERE `email` = %s AND `password` = %s;"
        #self.cur.execute(sql,email,hpw)
        self.getAll('Report_ID')
        choices=[]
        for self.data in row:
            value = row['Event_ID']
            text = row['Event_Status'] + '(' + row['Report_ID']  + ')'
            choices.append([value,text])
        return choices
    
    def allByFK(self, uid):
        self.connect()
        self.data=[]
        tn = 'Reports'
        #sql = f"SELECT * FROM `Reports` WHERE  `User_ID` = %s AND `Report_Sponsor_ID` = %s;"
        sql = f"SELECT * FROM `{tn}` WHERE `User_ID` = %s OR `Report_Sponsor_ID` = %s"
        #print(sql,(uid,uid))
        self.cur.execute(sql,(uid,uid))
        for row in self.cur:
            self.data.append(row)  
            
    def getAllReports(self, order=None):
        self.connect()
        sql = f'SELECT * FROM Reports;'
        if order is not None:
            sql += f"ORDER BY `{order}`"
        self.logger.info(f"sql = {sql} values = {id}")
        self.cur.execute(sql)
        self.data = []
        for row in self.cur:
            self.data.append(row)
        return self.data
            
    def getallReportsByFK(self, value):
        self.connect()
        self.data=[]
        tnOne='Users'
        tnTwo='Reports'
        tnThree='Events'
        #tnThree='Users'
        sql = f'''SELECT b.Event_ID, b.Event_Date, b.Event_Status, b.Report_ID, a.Report_Name, b.User_ID FROM {tnTwo} a, {tnThree} b 
        WHERE b.Report_ID = a.Report_ID
        AND a.User_ID = %s 
        OR a.Report_Sponsor_ID = %s'''
        #OR a.User_ID = b.Report_Sponsor_ID 
        #print(sql,value)
        self.cur.execute(sql,(value,value))
        for row in self.cur:
            self.data.append(row)
            #eid = row['Event_ID']
            #edate = row['Event_Date']
            #estatus = row['Event_Status']
            #uid = row['User_ID']
            #rname = ['Report_Name']
            #rid = row['Report_ID']
            #self.data.append([eid, edate, estatus, uid, rname, rid, rname]) 
import csv, pymysql
import logging,os
import logging.handlers
from pathlib import Path
import config

class base:
    def setup(self,table):
        self.tn = table
        self.data = []
        self.tempData=[]
        self.errors = []
        self.fields = []
        self.conn = None
        self.cur = None
        self.pk = None
        
        log_path = 'system_logs'
        Path(log_path).mkdir(parents=True, exist_ok=True)

        log_file_name = os.path.join(log_path, 'system_log.txt')
        logging_level = logging.DEBUG
        formatter = logging.Formatter('%(asctime)s, %(name)s, %(levelname)s, %(message)s')
        handler = logging.handlers.TimedRotatingFileHandler(log_file_name, when='midnight', backupCount=365)
        handler.suffix = '%Y-%m-%d'

        handler.setFormatter(formatter)
        self.logger = logging.getLogger('systemLog')
        self.logger.propagate = False
        self.logger.addHandler(handler)
        self.logger.setLevel(logging_level)
        
        self.getFields()
    
    def connect(self):
        self.conn = pymysql.connect(host=config.host, port=config.port, user= config.user,
                                passwd=config.passwd, db= config.db, autocommit = True)
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
    
    def close(self):
        self.cur.close()
        self.conn.close()

    def getFields(self):
        self.connect()
        sql = 'DESCRIBE ' + self.tn
        self.cur.execute(sql)
        self.logger.info(f"getting fields for {self.tn}")
        for row in self.cur:
            if 'auto_increment' in row['Extra']:
                self.pk = row['Field']
            else:
                self.fields.append(row['Field'])
        self.logger.info(f"fields = {self.fields}")    
        self.close()
        return True
    
    def createBlank(self):
        #create a blank version of the object
        d = {}
        for fn in self.fields:
            d['fn'] = ''
        self.add(d)
        
    def add(self,d):
        '''d2 = {}
        for k,v in d.items():
            if k in self.fields:
                d2[k] = v
        self.data.append(d2)'''
        self.data.append(d)
        
    def insert(self,n=0):
        self.connect()
        fl = '(`' + '`,`'.join(self.fields) + '`)'
        tl = str('%s,' * len(self.fields))[0:-1]
        sql = 'INSERT INTO ' + self.tn +" "+ fl + ' VALUES ('+tl+');'
        vl = []
        for fn in self.fields:
            vl.append(self.data[n][fn])
        #for fn,val in self.data[n].items():
            #vl.append(val)
        #print(vl)
        self.logger.info(f"sql = {sql} values = {vl} ")
        self.cur.execute(sql,vl)
        self.data[n][self.pk] = self.cur.lastrowid

    def getById(self, id):
        self.connect()
        sql = f"SELECT * FROM `{self.tn}`  WHERE `{self.pk}` = %s;"
        self.logger.info(f"sql = {sql} values = {id}")
        self.cur.execute(sql,id)
        self.data = []
        for row in self.cur:
            self.data.append(row)
            
    def getByField(self, fieldname, value):
        self.connect()
        sql = f'SELECT * FROM `{self.tn}` WHERE `{fieldname}` = %s;'
        self.logger.info(f"sql = {sql} values = {value}")
        self.cur.execute(sql,value)
        self.data = []
        for row in self.cur:
            self.data.append(row)
            
    def getReportsForUser(self, value):
        self.connect()
        self.data = []
        tn = 'Reports'
        #sql = f'SELECT * FROM `{self.tn}` WHERE `{fieldnameOne}` = %s OR `{fieldnameTwo}` = %s;'
        #self.logger.info(f"sql = {sql} values = {valueA} and {valueB}")
        sql = f"SELECT * FROM Reports WHERE User_ID = {value} OR Report_Sponsor_ID = {value};"
        self.cur.execute(sql)
        self.data = []
        for row in self.cur:
            self.data.append(row)
            
    def getEventsForUser(self, value):
        self.connect()
        self.data = []
        tn = 'Reports'
        #sql = f'SELECT * FROM `{self.tn}` WHERE `{fieldnameOne}` = %s OR `{fieldnameTwo}` = %s;'
        #self.logger.info(f"sql = {sql} values = {valueA} and {valueB}")
        sql = f"SELECT * FROM Events WHERE User_ID = {value} OR Report_Sponsor_ID = {value};"
        self.cur.execute(sql)
        self.data = []
        for row in self.cur:
            self.data.append(row)
       
    
    def getAll(self, order=None):
        self.connect()
        sql = f"SELECT * FROM `{self.tn}` "
        if order is not None:
            sql += f"ORDER BY `{order}`"
        self.logger.info(f"sql = {sql} values = {id}")
        self.cur.execute(sql)
        self.data = []
        for row in self.cur:
            self.data.append(row)
                
    def update(self,n=0):
        self.connect()
        fl = []
        for fn in self.fields:
            if fn in self.data[n].keys(): #dont try to update fields if the data doesn't exist
                fl.append(fn)
        fl = '`'+'`=%s, `'.join(fl) + '`=%s'
        sql = f'UPDATE `{self.tn}` SET {fl} WHERE `{self.pk}` = %s;'
        vl = []
        for fn in self.fields:
            if fn in self.data[n].keys(): #dont try to update fields if the data doesn't exist
                vl.append(self.data[n][fn])
        vl.append(self.data[n][self.pk])
        self.logger.info(f"sql = {sql} values = {vl} ")
        self.cur.execute(sql,vl)
        '''for fn,val in self.data[n].items():
            vl.append(val)'''
        #print(vl)
    
    def deleteById(self, id):
        self.connect()
        sql = f"DELETE FROM `{self.tn}`  WHERE `{self.pk}` = %s;"
        self.logger.info(f"sql = {sql} values = {id}")
        self.cur.execute(sql,id)
        
    def getByForeignKey(self,tableOne,tableTwo,fieldOne,fieldTwo):
        self.connect()
        self.data=[]
        tnOne=tableOne
        tnTwo=tableTwo
        sql = f"SELECT * FROM {tableOne} a, {tableTwo} b WHERE a.{fieldOne} = b.{fieldTwo};"
        #print(sql)
        self.cur.execute(sql)
        for row in self.cur:
            self.data.append(row)
        
    def getValByFK(self,tableOne,tableTwo,fieldOne,fieldTwo, value):
        self.connect()
        self.data=[]
        tnOne=tableOne
        tnTwo=tableTwo
        sql = f"SELECT * FROM {tableOne} a, {tableTwo} b WHERE a.{fieldOne} = %s AND b.User_ID = %s OR a.{fieldTwo} = %s AND b.User_ID = %s;" #AND a.{fieldOne} = b.{fieldOne}  OR b.{fieldOne} = a.{fieldTwo};"
        print(sql,value)
        self.cur.execute(sql,(value,value,value,value))
        for row in self.cur:
            self.data.append(row)     


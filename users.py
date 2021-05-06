from base import base
import pymysql
import hashlib
import config

class user(base):
    def __init__(self):
        self.setup('Users')
        self.types = [['0','Inactive'],['1','Employee'],['2','Admin']]
        self.deps_list = []
    def hashPassword(self,pw):
        salt = 'xyz'
        return hashlib.md5(pw.encode('utf-8')).hexdigest()

    def verify_insert(self,n=0):
        self.errors = []
        #print(self.data)
        if self.data[n]['User_Email'] == '':
            self.errors.append('Email cannot be blank.')
        if '@' not in self.data[n]['User_Email']:
            self.errors.append('Email must contain @ sign.')
        u = user()
        u.getByField('User_Email', self.data[n]['User_Email'])
        if len(u.data) > 0 and u.data[0]['User_ID'] != self.data[0]['User_ID']:
            self.errors.append('Email already in use.')
        
        if len(self.data[n]['User_Password']) < 5:
            self.errors.append('Password must be > 4 characters')
        else:
            self.data[n]['User_Password'] = self.hashPassword(self.data[n]['User_Password'])
        if len(self.errors) == 0:
            return True
        else:
            return False
        
    def verify_update(self,n=0):
        self.errors = []
        #print(self.data)
        if self.data[n]['User_Email'] == '':
            self.errors.append('Email cannot be blank.')
        if "@" not in self.data[n]['User_Email']:
            self.errors.append('Email must contain @ sign.')
        u = user()
        if len(u.data) > 0 and u.data[0]['User_ID'] != self.data[n]['User']:
            self.errors.append('Email in use')
        if len(self.data[n]['User_Password']) > 0: #user intends to change pw
            if self.data[n]['User_Password'] != self.data[n]['User_Password2']:
                self.errors.append('Retyped password must match')
            if len(self.data[n]['User_Password']) < 5:
                self.errors.append('Password must be more than 4 characters')
            else:
                self.data[n]['User_Password'] = self.hashPassword(self.data[n]['User_Password'])
        else:
            del self.data[n]['User_Password']
            
        if len(self.errors) == 0:
            return True
        else:
            return False
            
            
    def tryLogin(self, email, password):
        hpw = self.hashPassword(password)
        self.connect()
        sql = f"SELECT * FROM `{self.tn}` WHERE `User_Email` = %s AND `User_Password` = %s;"
        self.cur.execute(sql,(email,hpw))
        self.data = []
        for row in self.cur:
            self.data.append(row)
            

    def getChoices(self):
        #self.connect()
        #sql = f"SELECT * FROM `{self.tn}` WHERE `email` = %s AND `password` = %s;"
        #self.cur.execute(sql,email,hpw)
        self.getAll('User_Last_Name')
        choices=[]
        for row in self.data:
            value = row['User_ID']
            text = row['User_Email'] + '(' + row['User_Last_Name']  + ')'
            choices.append([value,text])
        return choices
        
    def getAllDepartments(self, order=None):
        self.connect()
        sql = f'SELECT * FROM Department;'
        if order is not None:
            sql += f"ORDER BY `{order}`"
        self.logger.info(f"sql = {sql} values = {id}")
        self.cur.execute(sql)
        self.data = []
        for row in self.cur:
            self.data.append(row)
        self.deps_list = []
        for dep in self.data:
            dep_id = dep['Department_ID']
            dep_type = dep['Department_Type']
            results = (dep_id,dep_type)
            self.deps_list.append(results)
        return self.data 




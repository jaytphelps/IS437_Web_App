from base import base
import pymysql
import hashlib

class department(base):
    def __init__(self):
        self.setup('Department')
        self.deps_list=[]
    
    def hashPassword(self,pw):
        salt = 'xyz'
        return hashlib.md5(pw.encode('utf-8')).hexdigest()

    def verify_insert(self,n=0):
        self.errors = []
        if self.data[n]['Department_Type'] == '':
            self.errors.append('Department_Type cannot be blank.')
        d = department()
        d.getByField('Department_Type', self.data[n]['Department_Type'])
        if len(d.data) > 0:
            self.errors.append('Department_Type already in use')
        if len(self.errors) == 0:
            return True
        else:
            return False
        
    def verify_update(self,n=0):
        self.errors = []
        if self.data[n]['Department_Type'] == '':
            self.errors.append('Department_Type cannot be blank.')
        d = department()
        d.getByField('Department_Type', self.data[n]['Department_Type'])
        if len(d.data) > 0 and d.data[0]['Department_ID'] != self.data[n]['Department_ID']:
            self.errors.append("Department_Type already in use")
        if len(self.errors) == 0:
            return True
        else:
            return False
            
            
    def getChoices(self):
        #self.connect()
        #sql = f"SELECT * FROM `{self.tn}` WHERE `email` = %s AND `password` = %s;"
        #self.cur.execute(sql,email,hpw)
        self.getAll('Department_Name')
        choices=[]
        for self.data in row:
            value = row['Department_ID']
            text = row['Department_Type'] + '(' + row['Department_Name']  + ')'
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
        n=0
        self.deps_list = []
        for dep in self.data:
            dep_type = dep['Department_Type']
            dep_name = dep['Department_Name']
            results = (dep_type,dep_name)
            self.deps_list.append(results)


#d = department()
#d.getByField('Department_ID')
#print(d.data)           
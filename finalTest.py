from users import user 
from base import base
from reports import report
from events import event

e = event()
e.getByForeignKey('Reports','Users','User_ID','User_ID')
print(e.data)
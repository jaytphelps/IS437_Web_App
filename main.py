

####################
####################
from flask import Flask
from flask import render_template,send_from_directory,request,redirect,session
from flask_session import Session
from datetime import timedelta
import time
import logging,os
import logging.handlers
from pathlib import Path 
from users import user
from departments import department
from events import event
from reports import report


'''
Configuration and Enstantiation
'''
app = Flask(__name__,static_url_path='')
app.config['SECRET_KEY'] = 'ETYNE&%ERThw4545tq345q3qRGQ5^%$^$%'
 
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
app.config['SESSION_FILE_THRESHOLD'] = 100
sess = Session()
sess.init_app(app)

log_path = 'web_logs'
Path(log_path).mkdir(parents=True, exist_ok=True)

log_file_name = os.path.join(log_path, 'web_log.txt')
logging_level = logging.DEBUG
formatter = logging.Formatter('%(asctime)s, %(name)s, %(levelname)s, %(message)s')
handler = logging.handlers.TimedRotatingFileHandler(log_file_name, when='midnight', backupCount=365)
handler.suffix = '%Y-%m-%d'

handler.setFormatter(formatter)
logger = logging.getLogger('webLog')
logger.addHandler(handler)
logger.setLevel(logging_level)


@app.context_processor
def inject_user():
    return dict(me=session.get('user'))
    
def sessionactive(type):
    try:
        if session.get('user')['User_Type'] == '':
            session['user']['User_Type'] = 0
            print('fixed blank session')
    except Exception as e:
        print(e)
        return False
    if session.get('lastactive') != None and \
        time.time() - session.get('lastactive') < 1000 \
        and int(session.get('user')['User_Type']) >= int(type):
        session['lastactive'] = time.time()
        return True
    return False
    
    
    
    
'''
Login
'''
@app.route('/set')
def set():
    session['key'] = 'value'
    return 'ok'
@app.route('/get')
def get():
    return session.get('key', 'not set') 
@app.route('/logout',methods=['GET','POST'])
def logout():
    session['user'] = None
    session['lastactive'] = None
    session['msg'] = 'You have been logged out'
    return redirect('/login')
@app.route('/login',methods=['GET','POST'])
def login():
    if sessionactive(1):
        return redirect('/mainmenu')
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username is None:
        if session.get('msg') != None:
            msg = session.get('msg')
            session['msg'] = None  #user is logging out
        else:
            msg = "Welcome!"  #first page load of login    
    elif username == '' or password == '':
        msg = 'You must type email and password'   #user has left pw or un blank
    else:
        print(username,password)
        u = user()
        u.tryLogin(username,password)
        if len(u.data) == 1:   #credentials match
            msg= 'login okay'
            session['user'] = u.data[0]
            session['lastactive'] = time.time()
            return redirect('/mainmenu')
        else:     #credentials dont match
            msg = 'Login failed'
            logger.info(f"login failed for user {username}")
    return render_template('login.html',msg=msg) 
    
    
  
'''
Home Page
''' 
@app.route('/')
def root():
    return redirect('/login')
   
@app.route('/mainmenu')
def home():
    if sessionactive(2):
        msg = "Welcome Administrator: " + session.get('user')['User_First_Name'] 
        return render_template('mainmenu.html',title='My Webpage',msg=msg,user_type=session.get('user')['User_Type'])
    elif sessionactive(1):
        msg = "Welcome " + session.get('user')['User_First_Name']
        user_type=session.get('user')['User_Type']
        return render_template('mainmenu.html',title='My Webpage',msg=msg,user_type=session.get('user')['User_Type'])
    else:
        session['msg'] = 'You must log in'
        return redirect('/login')







'''
Users Section
'''
@app.route('/user', methods=['GET','POST'])
def userbyid():
    u = user()
    if sessionactive(1):
        u.getAllDepartments()
        if request.args.get('delete') == 'true':
            u.deleteById(request.args.get('User_ID'))
            logger.info("user "+ str(request.args.get('User_ID'))+ " deleted")
            return redirect('/users?msg=User '+str(request.args.get('User_ID'))+' Deleted.')
        if request.form.get('User_ID') is not None:
            if request.form.get('User_ID') == '': #INSERT#user data needs to be updated
                d={}
                d['User_Email'] = request.form.get('User_Email')
                d['User_Password'] = request.form.get('User_Password')
                d['User_Password2'] = request.form.get('User_Password2')
                d['User_Last_Name'] = request.form.get('User_Last_Name')
                d['User_First_Name'] = request.form.get('User_First_Name')
                d['User_Type'] = request.form.get('User_Type')
                d['Department_ID'] = request.form.get('Department_ID')
                u = user()
                u.add(d)
                #print(u.data)
                if u.verify_insert():
                    #all form data was validated
                    u.insert()
                    logger.info("user "+ str(u.data[0]['User_ID'])+ " Created")
                    return redirect('/users?msg=User '+str(u.data[0]['User_ID'])+' created.')
                else:
                    #if there was an error with the form data
                    return render_template('users/user.html',title=f"New User ",
                    object=u.data[0],errors = u.errors,choices=u.types, deps=u.deps_list)
            else:
                u.getById(request.form.get('User_ID'))
                u.data[0]['User_Email'] = request.form.get('User_Email')
                u.data[0]['User_Password'] = request.form.get('User_Password')
                u.data[0]['User_Password2'] = request.form.get('User_Password2')
                u.data[0]['User_Last_Name'] = request.form.get('User_Last_Name')
                u.data[0]['User_First_Name'] = request.form.get('User_First_Name')
                u.data[0]['User_Type'] = request.form.get('User_Type')
                u.data[0]['Department_ID'] = request.form.get('Department_ID')
                if u.verify_update():
                    #all form data validated
                    u.update()
                    logger.info("user "+ str(u.data[0]['User_ID'])+ " updated")
                    return redirect('/users?msg=User '+str(u.data[0]['User_ID']) + ' Saved')
                else:
                    #if there was an error with form data
                    uid = request.form.get('User_ID')
                    
                    return render_template('users/user.html',title=f"User {uid}", object=u.data[0], errors=u.errors, choices=u.types, deps=u.deps_list)
                
        uid = request.args.get('User_ID')
        if uid == 'new':
            u.createBlank()
            return render_template('users/user.html',title=f"User {uid}", object=u.data[0], choices=u.types, deps=u.deps_list)
        else:
            u.getById(uid)
            return render_template('users/user.html',title=f"User {uid}", object=u.data[0], choices=u.types, deps=u.deps_list)

@app.route('/users')
def allUsers():
    if sessionactive(2):
        u = user()
        u.getAll()
        d = u.data
        return render_template('users/userTable.html',title="Users",table=d, msg=request.args.get('msg'))
    else:
        u = user()
        u.getAll()
        d = u.data
        return render_template('users/userTable2.html',title="Users",table=d, msg=request.args.get('msg'))
'''
End Users Section
'''




'''
Departments Section
'''
@app.route('/department', methods=['GET','POST'])
def depbyid():
    d = department()
    if sessionactive(1):
        d.getAllDepartments()
        if request.args.get('delete') == 'true':
            d.deleteById(request.args.get('Department_ID'))
            logger.info("department "+ str(request.args.get('Departments_ID'))+ " deleted")
            return redirect('/departments?msg=Department '+str(request.args.get('Department_ID'))+' Deleted.')
        if request.form.get('Department_ID') is not None:
            if request.form.get('Department_ID') == '': #INSERT#user data needs to be updated
                o={}
                o['Department_Type'] = request.form.get('Department_Type')
                o['Department_Name'] = request.form.get('Department_Name')
                d.add(o)
                if d.verify_insert():
                    #all form data was validated
                    d.insert()
                    logger.info("Department"+ str(d.data[0]['Department_ID'])+ " Created")
                    return redirect('/departments?msg=Department '+str(d.data[0]['Department_ID'])+' created.')
                else:
                    #if there was an error with the form data
                    return render_template('departments/department.html',title=f"New Department ",
                    object=d.data[0],errors = d.errors, deps=d.deps_list)
            else:
                d.getById(request.form.get('Department_ID'))
                d.data[0]['Department_Type'] = request.form.get('Department_Type')
                d.data[0]['Department_Name'] = request.form.get('Department_Name')
                if d.verify_update():
                    #all form data validated
                    d.update()
                    logger.info("Department "+ str(d.data[0]['Department_ID'])+ " updated")
                    return redirect('/departments?msg=Department '+str(d.data[0]['Department_ID']) + ' Saved')
                else:
                    #if there was an error with form data
                    did = request.form.get('Department_ID')
                    return render_template('departments/department.html',title=f"Department {did}", object=d.data[0], errors=d.errors, deps=d.deps_list)
        
        #view users in department
           
        did = request.args.get('Department_ID')
        if did == 'new':
            d.createBlank()
            return render_template('departments/admindepartment.html',title=f"Department {did}", object=d.data[0])
        else:
            d.getById(did)
            return render_template('departments/department.html',title=f"Department {did}", object=d.data[0], deps=d.deps_list)

@app.route('/departments')
def allDepartments():
    if sessionactive(1):
        d = department()
        d.getAll()
        o = d.data
        return render_template('departments/departmentsTable.html',title="Departments",table=o, msg=request.args.get('msg'), user_type=session.get('user')['User_Type'])
         
            
@app.route('/users_by_department')
def userByDepartment():
    if sessionactive(1):
        if request.args.get('Dep_ID') is not None:
            du = user()
            dep_id = request.args.get('Dep_ID')
            du.getByField('Department_ID',dep_id)
            dep_mems = du.data
            return render_template('users/userTable2.html',title=f"Department {dep_id} Members", table=dep_mems, user_type=session.get('user')['User_Type'])
    else:
        msg = 'You do not have access to that.'
    




'''
Reports Section
'''
@app.route('/report', methods=['GET','POST'])
def reportbyid():
    e = report()
    allUsers = user()
    allUsers = allUsers.getChoices()
    if sessionactive(1):
        if request.args.get('delete') == 'true':
            e.deleteById(request.args.get('Report_ID'))
            logger.info("Report "+ str(request.args.get('Report_ID'))+ " deleted")
            return redirect('/reports?msg=Report '+str(request.args.get('Report_ID'))+' Deleted.')
        if request.form.get('Report_ID') is not None:
            if request.form.get('Report_ID') == '': #INSERT#user data needs to be updated
                d={}
                d['File_Name'] = request.form.get('File_Name')
                d['File_Type'] = request.form.get('File_Type')
                d['ReportCreationDate'] = request.form.get('ReportCreationDate')
                d['Report_Name'] = request.form.get('Report_Name')
                d['Report_Sponsor_ID'] = request.form.get('Report_Sponsor_ID')
                d['User_ID'] = request.form.get('User_ID')
                e.add(d)

                if e.verify_insert():
                    #all form data was validated
                    e.insert()
                    logger.info("Report"+ str(e.data[0]['Report_ID'])+ " Created")
                    return redirect('/reports?msg=Report '+str(e.data[0]['Report_ID'])+' created.')
                else:
                    #if there was an error with the form data
                    
                    return render_template('reports/report.html',title=f"New Report ",
                    object=e.data[0],errors = e.errors, spons=allUsers, eid=session.get('user')['User_ID'])
            else:
                e.getById(request.form.get('Report_ID'))
                e.data[0]['File_Name'] = request.form.get('File_Name')
                e.data[0]['File_Type'] = request.form.get('File_Type')
                e.data[0]['ReportCreationDate'] = request.form.get('ReportCreationDate')
                e.data[0]['Report_Name'] = request.form.get('Report_Name')
                e.data[0]['Report_Sponsor_ID'] = request.form.get('Report_Sponsor_ID')
                e.data[0]['User_ID'] = request.form.get('User_ID')
                if e.verify_update():
                    #all form data validated
                    e.update()
                    logger.info("Report "+ str(e.data[0]['Report_ID'])+ " updated")
                    return redirect('/reports?msg=Report '+str(e.data[0]['Report_ID']) + ' Saved')
                else:
                    #if there was an error with form data
                    eid = request.form.get('Report_ID')
                    return render_template('reports/report.html',title=f"Report {eid}", object=e.data[0], errors=e.errors, spons=allUsers)

        eid = request.args.get('Report_ID')
        if eid == 'new':
            e.createBlank()
            return render_template('reports/report2.html',title=f"Report {eid}", object=e.data[0], spons=allUsers, eid=session.get('user')['User_ID'])
        else:
            e.getById(eid)
            return render_template('reports/report.html',title=f"Report {eid}", object=e.data[0], spons=allUsers, eid=session.get('user')['User_ID'])

@app.route('/reports')
def allReports():
    if sessionactive(2):
        e = report()
        #e.getAll()
        e.getByForeignKey('Reports','Users','User_ID','User_ID')
        o = e.data
        return render_template('reports/reportsTable.html',title="Report",table=o, msg=request.args.get('msg'))
    else:
        if sessionactive(1):
            user_id = session.get('user')['User_ID']
            if request.args.get('User_ID') is None:
                ruid = session.get('user')['User_ID']
                ru = report()
                #ru.getReportsForUser(ruid)
                ru.getValByFK('Reports','Users','User_ID','Report_Sponsor_ID',ruid)
                dep_mems = ru.data
                print(ru.data)
                return render_template('reports/reportsTable.html',title=f"Reports For User {ruid}", table=dep_mems, User_ID=ruid, user_type=session.get('user')['User_Type'])
        else:
            msg = 'You do not have access to that.'






'''
Events Section
'''
@app.route('/event', methods=['GET','POST'])
def eventbyid():
    e = event()
    er = event()
    er.getAllReports()
    allReports = er.data
    if sessionactive(1):
        if request.args.get('delete') == 'true':
            e.deleteById(request.args.get('Event_ID'))
            logger.info("event "+ str(request.args.get('Event_ID'))+ " deleted")
            return redirect('/events?msg=Event '+str(request.args.get('Event_ID'))+' Deleted.')
        if request.form.get('Event_ID') is not None:
            if request.form.get('Event_ID') == '': #INSERT#user data needs to be updated
                d={}
                d['Report_ID'] = request.form.get('Report_ID')
                d['Event_Date'] = request.form.get('Event_Date')
                d['Event_Status'] = request.form.get('Event_Status')
                d['User_ID'] = request.form.get('User_ID')
                e.add(d)
                #print(rep_for_user)
                if e.verify_insert():
                    #all form data was validated
                    e.insert()
                    logger.info("Event"+ str(e.data[0]['Event_ID'])+ " Created")
                    return redirect('/events?msg=Event '+str(e.data[0]['Event_ID'])+' created.')
                else:
                    #if there was an error with the form data
                    return render_template('events2/event.html',title=f"New Event ",
                    object=e.data[0],errors = e.errors, choices=e.status, reps=allReports)
            else:
                e.getById(request.form.get('Event_ID'))
                e.data[0]['Report_ID'] = request.form.get('Report_ID')
                e.data[0]['Event_Date'] = request.form.get('Event_Date')
                e.data[0]['Event_Status'] = request.form.get('Event_Status')
                e.data[0]['User_ID'] = request.form.get('User_ID')
                if e.verify_update():
                    #all form data validated
                    e.update()
                    logger.info("Event "+ str(e.data[0]['Event_ID'])+ " updated")
                    return redirect('/events?msg=Event '+str(e.data[0]['Event_ID']) + ' Saved')
                else:
                    #if there was an error with form data
                    eid = request.form.get('Event_ID')
                    return render_template('events/event.html',title=f"Event {eid}", object=e.data[0], errors=e.errors, choices=e.status, reps=allReports)

        eid = request.args.get('Event_ID')
        if eid == 'new':
            e.createBlank()
            return render_template('events/event2.html',title=f"Event {eid}", object=e.data[0], choices=e.status, reps=allReports)
        else:
            e.getById(eid)
            return render_template('events/event.html',title=f"Event {eid}", object=e.data[0], choices=e.status, reps=allReports)

@app.route('/events')
def allEvents():
    if sessionactive(2):
        e = event()
        e.getAll()
        o = e.data
        return render_template('events/eventsTable.html',title="Events",table=o, msg=request.args.get('msg'))
    else:
        if sessionactive(1):
            user_id = session.get('user')['User_ID']
            if request.args.get('User_ID') is None:
                euid = session.get('user')['User_ID']
                eu = event()
                eu.getByField("User_ID",euid)
                dep_mems = eu.data
                print(eu.data)
                return render_template('events/eventsTable.html',title=f"Events For User {euid}", table=dep_mems, User_ID=euid, user_type=session.get('user')['User_Type'])
        else:
            msg = 'You do not have access to that.'
            
            
@app.route('/report_by_event')
def reportForEvent():
    if sessionactive(1):
        if request.args.get('Report_ID') is not None:
            r = report()
            rid = request.args.get('Report_ID')
            r.getByField('Report_ID',rid)
            print(r.data)
            return render_template('reports/reportread.html',title=f"Report {rid} ", object=r.data[0])
    else:
        msg = 'You do not have access to that.'




'''
Necessary Flask Stuff
'''
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
    
if __name__ == '__main__':
    app.run(host='127.0.0.1',debug=True)


    
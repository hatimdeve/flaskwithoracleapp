import json
import cx_Oracle
from flask import Flask,request,app,jsonify,url_for,render_template,redirect,g,flash
from flask_restful import Api,Resource,reqparse
from flask_cors import CORS,cross_origin
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import pickle
import ast
from flask import session
from random import *
app=Flask(__name__)

app.config['SECRET_KEY'] = 'thisisasecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)



class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    @classmethod
    def get(cls, id):
        connection = init()
        cursor = connection.cursor()
        cursor.execute("SELECT USER_ID, USERNAME, PASSWORD FROM DBA_USERS WHERE USER_ID  = :id", {'id': id})
        result = cursor.fetchone()
        if result:
            id, username, password = result
            user = cls(id, username, password)
        else:
            user = None
        cursor.close()
        connection.close()
        return user
    def get_id(self):
        return super().get_id()

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired()], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

class sessionPool():
      def __init__(self, username, password, inf):
        self.conexion = cx_Oracle.connect(
                  username,
                password,
                inf,
                encoding = 'UTF-8' ) 

      def getsession(self):
        return self.conexion
      def destroysesion(self):
        cursor = self.conexion.cursor()
        cursor.close()
              



def init():
     username = 'sys'
     password = '123Tim456'
     dsn = 'localhost/orcl.mshome.net'
     port = 1512
     encoding = 'UTF-8'
     return   cx_Oracle.connect(
        username,
        password,
        dsn,
        encoding=encoding,mode=cx_Oracle.SYSDBA)

def getuser(user_name):
    connection=init()
    l=[]
    cursor = connection.cursor()
    cursor.execute("SELECT USERNAME, USER_ID FROM DBA_USERS WHERE USERNAME = :user_name", {':user_name': user_name})
    user, password = cursor.fetchone()
    l.append(user)
    l.append(password)
    cursor.close()
    return l
    
class Infoprof():

    def selectdata(self,connexion):
        cursor=connexion.cursor()    
        p1='select * from cheffiliere.infoprofs'
        cursor.execute(p1)
        d={'course':list(json.dumps(x) for x in cursor)}
        connexion.commit() 
        return d  

    def insertdata(self,connexion,id,NOMPROF,NBHT,SALAIRE):
        cursor=connexion.cursor()  
        p1="INSERT INTO cheffiliere.infoprofs (id, nomprof,nbht,salaire) VALUES(:1,:2,:3,:4)"
        cursor.execute(p1,(id,NOMPROF,NBHT,SALAIRE))
        connexion.commit()
        return "Data inserted successfully"  
    def delete(self,connexion,id):
        cursor=connexion.cursor()
        p1="delete from cheffiliere.infoprofs where id=:id" 
        cursor.execute(p1,{'id': id})  
        connexion.commit()
        return "Data delete successfully"    
    def upadte(self,connexion,id,NOMPROF,NBHT,SALAIRE):
        cursor=connexion.cursor()
        p1="update cheffiliere.infoprofs set nomprof=:1,nbht=:2,salaire=:3 where id=:4" 
        cursor.execute(p1,(NOMPROF,NBHT,SALAIRE,id))  
        connexion.commit()
        return "Data updated successfully" 

class course():

    def getconnection(self,score,score1):
        self.__connexion = cx_Oracle.connect(score,score1,'localhost:1521/orcl.mshome.net')
        return self.__connexion 

    def selectdata(self,connexion):
        cursor=connexion.cursor()    
        p1='select * from cheffiliere.course'
        cursor.execute(p1)
        d={'course':list(json.dumps(x) for x in cursor)}
        connexion.commit() 
        return d  

    def insertdata(self,connexion,id,nommatiere,nomprof,numheurecours,numheuretp,salle):
        cursor=connexion.cursor()  
        p1="INSERT INTO cheffiliere.course (id, nommatiere, nomprof, numheurecours, numheuretp, salle) VALUES(:1,:2,:3,:4,:5,:6)"
        cursor.execute(p1,(id,nommatiere,nomprof,numheurecours,numheuretp,salle))
        connexion.commit()
        return "Data inserted successfully"   

    def delete(self,connexion,id):
        cursor=connexion.cursor()
        p1="delete from cheffiliere.course where id=:id" 
        cursor.execute(p1,{'id': id})  
        connexion.commit()
        return "Data delete successfully"  

    def upadte(self,connexion,id,nommatiere,nomprof,numheurecours,numheuretp,salle):
        cursor=connexion.cursor()
        p1="update cheffiliere.course set nommatiere=:1,nomprof=:2,numheurecours=:3,numheuretp=:4,salle=:5 where id=:6" 
        cursor.execute(p1,(nommatiere,nomprof,numheurecours,numheuretp,salle,id))  
        connexion.commit()
        return "Data updated successfully"  

session_pool = None  

@app.route('/login',methods=['POST','GET'])     
def login():
    form = LoginForm()
    if request.method=='POST':
        username=request.form["username"]
        password= request.form["password"]
        print(username,password)
        l=getuser(username)
        userid=l[1]
        if username==l[0]:
            if password=='123':  
                p=sessionPool(username, password, 'localhost:/orcl.mshome.net')
                global session_pool
                session_pool=p.getsession()
                print(session_pool)
                new_user = User(l[1],username=form.username.data, password=form.password.data)
                login_user(new_user)
                print("hiiiiiiiiii",l[1])
                return render_template('welcome.html')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    global session_pool
    cursor = session_pool.cursor()
    cursor.close()
    logout_user()
    return redirect(url_for('login'))

@app.route('/delete/<id>/', methods=['GET', 'POST'])
@login_required
def delete(id):
    global session_pool
    error=None
    id=int(id)
    print(id,type(id))
    c=course()
    try:
       d=c.delete(session_pool,id)
       print(d)
       return redirect(url_for('table'))
    except cx_Oracle.DatabaseError as e:
        error=str(e)
        return render_template('test.html', error_msg=error)

@app.route('/delete1/<id>/', methods=['GET', 'POST'])
@login_required
def delete1(id):
    global session_pool
    id=int(id)
    print(id,type(id))
    c=Infoprof()
    d=c.delete(session_pool,id)
    print(d)
    return redirect(url_for('tableinfoprof'))  


@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    global session_pool
    c=course()
    if request.method=='POST':
        id=request.form['id']
        NomMatiere=request.form["NomMatiere"]
        NomProf= request.form["NomProf"]
        Nbheurecoure=request.form["Nbheurecoure"]
        Nbheuretp= request.form["Nbheuretp"]
        Salle= request.form["Salle"]
        d=c.upadte(session_pool,id,NomMatiere,NomProf,Nbheurecoure,Nbheuretp,Salle)
        flash("Data updated successfully ")
        return redirect(url_for('table'))
    
@app.route('/update1', methods=['GET', 'POST'])
@login_required
def update1():
    global session_pool
    c=Infoprof()
    if request.method=='POST':
        id=request.form['id']
        NOMPROF=request.form["NOMPROF"]
        NBheuretravail= request.form["NBheuretravail"]
        SALAIRE=request.form["SALAIRE"]
        print(id,NOMPROF,NBheuretravail,SALAIRE)
        d=c.upadte(session_pool,id,NOMPROF,NBheuretravail,SALAIRE)
        print(d)
        flash("Data updated successfully ")
        return redirect(url_for('tableinfoprof'))

@app.route('/welcome', methods=['GET', 'POST'])
@login_required
def welcome():
    return render_template('welcome.html')  

@app.route('/tableinfoprof',methods=['POST','GET'])    
@login_required
def tableinfoprof():
    infoprof=[]
    message=None
    global session_pool
    print(session_pool)
    cursor = session_pool.cursor()
    # Query the v$session view to get information about all active sessions
    cursor.execute("select user from dual")
    connected_users = cursor.fetchall()
    print(connected_users[0][0])
    if connected_users[0][0]=='CHEFFILIERE':
       c=Infoprof()
       d=c.selectdata(session_pool)
       for key,value in d.items():
          for i in value:
            my_list = ast.literal_eval(i)
            infoprof.append(my_list)
       return render_template('infoprof.html',data=infoprof,message=message) 
    else:
        message="vous n'avez pas le droit de voir cette table"
        return render_template('infoprof.html',data=infoprof,message=message)  

@app.route('/insert',methods=['POST','GET'])    
@login_required
def insert():
    global session_pool
    id=randint(0,38)
    c=course()
    error=None
    try:
      if request.method=='POST':
        NomMatiere=request.form["NomMatiere"]
        NomProf= request.form["NomProf"]
        Nbheurecoure=request.form["Nbheurecoure"]
        Nbheuretp= request.form["Nbheuretp"]
        Salle= request.form["Salle"]
        d=c.insertdata(session_pool,id,NomMatiere,NomProf,Nbheurecoure,Nbheuretp,Salle)
        print(d)
        flash("Data inserted successfully ")
        return redirect(url_for('table'))
    except cx_Oracle.DatabaseError as e:
        error=str(e)
        return render_template('test.html', error_msg=error)

@app.route('/insert1',methods=['POST','GET'])    
@login_required
def insert1():
    global session_pool
    id=randint(0,38)
    c=Infoprof()
    if request.method=='POST':
        NOMPROF=request.form["NOMPROF"]
        NBheuretravail= request.form["NBheuretravail"]
        SALAIRE=request.form["SALAIRE"]
        d=c.insertdata(session_pool,id,NOMPROF,NBheuretravail,SALAIRE)
        print(NOMPROF,NBheuretravail,SALAIRE)
        flash("Data inserted successfully ")
        return redirect(url_for('tableinfoprof'))
        
@app.route('/table/',methods=['POST','GET'])    
@login_required
def table():
    cour=[]
    global session_pool
    print(session_pool)
    c=course()
    d=c.selectdata(session_pool)
    for key,value in d.items():
        for i in value:
            my_list = ast.literal_eval(i)
            cour.append(my_list)
    return render_template('table.html',data=cour)


@app.route('/')
def home():
    
    return render_template('home.html')


if __name__=="__main__":
    app.run(debug=True)
    
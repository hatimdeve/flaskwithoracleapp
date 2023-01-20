import json
import cx_Oracle
from flask import Flask,request,app,jsonify,url_for,render_template,redirect
from flask_restful import Api,Resource,reqparse
from flask_cors import CORS,cross_origin
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


app=Flask(__name__)

app.config['SECRET_KEY'] = 'thisisasecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

session=None
pool=None

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


def getsession(user,psw,inf):
      l=[]
      pool = cx_Oracle.SessionPool(
                  user,
                psw,
                inf,
                min=2, max=5, increment=1 )
      conexion =pool.acquire()
      l.append(pool)
      l.append(conexion)
      return l
def endsession(conexion,pool):
    pool.release(conexion)

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

class course():
    def __init__(self,connexion):
        self.__connexion=connexion

    def getconnection(self,score,score1):
        self.__connexion = cx_Oracle.connect(score,score1,'localhost:1521/orcl.mshome.net')
        return self.__connexion 

    def selectdata(self,connexion):
        cursor=connexion.cursor()    
        p1='select * from cheffiliere.course'
        cursor.execute(p1)
        d={'course':list(json.dumps(x) for x in cursor)}
        connexion.commit()
        connexion.close()
        connexion.close()  
        return d  

    def insertdata(self,connexion):
        cursor=connexion.cursor()  
        data=request.get_json()  
        p1="INSERT INTO cheffiliere.course (id, nommatiere, nomprof, numheurecours, numheuretp, salle) VALUES(:1,:2,:3,:4,:5,:6)"
        cursor.execute(p1,(data['id'],data['nommatiere'],data['nomprof'],data['numheurecours'],data['numheuretp'],data['salle']))
        connexion.commit()
        cursor.close()
        connexion.close()
        return "Data inserted successfully"   

@app.route('/login',methods=['POST','GET'])     
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password= form.password.data
        l=getuser(username)
        userid=l[1]
        if username==l[0]:
            if password=='123':  
                new_user = User(l[1],username=form.username.data, password=form.password.data)
                login_user(new_user)
                print("hiiiiiiiiii",l[1])
                return redirect(url_for('table'))
    return render_template('test.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/table',methods=['POST','GET'])    
@login_required
def table():
    return render_template('table.html')
    '''
        userinfo=[]
    if request.method=='POST':
       user =request.form["username"]
       pasw=request.form["password"]
    return redirect(url_for('connexion',score=user,score1=pasw))  
    '''

    '''
    @app.route('/connexion/<string:score>/<string:score1>',methods=['GET'])     
def connexion(score,score1):
    f=course(0)
    e=f.getconnection(score,score1)
    return render_template('table.html',data=e)
    ''' 


@app.route('/')
def home():
    return render_template('home.html')



if __name__=="__main__":
    app.run(debug=True)
    
import json
import cx_Oracle
from flask import Flask,request,app,jsonify,url_for,render_template,redirect
from flask_restful import Api,Resource,reqparse
from flask_cors import CORS,cross_origin
app=Flask(__name__)
CORS(app)

def getconnection(score,score1):
    connection  = cx_Oracle.connect(score,score1,'localhost:1521/orcl.mshome.net')
    return connection
def selectdata():
    connection=getconnection()
    cursor=connection.cursor()    
    p1='select * from cheffiliere.course'
    cursor.execute(p1)
    return {'course':list(json.dumps(x) for x in cursor)}
    connection.commit()
    cursor.close()
    connection.close()
    
def insertdata():
    connection=getconnection()
    cursor=connection.cursor()  
    data=request.get_json()  
    p1="INSERT INTO cheffiliere.course (id, nommatiere, nomprof, numheurecours, numheuretp, salle) VALUES(:1,:2,:3,:4,:5,:6)"
    cursor.execute(p1,(data['id'],data['nommatiere'],data['nomprof'],data['numheurecours'],data['numheuretp'],data['salle']))
    connection.commit()
    cursor.close()
    connection.close()
    return "Data inserted successfully"
def updatedata():
    connection=getconnection()
    cursor=connection.cursor()    
    p1="update cheffiliere.course set nommatiere='fr' where id =1"
    cursor.execute(p1)
    connection.commit()
    cursor.close()
    connection.close()
    return "Data update successfully"    
def deleteedata():
    connection=getconnection()
    cursor=connection.cursor()    
    p1="delete from cheffiliere.course where  id =1"
    cursor.execute(p1)
    connection.commit()
    cursor.close()
    connection.close()
    return "Data delete successfully"  
@app.route('/login',methods=['POST','GET'])     
def user():
    userinfo=[]
    if request.method=='POST':
       user =request.form["username"]
       pasw=request.form["password"]
    return redirect(url_for('connexion',score=user,score1=pasw))   
@app.route('/connexion/<string:score>/<string:score1>',methods=['GET'])     
def connexion(score,score1):
    f=getconnection(score,score1)
    
    return render_template('table.html',data=f)

@app.route('/')
def home():
    return render_template('login.html')



if __name__=="__main__":
    app.run(debug=True)
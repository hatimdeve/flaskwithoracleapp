import json
import cx_Oracle
import oracledb
from flask import Flask,request,app,jsonify,url_for,render_template

app=Flask(__name__)
def getconnection():
    connection  = cx_Oracle.connect('professeu/123@localhost:1521/orcl.mshome.net')
    return connection
def selectdata():
    connection=getconnection()
    cursor=connection.cursor()    
    p1='select * from course'
    cursor.execute(p1)
    for resulat in cursor:
        return resulat[1]
    connection.commit()
    cursor.close()
    connection.close()
    return "Data slected successfully"  
def insertdata():
    connection=getconnection()
    cursor=connection.cursor()    
    p1="INSERT INTO course (id, nommatiere, nomprof, numheurecours, numheuretp, salle)VALUES (1, 'math', 'John Smith', 3, 2, 'A1')"
    cursor.execute(p1)
    connection.commit()
    cursor.close()
    connection.close()
    return "Data inserted successfully"
def updatedata():
    connection=getconnection()
    cursor=connection.cursor()    
    p1="update course set nommatiere='fr' where id =1"
    cursor.execute(p1)
    connection.commit()
    cursor.close()
    connection.close()
    return "Data update successfully"    
def deleteedata():
    connection=getconnection()
    cursor=connection.cursor()    
    p1="delete from course where  id =1"
    cursor.execute(p1)
    connection.commit()
    cursor.close()
    connection.close()
    return "Data delete successfully"       
@app.route('/')
def home():
    f=selectdata()
    return render_template('home.html',data=f)



if __name__=="__main__":
    app.run(debug=True)
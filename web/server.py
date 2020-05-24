from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
from datetime import datetime
import json
import time

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    return redirect('static/html/index.html')

@app.route('/login',methods=["POST"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    key = 'logged'
    if key in session and session[key] == [username,password]:
        return "already logged" + " " + username
    db_session = db.getSession(engine)
    respuesta = db_session.query(entities.User).filter(entities.User.username==username).filter(entities.User.password==password)
    users = respuesta[:]
    if len(users) > 0:
        session[key] = [username,password]
        return "login successful"
    return "login failed"



@app.route('/static/<content>')
def static_content(content):
    return render_template(content)

########### CRUD  users ###########Gi

# 1. CREATE
@app.route('/users', methods = ['POST'])
def create_users():
    body = json.loads(request.data)
    user = entities.User(username = body['username'], name = body['name'], fullname = body['fullname'], password = body['password'])
    db_session =  db.getSession(engine)
    db_session.add(user)
    db_session.commit()
    message = {'msg': 'User created'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    return Response(json_message, status=201, mimetype='application/json')
#1.1 Create MEssages
@app.route('/messages', methods = ['POST'])
def create_message():
    c = json.loads(request.form['values'])
    message = entities.Message(
        content = c['content'],
        sent_on = datetime.now(),
        user_from_id = c['user_from_id'],
        user_to_id = c['user_to_id']
    )
    session = db.getSession(engine)
    session.add(message)
    session.commit()
    return Response('Message Created')

# 2. READ
@app.route('/users', methods = ['GET'])
def read_user():
    db_session = db.getSession(engine)
    response = db_session.query(entities.User)
    users = response[:]
    json_message = json.dumps(users, cls=connector.AlchemyEncoder)
    return Response(json_message, status=200 ,mimetype='application/json')
# 2.1. READ M
@app.route('/messages', methods = ['GET'])
def read_message():
    db_session = db.getSession(engine)
    response = db_session.query(entities.Message)
    messages = response[:]
    json_message = json.dumps(messages, cls=connector.AlchemyEncoder)
    return Response(json_message, status=200 ,mimetype='application/json')

#3. UPADATE
@app.route('/users/<id>', methods = ['PUT'])
def update_user(id):
    #busca al usuarui
    db_session =  db.getSession(engine)
    user = db_session.query(entities.User).filter(entities.User.id == id).first()
    body = json.loads(request.data)
    #actualiza los datos
    for key in body.keys():
        setattr(user, key, body[key])
    #se guarda la actulizacion
    db_session.add(user)
    db_session.commit()
    #responde al cliente
    message = {'msg': 'User update'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    return Response(json_message, status = 201, mimetype='application/json')
@app.route('/messages',methods=['PUT'])
def update_message():
    session = db.getSession(engine)
    id = request.form['key']
    message = session.query(entities.Message).filter(entities.Message.id==id).first()
    val = json.loads(request.form['values'])
    for key in val.keys():
        setattr(message,key,val[key])
    session.add(message)
    session.commit()
    return 'Message Updated'

# 4. DELETE
@app.route('/users/<id>', methods = ['DELETE'])
def delete_user(id):
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(entities.User.id == id).first()
    db_session.delete(user)
    db_session.commit()
    #responde al cliente
    message = {'msg': 'User Deleted'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    return Response(json_message, status = 201, mimetype='application/json')

@app.route('/messages',methods=['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    message = session.query(entities.Message).filter(entities.Message.id==id).one()
    session.delete(message)
    session.commit()
    return "Message Deleted"


@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')
    message = { 'status': 404, 'message': 'Not Found'}
    return Response(json.dumps(message), status=404, mimetype='application/json')
@app.route('/messages/<id>',methods=['GET'])
def get_message(id):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).filter(entities.Message.id==id)
    for message in messages:
        js = json.dumps(message,cls=connector.AlchemyEncoder)
        return Response(js,status=200,mimetype='application/json')
    message = {'status':404,'message':'Not Found'}
    return Response(message,status=404,mimetype='application/json')

if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host=('127.0.0.1'))

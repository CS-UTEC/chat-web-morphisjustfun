from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
from datetime import datetime
import json
import time
import threading

from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.protocol_version = "HTTP/1.1"

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)
cache = {}
key_users = 'keyuser'
key_messages = 'keymessages'
lock = threading.Lock()
locku = threading.Lock()

@app.route('/',methods=['GET'])
def index():
    return redirect('static/html/index.html')

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)

@app.route('/logout',methods=['GET'])
def logout():
    del session['logged']
    del session['idk']
    return redirect('/')

def assign(key,value):
    session[key] = value


@app.route('/login',methods=["POST"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    key = 'logged'
    if key in session and session[key] == [username,password]:
        return redirect('static/html/chat.html')
    db_session = db.getSession(engine)
    respuesta = db_session.query(entities.User).filter(entities.User.username==username).filter(entities.User.password==password)
    users = respuesta[:]
    idk = respuesta[0].id
    if len(users) > 0:
        assign(key,[username,password])
        assign('idk',idk)
        db_session.close()
        return redirect('static/html/chat.html')
    db_session.close()
    return "login failed"

@app.route('/current', methods = ['GET'])
def current():
    db_session = db.getSession(engine)
    response = db_session.query(entities.User).filter(entities.User.id==session['idk'])
    users = response[:]
    json_message = json.dumps(users, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status=200 ,mimetype='application/json')

#-------------CRUD USERS --------------#
#GET - with cache
@app.route('/users', methods = ['GET'])
def read_user():
    users = []
    locku.acquire()
    if key_users in cache and (datetime.now()-cache[key_users]['datetime']).total_seconds() < 10:
        users = cache[key_users]['data']
    else:
        db_session = db.getSession(engine)
        response = db_session.query(entities.User)
        users = response[:]
        now = datetime.now()
        cache[key_users] = {'data':users,'datetime':now}
        db_session.close()
    json_message = json.dumps(users, cls=connector.AlchemyEncoder)
    locku.release()
    return Response(json_message, status=200 ,mimetype='application/json')
#GET with ID
@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')
    message = { 'status': 404, 'message': 'Not Found'}
    db_session.close()
    return Response(json.dumps(message), status=404, mimetype='application/json')
#CREATE
@app.route('/users', methods = ['POST'])
def create_users():
    body = json.loads(request.data)
    user = entities.User(username = body['username'], name = body['name'], fullname = body['fullname'], password = body['password'])
    db_session =  db.getSession(engine)
    db_session.add(user)
    db_session.commit()
    message = {'msg': 'User created'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status=201, mimetype='application/json')
#DELETE with ID
@app.route('/users/<id>', methods = ['DELETE'])
def delete_user(id):        
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(entities.User.id == id).first()
    db_session.delete(user)
    db_session.commit()
    #responde al cliente
    message = {'msg': 'User Deleted'}
    json_message = json.dumps(message, cls=connector.AlchemyEncoder)
    db_session.close()
    return Response(json_message, status = 201, mimetype='application/json')
#UPDATE with ID
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
    db_session.close()
    return Response(json_message, status = 201, mimetype='application/json')

#-------------CRUD MESSAGES --------------#
#GET --- with cache
@app.route('/messages', methods = ['GET'])
def read_message():
    messages = []
    json_message = ''
    lock.acquire()
    if key_messages in cache and (datetime.now()-cache[key_messages]['time']).total_seconds()<10:
        messages = cache[key_messages]['data']
        json_message = json.dumps(messages, cls=connector.AlchemyEncoder)
    else:
        db_session = db.getSession(engine)
        response = db_session.query(entities.Message)
        messages = response[:]
        newmessage = []
        for x in messages:
            mex = {}
            mex['id'] = x.id
            mex['content'] = x.content
            mex['user_from_id'] = x.user_from_id
            mex['user_to_id'] = x.user_to_id
            try:
                mex['sent_on'] = x.sent_on.strftime("%m/%d/%Y  %H:%M:%S")
            except:
                mex['sent_on'] = 0
            newmessage.append(mex)
        cache[key_messages] = {'data': newmessage, 'time': datetime.now()}
        json_message = json.dumps(newmessage, cls=connector.AlchemyEncoder)
        db_session.close()
    lock.release()
    return Response(json_message, status=200 ,mimetype='application/json')
#GET with ID
@app.route('/messages/<id>',methods=['GET'])
def get_message(id):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).filter(entities.Message.id==id)
    for message in messages:
        js = json.dumps(message,cls=connector.AlchemyEncoder)
        return Response(js,status=200,mimetype='application/json')
    message = {'status':404,'message':'Not Found'}
    db_session.close()
    return Response(message,status=404,mimetype='application/json')
#UPDATE
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
#DELETE
@app.route('/messages',methods=['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    message = session.query(entities.Message).filter(entities.Message.id==id).one()
    session.delete(message)
    session.commit()
    return "Message Deleted"
#CREATE
@app.route('/messages', methods = ['POST'])
def create_message():
    c = (request.form['values'])
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
#CRETE to ID
@app.route('/messages/<user_to_id>', methods = ['POST'])
def create_message2(user_to_id):
    ida = str(session['idk'])
    c = request.form.get('content')
    message = entities.Message(
        content = c,
        sent_on = datetime.now(),
        user_from_id = ida,
        user_to_id = user_to_id
    )
    session2 = db.getSession(engine)
    session2.add(message)
    session2.commit()
    return redirect('http://localhost:8080/static/html/chat.html')




@app.route('/get_chat/<user_to_id>',methods=['GET'])
def get_chat(user_to_id):
    ida = str(session['idk'])
    if ida!=user_to_id:
        db_session = db.getSession(engine)
        messages = db_session.query(entities.Message).filter(entities.Message.user_from_id == ida).filter(
            entities.Message.user_to_id == user_to_id)
        data = messages[:]
        messages2 = db_session.query(entities.Message).filter(entities.Message.user_from_id == user_to_id).filter(
            entities.Message.user_to_id == ida)
        data2 = messages2[:]
        data = data + data2
        db_session.close()
        return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')
    else:
        db_session = db.getSession(engine)
        messages = db_session.query(entities.Message).filter(entities.Message.user_from_id == ida).filter(
            entities.Message.user_to_id == user_to_id)
        data = messages[:]
        db_session.close()
        return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host=('127.0.0.1'))



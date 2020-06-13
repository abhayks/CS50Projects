import os
import time
from flask import Flask , session, flash, render_template, request, redirect, url_for,  jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room


app = Flask(__name__)
app.config["SECRET_KEY"] = "Development"
socketio = SocketIO(app)
app.debug = True
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Add a list for all user & Channels
users=[]
channels = []
# The messages will be a dictionary 
# Format 
# Channel: <Channel_name>
# User   : <user_name>
# message: <actual_message>
# time   : <message_time>   
messages = {}

def foramt_message(channel, user, message, time):
    messagestr="message : "+message+ " user : " + user + " time : " + time
    messages[channel].append(messagestr)
    # As per project requirements, store only 100 messages
    if len(messages[channel]) > 100:
        messages[channel].pop(0)
    return messagestr


@app.route("/" , methods=['GET', 'POST'])
def index():
    if session.get('logged_in'):
        print(session.get('username'))
        return render_template('index.html', username=session['username'])
    else:
        print('Not logged in')
    if(request.method == 'POST'):
        username=request.form['inputusername']
        print (username)
        if username in users:
            flash('Username taken, please enter another')
        else:
            users.append(username)
            session['username']=username
            session['logged_in']=True
            return render_template('index.html', username=session['username'])
    return render_template('signin.html')

@socketio.on("request-all-rooms")
def showrooms():
    print('In request, sending channels back')
    print(channels)
    emit("connected", session['username'])
    emit("show-all-rooms", channels)

@socketio.on("create-channel")
def createChannel(channel):
    if channel in channels:
    # retund non- success
        emit("error", "Channel exists")
    else:
        channels.append(channel)
        messages[channel]=[]
        emit("message", "Channel '"+channel+"' created!", broadcast=True)
        emit("show-all-rooms", channels, broadcast=True)

@socketio.on("join-channel")
def join_channel(channel):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    # TODO :: Only join if the channel existys in channels
    if channel in channels:
        join_room(channel)
        emit('join-accepted', channel)
        msgstr=session.get('username') + " has joined room"
        print("Message string = " + msgstr)
        emit("broadcast-to-channels", msgstr, room=channel)

@socketio.on("leave-channel")
def leave_channel(channel):
    leave_room(channel)
    msgstr=session.get('username') + " has Left room"
    print("Leave Channel Message string = " + msgstr)
    emit("broadcast-to-channels", msgstr, room=channel)    

@socketio.on("send-message")
def send_message(data):
    mtime = time.ctime(time.time())
    message = {"username": session.get('username'), "msg" : data["msg"], "mtime": mtime}
    messages[data["channel"]].append(message)
    print(data)
    emit("receive-message", message, room=data["channel"]) 

if __name__ == "__main__":
	socketio.run(app, debug = True)

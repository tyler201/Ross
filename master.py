from bottle import get, post, request, Bottle, abort, static_file, redirect, response
from gevent import Timeout
import threading
import downloader
import player
import time
import os

skipped = False
time_to_wait = 0.1
app = Bottle()
playlist = []
idlist = []
volume = 100

def check_login(u, p):
    u = str(u)
    p = str(p)
    if u == "PyRo":
        if p == "flamingo":
            return True
        else:
            pass
    else:
        pass

def playerthread():
    while True:
        try:
            currentsong = playlist[0]
            currentid = idlist[0]
            player.playtrack(currentid, currentsong)
            playlist.remove(currentsong)
            idlist.remove(currentid)
        except IndexError:
            pass

def skipcheck():
    while 1<2:
        global skipped
        if skipped == True:
            skipped = False
        time.sleep(1)

def downloadthread(url, *args):
    try:
        songtitle, songid = downloader.download(url)
        playlist.append(songtitle)
        idlist.append(songid)
    except downloader.SongExists:
        print("Song already been downloaded, skipping.")


threadymcthreaderson = threading.Thread(target=playerthread)
threadymcthreaderson.start()

skipthread = threading.Thread(target=skipcheck)
skipthread.start()

@app.get('/admin-login')  # or @route('/login')
def login():
    logged = request.get_cookie("logged-in")
    if logged == "yes":
        redirect("/admin-panel")
    else:
        return '''
            <head>  
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
            </head>
            <title>ROSS Login</title>
            <div class="container">
                <div class="col-lg-4"></div>
                <div class="col-lg-4">
                     <div class="jumbotron text-center" style="margin-top:150px">
                          <h1>ROSS Login</h1>
                          <form action="/login" method="post">
                          <div class="form-group">
                              <input name="username" placeholder="Username" class="form-control" type="text" />
                          </div>
                          <div class="form-group">
                              <input name="password" placeholder="Password" class="form-control" type="password" />
                          </div>
                          <button type="submit" class="btn btn-primary form-control">Login</button>
                        </form>
                     </div>
                </div>
                <div class="col-lg-4"></div>
            </div>
        '''

@app.post('/login')  # or @route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if check_login(username, password):
        response.set_cookie("logged-in", "yes")
        redirect("/admin-panel")
    else:
        redirect("/home")

@app.get("/admin-panel")
def panel():
    if request.get_cookie("logged-in") == "yes":
        return static_file("admin.html", root=".")

@app.post("/admin-panel")
def panelpost():
    global skipped
    global volume
    if request.get_cookie("logged-in") == "yes":
        func = request.forms.get('function')
        if func == "Skip":
            skipped = True
            print("Skipping...")
        elif func == "Set volume":
            volume = request.forms.get('volume')
            print(volume)
        elif func.split(" ")[0] == "Skip":
            print(func.split(" ")[1])
            playlist.pop(int(func.split(" ")[1]))
            filename = idlist[int(func.split(" ")[1])] + ".wav"
            os.remove(filename)
            idlist.pop(int(func.split(" ")[1]))
        elif func.split(" ")[0] == "Blacklist":
            print(func.split(" "))
            if func.split(" ")[1] == "0":
                print("First")
                skipped = True
            else:
                print("Not first")
                playlist.pop(int(func.split(" ")[1]))
                filename = idlist[int(func.split(" ")[1])] + ".wav"
                os.remove(filename)
                idlist.pop(int(func.split(" ")[1]))
            blacklistfile = open("config/blacklist.txt", "a")
            video_id = idlist[int(func.split(" ")[1])]
            url = downloader.get_url(video_id)
            blacklistfile.write(url + "\n")
            blacklistfile.close()
    redirect("/admin-panel")

class TooLong(Exception):
    pass

@app.route('/websocket')
def handle_websocket():
    global playlist
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')
    print("Connection made.")
    message = ""
    num = 0
    for x in playlist:
        if num == 0:
            message = message + x
        else:
            message = message + "\n" + x
        num = num + 1
    wsock.send(message)
    while 1 < 2:
        try:
            with Timeout(time_to_wait, TooLong):
                wsock.receive()
                print("Connection Dead.")
                break
        except TooLong:
            try:
                message = ""
                num = 0
                for x in playlist:
                    if num == 0:
                        message = message + x
                    else:
                        message = message + "\n" + x
                    num = num + 1
                wsock.send(message)
            except WebSocketError:
                print("Connection closed.")
                break

@app.get('/home')
def homepage():
    return static_file("index.html", root=".")

@app.post('/request')
def request_song():
    url = request.forms.get("link")
    if url != "":
        dlthread = threading.Thread(target=downloadthread, args={url : url})
        dlthread.start()
    if request.get_cookie("logged-in") == "yes":
        redirect("/admin-panel")
    else:
        redirect("/home")

@app.get('/')
def begin():
    response.set_cookie("logged-in", "no")
    redirect("/home")

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
server = WSGIServer(("127.0.0.1", 8080), app,
                    handler_class=WebSocketHandler)
print("Running server...")
server.serve_forever()
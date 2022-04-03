from flask import Flask, request, json
from flask import render_template

app = Flask(__name__)
app.debug = True



@app.route("/")
def home():
    return render_template('index.html')

@app.route("/Register")
def Register():
    return render_template('Register.html')

@app.route("/signin", methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    if username and password:
        if validateUser(username, password):
            print("Log in as " + username + ", " + password)
            return render_template('Main.html')


@app.route("/register", methods=['POST'])
def register():
    print("this is a test")
    username = request.form['username']
    password = request.form['password']
    cpassword = request.form['Cpassword']
    if request.method == 'POST' and cpassword == password:
        with open('nopol.txt', 'a') as f:
            print("writing")
            txt1 = "{fname}:{password}:".format(fname=username, password=password)
            f.write(txt1)

    return render_template('index.html')

def validateUser(username, password):
    f = open('nopol.txt')
    l = []
    i = 0
    for line in f:
        l = line.split(":")
        if username == l[i] and password == l[i + 1]:
            return True
        i += 2

    return False
    


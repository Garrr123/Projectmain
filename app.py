from flask import Flask, request, json
from flask import render_template

app = Flask(__name__)
app.debug = True



@app.route("/")
def home():
    return render_template('index.html')

@app.route("/Log_In")
def LogIn():
    return render_template('Log_In.html')

@app.route("/Register")
def Register():
    return render_template('Register.html')

@app.route("/signin", methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    if username and password:
        if validateUser(username, password):
            return render_template('MainPage.html')


@app.route("/register", methods=['POST'])
def register():
    print("this is a test")
    username = request.form['username']
    password = request.form['password']
    cpassword = request.form['Cpassword']
    if request.method == 'POST' and cpassword == password:
        with open('nopol.txt', 'w') as f:
            print("writing")
            txt1 = "{fname}:{password}".format(fname=username, password=password)
            f.write(txt1)

    return render_template('Index.html')

def validateUser(username, password):
    f = open('nopol.txt')
    l = []
    for line in f:
        l = line.split(":")
        if username == l[0] and password == l[1]:
            return True

    return False
    


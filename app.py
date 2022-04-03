from flask import Flask, request, json
from flask import render_template
from AppObjects import *
import random

random.seed(42)

app = Flask(__name__)
app.debug = True

customer_list = []
driver_list = []
journey_list = []
transaction_No = 0
amk_graph = {}
journey_dict = {}


def setup():
    global amk_graph
    global driver_list
    global customer_list
    amk_graph = AMK_Graph()
    with open('customer.txt', 'r') as f:
        line = f.readline()
        line = f.readline()
        while(line != ""):
            id, name = line.split(',')
            customer_list.append(Customer(id, name) )
            line = f.readline()
    with open('drivers.txt.txt', 'r') as f:
        line = f.readline()
        line = f.readline()
        while(line != ""):
            id,name,license_plate,cartype,seats,luggage_limit = line.split(',')
            location = list(amk_graph.nodes_dict.keys())[random.randint((0,len(amk_graph)+ 1))]
            driver_list.append(Driver(id,name,license_plate,cartype,location,seats,luggage_limit) )
            line = f.readline()

setup()
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
        with open('customer.txt', 'a') as f:
            print("writing")
            txt1 = "{fname}:{password}:".format(fname=username, password=password)
            f.write(txt1)

    return render_template('index.html')

def validateUser(username, password):
    f = open('customer.txt')
    l = []
    i = 0
    for line in f:
        l = line.split(":")
        if username == l[i] and password == l[i + 1]:
            return True
        i += 2

    return False
    


def book():
    global transaction_No
    transaction_No += 1

    return

def cancel(journey_id):
    return

def complete(journey_id):
    return


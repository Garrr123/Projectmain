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
journey_No = 0
amk_graph = {}
journey_dict = {}
busy_customer = []
busy_driver = []
sharing_journey = []
lone_journey = []


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
            customer_list.append(Customer(id, name))
            line = f.readline()
    with open('drivers.txt', 'r') as f:
        line = f.readline()
        line = f.readline()
        while(line != ""):
            id,name,license_plate,cartype,seats,luggage_limit = line.split(',')
            location = list(amk_graph.nodes_dict.keys())[random.randint(0,len(amk_graph.nodes_dict))]

            driver_list.append(Driver(id,name,license_plate,cartype,location,seats,luggage_limit) )
            line = f.readline()

setup()
@app.route("/")
def home():
    return render_template('main.html')



def book(user_id ,start, end ,cartype,seats = 1 , luggage_req =0 , sharing = False ,distance_limit = 300):
    global journey_No
    global driver_list
    global customer_list
    global busy_customer
    global busy_driver
    global amk_graph
    global sharing_journey
    global lone_journey
    booking = Booking(user_id ,start, end ,cartype,seats , luggage_req , sharing ,distance_limit )
    ##if sharing:

    start_lat_long = getLat_Long(api_Search(start))
    end_lat_long = getLat_Long(api_Search(end))
    if start_lat_long is None or end_lat_long is None:
        return False

    ## looking for drivers that fit
    fit_drivers = []
    for i in driver_list:
        if booking.car_fit(i):
            fit_drivers.append(i)

    if len(fit_drivers) == 0:
        return False
    closest_driver = None
    shortest_dist = 999999999
    lat_start, lng_start = float(start_lat_long['lat']), float(start_lat_long['long'])

    ## Find nearest driver
    for j in fit_drivers:
        lat_driver, lng_driver = [ float(x) for x in j.location.split(',')]
        dist = distance(lat_driver, lng_driver, lat_start, lng_start ) * 1000
        if dist < shortest_dist:
            closest_driver = j
            shortest_dist = dist

    ## Find path
    path = amk_graph.findpath(start, end)
    ## Get path map
    map = get_route_map(path,
                        [amk_graph.get_nearest_node(start)],
                        amk_graph.get_nearest_node(end))

    time = amk_graph.get_path_distance(path)
    dist = amk_graph.get_path_duration(path)
    trip  = Journey(journey_No,booking, closest_driver.id,closest_driver.seats - seats,path
                                ,map,dist,time, closest_driver.seats -seats )
    if sharing:
      sharing_journey.append(trip)
    else:
      lone_journey.append(trip)
    journey_No += 1

    return True

def complete(journey_id):
    return


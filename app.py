from flask import Flask, request, json
from flask import render_template
from AppObjects import *
import random


random.seed(42)

app = Flask(__name__)
app.debug = True

customer_dict = {}
driver_dict  = {}
journey_dict  = {}
journey_No = 0
amk_graph = {}
busy_customer = {}
busy_driver = {}
sharing_journey = {}
lone_journey = {}
token = None


def setup():
    global amk_graph
    global driver_dict
    global customer_dict
    global token
    token = api_getToken()
    amk_graph = AMK_Graph()
    with open('customer.txt', 'r') as f:
        line = f.readline()
        line = f.readline()
        while(line != ""):
            id, name = line.split(',')
            customer_dict[id] = Customer(id,name.strip())
            line = f.readline()
    with open('drivers.txt', 'r') as f:
        line = f.readline()
        line = f.readline()
        while(line != ""):
            id,name,license_plate,cartype,seats,luggage_limit = line.split(',')
            location = list(amk_graph.nodes_dict.keys())[random.randint(0,len(amk_graph.nodes_dict))]
            location = api_reverse_latLong(location, token)
            driver_dict[id] = Driver(id,name,license_plate,cartype,location,seats,luggage_limit)
            line = f.readline()

setup()
@app.route("/" , methods=['GET'])
def home():
    return render_template('main.html', user = customer_list , driver = driver_list)

@app.route('/RenderPage', methods=['POST' , 'GET'])
def RenderPage():
    User_Info = request.form.get("UserInfo")
    case = 0
    if request.method == 'POST':
        if request.form['MainPButton'] == 'Book':
            case = 1
        elif request.form['MainPButton'] == 'Journey':
            case = 2
        elif request.form['MainPButton'] == 'Book':
            case = 3
        elif request.form['MainPButton'] == 'Empty':
            case = 4

    if case == 1:
        return render_template('Book.html', Pass=User_Info) # Pass will be the objetct getting from the html
    elif case == 2:
        return render_template('Journey.html' , Pass = User_Info)
    elif case == 3:
        return render_template('Transaction.html' , Pass = User_Info)
    elif case == 4:
        return render_template('Empty.html' , Pass = User_Info)

@app.route("/Booking", methods=['POST'])
def BookPage():
    return render_template('Main.html')


def book(user_id, start, end, cartype, seats=1, luggage_req=0, sharing=False, distance_limit=300):
    global journey_No
    global driver_dict
    global customer_dict
    global busy_customer
    global busy_driver
    global amk_graph
    global sharing_journey
    global lone_journey
    booking = Booking([user_id], [start], end, cartype, seats, luggage_req, sharing, distance_limit)
    ##if sharing:

    start_lat_long = amk_graph.get_nearest_node(start)
    end_lat_long = getLat_Long(api_Search(end))
    if start_lat_long is None or end_lat_long is None:
        print(start_lat_long, end_lat_long)
        return False

    ## looking for drivers that fit
    fit_drivers = []
    for i in driver_dict.values():
        if booking.car_fit(i):
            fit_drivers.append(i)

    if len(fit_drivers) == 0 and sharing is False:
        print("no match")
        return False

    closest_driver = None
    shortest_dist = 999999999
    lat_start, lng_start = start_lat_long.split(',')

    ## Find nearest driver
    time = None
    trip = None
    dist = None
    if len(fit_drivers) > 0:
        for j in fit_drivers:
            lat_driver, lng_driver = [float(x) for x in amk_graph.get_nearest_node(j.location).split(',')]
            dist = distance(lat_driver, lng_driver, float(lat_start), float(lng_start)) * 1000
            if dist < shortest_dist:
                closest_driver = j
                shortest_dist = dist

        ## Find path
        path = amk_graph.findpath(start, end)
        driver_start = amk_graph.findpath(closest_driver.location, start)
        driver_start.pop()
        combined_path = driver_start + path
        ## Get path map
        map = get_route_map(combined_path,
                            [amk_graph.get_nearest_node(closest_driver.location),
                             amk_graph.get_nearest_node(start)],
                            amk_graph.get_nearest_node(end))

        # Get journey distance and time
        time = amk_graph.get_path_distance(path)
        dist = amk_graph.get_path_duration(path)

        # create journey
        trip = Journey(journey_No, booking, closest_driver.id, closest_driver.seats - seats, path
                       , map, dist, time, closest_driver.location, closest_driver.luggage_weight - luggage_req)

        # Pop out the user and driver , store them in respective busy list
        if sharing is False:
            busy_customer[user_id] = customer_dict.pop(user_id)
            busy_driver[closest_driver.id] = driver_dict.pop(closest_driver.id)

    ## Increment jorurney_No
    journey_No += 1
    # Store jorney in a list based on Sharing type
    journey_choice = [trip]
    if sharing:
        sj_Exist = False
        for sj in sharing_journey.values():
            if booking.car_fit(sj):
                print("one  pass")
                ## check if distance from end is within limit
                sj_end_node = amk_graph.get_nearest_node(sj.end).split(',')
                book_end_latlong = getLat_Long(api_Search(end))
                dist_check = distance(float(sj_end_node[0]), float(sj_end_node[1]),
                                      float(book_end_latlong['lat']), float(book_end_latlong['long']))
                if dist_check * 1000 > distance_limit:
                    print("fail dist check")
                    continue
                ## Check if new shared journey is 2 times more time to complete
                shortest_shared = shortest_shared_path(sj.driver_location, sj.start + [start],
                                                       sj.end, amk_graph)
                if time is not None:
                    if shortest_shared[0] > time * 2 or shortest_shared[0] > sj.time * 2:
                        print("fail time check 1")
                        continue

                    if shortest_shared[0] - time > 900 or shortest_shared[0] - sj.time > 900:
                        print("fail time check 2")
                        continue

                if start not in sj.start:
                    booking.start = sj.start + [start]

                dist = amk_graph.get_path_distance(shortest_shared[1])
                start_nodes = set([amk_graph.get_nearest_node(i) for i in booking.start])
                map = get_route_map(shortest_shared[1],
                                    [amk_graph.get_nearest_node(sj.driver_location)] + [amk_graph.get_nearest_node(i)
                                                                                        for i in booking.start],
                                    amk_graph.get_nearest_node(sj.end))
                booking.user_id = sj.user_id + [user_id]
                booking.start = sj.start + [start]
                journey = Journey(journey_No, booking, sj.driver_id, sj.seats - seats
                                  , shortest_shared[1], map, dist, shortest_shared[0]
                                  , sj.driver_location, sj.luggage_weight - luggage_req)
                print("Here")
                journey_choice.append(journey)
                sj_Exist = True

        if sj_Exist:
            print("have SJ")
            return journey_choice
        elif len(fit_drivers) > 0:
            print("no sj but have driver")
            busy_customer[user_id] = customer_dict.pop(user_id)
            busy_driver[closest_driver.id] = driver_dict.pop(closest_driver.id)

            sharing_journey[trip.id] = trip
            return True
        else:
            print("no driver")
            return False

    else:
        lone_journey[trip.id] = trip

    print("end")
    return True

def complete(journey_id, sharing):
  global driver_dict
  global customer_dict
  global busy_customer
  global busy_driver
  global sharing_journey
  global lone_journey
  global amk_graph
  global token

  journey = None

  if sharing:
    journey = sharing_journey.pop(journey_id)
  else :
    journey = lone_journey.pop(journey_id)

  if journey == None:
    return False

  for i in journey.user_id:
    customer_dict[i] = busy_customer.pop(i)

  driver_dict[journey.driver_id] = busy_driver.pop(journey.driver_id)
  driver_dict[journey.driver_id].location = api_reverse_latLong(amk_graph.get_nearest_node(journey.end), token)


  return True

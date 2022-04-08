from flask import Flask, request, json, flash
from flask import render_template

from AppObjects import *
import random


random.seed(42)

app = Flask(__name__)
app.debug = True

customer_dict = {}
driver_dict  = {}
journey_No = 0
amk_graph = {}
busy_customer = {}
busy_driver = {}
sharing_journey = {}
lone_journey = {}
token = None
journey_choice = []

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
    return render_template('main.html')

@app.route("/gotoBook")
def gotoBook():
    global driver_dict
    global customer_dict
    return render_template('Book.html' , user = customer_dict , driver = driver_dict)

@app.route("/gotoTransaction")
def gotoTransaction():
    global driver_dict
    global customer_dict
    return render_template('Transaction.html')

@app.route("/gotoJourney", methods=['POST' ,'GET'])
def gotoJourney():

    global sharing_journey
    global lone_journey

    rideType = request.form.get("RideType")
    if rideType == "1":
        return render_template('Journey.html', rideType ="1",journey_dict = sharing_journey )
    else:
        return render_template('Journey.html', rideType="0", journey_dict=lone_journey)

@app.route("/gotoEmpty")
def gotoEmpty():

    global driver_dict
    global customer_dict

    return render_template('Empty.html')

@app.route("/completeSharing" , methods=['POST'])
def completeSharing():

    global sharing_journey
    global lone_journey
    journey_id = request.form.get("complete_journey")
    complete(int(journey_id), True)

    return render_template('Journey.html', rideType="1", journey_dict=sharing_journey)


@app.route("/completeLone", methods=['POST'])
def completeLone():

    global sharing_journey
    global lone_journey
    journey_id = request.form.get("complete_journey")
    complete(int(journey_id), False)
    return render_template('Journey.html', rideType="0", journey_dict=lone_journey )

@app.route("/viewSharing", methods=['GET'])
def viewSharing():
    global busy_driver
    global busy_customer
    global sharing_journey
    journey_id = request.form.get("view_journey")
    journey = displayJourney(journey_id, sharing_journey)
    return render_template('journeyDetails.html', rideType="1", journey=journey)

@app.route("/viewLone", methods=['GET'])
def viewLone():
    global busy_driver
    global busy_customer
    global lone_journey
    journey_id = request.form.get("view_journey")

    journey = displayJourney(journey_id,lone_journey)


    return render_template('journeyDetails.html', rideType="0", journey=journey)

@app.route("/Booking", methods=['POST', 'GET'])
def BookPage():
    global lone_journey
    global journey_No
    global driver_dict
    global customer_dict
    global busy_customer
    global busy_driver
    global amk_graph
    global sharing_journey
    global lone_journey
    global journey_choice

    name = request.form.get("info")
    field = request.form.get("Field")
    S_Location = request.form.get("SLocation")
    E_Location = request.form.get("Elocation")
    Luggage_Size = request.form.get("LuggageSize")
    Limit = request.form.get("DistanceLimit")
    Car_Type = request.form.get("CarType")
    Sharable = request.form.get("Sharable")
    Seat_Number = request.form.get("Seat")


    print(name ,field, S_Location, E_Location, Luggage_Size, Limit, Car_Type, Sharable,Seat_Number)
    print("Thank you")
    sharing = True if Sharable == "Y" else False
    Limit = 300.0 if Limit == "" else float(Limit)
    Luggage_Size = 0.0 if Luggage_Size == "" else float(Luggage_Size)
    results = book( name, S_Location, E_Location, Car_Type, int(Seat_Number), Luggage_Size, sharing , Limit)



    if isinstance(results, bool):
        if sharing and results:
            ## POP UP Here

            #your table is formed from journey_choice , a global list
            ## journey.user_id[-1] , this is the latest customer id , use this to get customer name from  customer dict
            ## journey.driver_id, the driver id , use this to get driver name from busy driver dict
            ## start from index 1 of the list
            ## the accept button value is the list index
            ## The amount of rows is len(journey_choice) -1 .
            """
            for i in journey_choice[1:]:
                customer_name = customer_dict[i.user_id[-1]]
                driver_name = busy_driver[i.driver_id]
                print(customer_name ,driver_name , "accept " )
            """


            return render_template('Main.html')
    else:
        ## errors
        print(results)
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
    global journey_choice

    booking = Booking([user_id], [start], end, cartype, seats, luggage_req, sharing, distance_limit)
    ##if sharing:

    start_lat_long = amk_graph.get_nearest_node(start)
    end_lat_long = getLat_Long(api_Search(end))
    if start_lat_long is None or end_lat_long is None:
        print(start_lat_long, end_lat_long)
        return "Invalid Start or End Address"

    ## looking for drivers that fit
    fit_drivers = []
    for i in driver_dict.values():
        if booking.car_fit(i):
            fit_drivers.append(i)

    if len(fit_drivers) == 0 and sharing is False:
        print("no match")
        return "No Available cars"

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
            return True
        elif len(fit_drivers) > 0:
            print("no sj but have driver")
            busy_customer[user_id] = customer_dict.pop(user_id)
            busy_driver[closest_driver.id] = driver_dict.pop(closest_driver.id)

            sharing_journey[trip.id] = trip
            return True
        else:
            return "No available drivers"

    else:
        print(trip.id)
        lone_journey[trip.id] = trip

    print("end")
    return True

def displayJourney(id,journey_dict):

    selected = journey_dict[int(id)]
    journey = {}
    sentence = ",".join([busy_customer[i].name for i in selected.user_id])
    journey['journey_id'] = selected.id
    journey["customer"] = sentence
    journey['driver_name'] = busy_driver[selected.driver_id].name
    journey['driver_id'] = selected.driver_id
    journey['cartype'] = selected.cartype
    journey['start'] = selected.start
    journey['end'] = selected.end
    journey['sharing'] = selected.sharing
    journey['luggage_weight'] = selected.luggage_weight
    journey['seats'] = selected.seats
    journey['seats'] = selected.map
    journey['driver_location'] = selected.driver_location
    journey['distance'] = selected.dist
    journey['time'] = selected.time
    return journey


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

def sharing_choice(index):
  global journey_choice
  global sharing_journey
  journey =journey_choice[index]
  if index == 0:
    if journey is not None:
      busy_customer[journey.user_id[-1]] = customer_dict.pop(journey.user_id[-1])
      busy_driver[journey.driver_id] = driver_dict.pop(journey.driver_id)
      sharing_journey[journey.id] = journey_choice[0]
  else:
    for i in sharing_journey.values():
      if i.driver_id == journey.driver_id:
        sharing_journey.pop(i.id)
    sharing_journey[journey.id] = journey


  return True
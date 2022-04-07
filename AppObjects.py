from AMK_Graph import *
class Customer:
    def __init__(self, user_id, name):
        self.name = name
        self.user_id = user_id


class Driver:
    def __init__(self,id , name , license_plate ,cartype, location, seats = 4  ,Luggage_limit =20  ):
        self.id = id
        self.name = name
        self.cartype = cartype
        self.seats = int(seats)
        self.location = location
        self.luggage_weight =float(Luggage_limit)
        self.license_plate  = license_plate
    def display(self):
        print("id",self.id )
        print("name",self.name )
        print("cartype",self.cartype )
        print("seats", self.seats)
        print("seats", self.seats)
        print("location",self.location )
        print("luggage_weight",self.luggage_weight )
        print("license_plate",self.license_plate)


class Booking:
    def __init__(self,user_id ,start, end ,cartype,seats = 1 , luggage_req =0 , sharing = False ,distance_limit = 300):
        self.cartype = cartype
        self.user_id = user_id
        self.start = start
        self.end  = end
        self.sharing = bool(sharing)
        self.luggage_weight = float(luggage_req)
        self.distance_limit = float(distance_limit)
        self.seats = int(seats)

    def display(self):
        print("cartype",self.cartype )
        print("user_id",self.user_id )
        print("start",self.start )
        print("end",self.end  )
        print("sharing",self.sharing )
        print("luggage_weight",self.luggage_weight )
        print("distance_limit",self.distance_limit)
        print("seats",self.seats )

    def car_fit(self, comparison):
        if self.cartype == comparison.cartype:
            if self.luggage_weight <= comparison.luggage_weight:
                if self.seats <= comparison.seats:
                    return True
        return False





class Journey:
    def __init__(self ,id ,booking,driver_id,  seats,path ,map ,distance, time , driver_location,luggage =0 ):
        self.id = id
        self.cartype = booking.cartype
        self.driver_id = driver_id
        self.user_id = booking.user_id
        self.start = booking.start
        self.end  = booking.end
        self.sharing = booking.sharing
        self.luggage_weight = luggage
        self.seats = int(seats)
        self.path = path
        self.map = map
        self.driver_location = driver_location
        self.dist = float(distance)
        self.time  = float(time)

    def update(self, user_id, start, seats , map, distance, time, luggage = 0):
        self.user_id.append(user_id)
        self.start.append(start)
        self.seats = self.seats - int(seats)
        self.luggage_weight = self.luggage_weight - float(luggage)
        self.map = map
        self.dist = float(distance)
        self.time = float(time)


    def display(self):
        print("id", self.id)
        print("cartype",self.cartype )
        print(" driver_id",self.driver_id)
        print("user_id ",self.user_id )
        print("start",self.start  )
        print("end",self.end  )
        print("sharing ",self.sharing )
        print("luggage_weight ",self.luggage_weight )
        print("seats",self.seats  )
        print("path ",self.path )
        print(" driver_location",self.driver_location  )
        print(" dist",self.dist  )
        print("time ",self.time  )



from AMK_Graph import *
class Customer:
    def __init__(self, user_id, name):
        self.name = name
        self.user_id = user_id


class Driver:
    def __init__(self,id , name , license_plate ,cartype, location, seats = 4  ,Luggage_limit =20  ):
        self.id = id
        self.name = name
        self.carType = cartype
        self.seats = seats
        self.location = location
        self.luggage_weight =Luggage_limit
        self.license_plate  = license_plate


class Booking:
    def __init__(self,user_id ,start, end ,cartype,seats = 1 , luggage_req =0 , sharing = False ,distance_limit = 300):
        self.cartype = cartype
        self.user_id = user_id
        self.start = start
        self.end  = end
        self.sharing = sharing
        self.luggage_weight = luggage_req
        self.distance_limit = distance_limit
        self.seats = seats

    def car_fit(self, comparison):
        if self.cartype == comparison.cartype:
            if self.luggage_weight <= comparison.luggage_weight:
                if self.seats <= comparison.seats:
                    return True
        return False

    def journey_fit(self,comparison):
        if self.car_fit(comparison):
            comp_end = comparison.end.split(',')
            j_end = self.end.split(',')
            dist_diff = distance(float(j_end[0] ), float(j_end[1] ),float(comp_end[0] ),float(comp_end[1] ))
            if self.distance_limit <= dist_diff:
                return True
        return False




class Journey:
    def __init__(self ,id ,booking,driver_id,  seats,path ,map , luggage =0 ):
        self.id = id
        self.cartype = booking.cartype
        self.driver_id = driver_id
        self.user_id = [booking.user_id]
        self.start = [booking.start]
        self.end  = booking.end
        self.sharing = booking.sharing
        self.luggage = luggage
        self.seats = seats
        self.path = path
        self.map = map

    def update(self, user_id, start, seats , map,luggage = 0):
        self.user_id.append(user_id)
        self.start.appned(start)
        self.seats = self.seats - seats
        self.luggage = self.luggage - luggage
        self.map = map


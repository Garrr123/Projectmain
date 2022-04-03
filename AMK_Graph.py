import requests
import json
import time
import requests
from PIL import Image
from io import BytesIO
import math


class AMK_Graph:
    def __init__(self):
        self.nodes_dict = {}
        self.nodes_list = []
        self.token = api_getToken()

        import pickle
        with open('AMK_NODES.pkl', 'rb') as handle:
            self.amk_dict = pickle.load(handle)

        self.nodes_list = []
        nodes_to_delete = []
        for i in self.nodes_dict.keys():
            if type(i) is not int:
                self.nodes_list.append(i.split(","))
            else:
                nodes_to_delete.append(i)

        for i in nodes_to_delete:
            self.nodes_dict.pop(i)

    def findpath(self,start, end):
        ## get start coordinates
        start_loc = api_Search(start)
        start_coords = getLat_Long(start_loc)

        ## get end coordinates
        end_loc = api_Search(end)
        end_coords = getLat_Long(end_loc)

        ## find nearest node to start and end

        closest_end = []
        closest_start = []
        end_min = 999999999.0
        start_min = 99999999.0
        for i in self.nodes_list:
            dist_start = distance(float(i[0]), float(i[1]), float(start_coords['lat']), float(start_coords['long']))
            dist_end = distance(float(i[0]), float(i[1]), float(end_coords['lat']), float(end_coords['long']))
            if dist_start < start_min:
                closest_start = [i[0], i[1]]
                start_min = dist_start
            if dist_end < end_min:
                closest_end = [i[0], i[1]]
                end_min = dist_end

        pathFinder = shortest_path(','.join(closest_start), ','.join(closest_end), self.nodes_dict)

        paths = pathFinder.get_shortest_path()

        return paths

    def get_nearest_node(self,address):
        lat_long = getLat_Long(api_Search(address))
        closest = ""
        min_dist = 999999999
        for i in self.nodes_list:
            dist_start = distance(float(i[0]), float(i[1]), float(lat_long['lat']), float(lat_long['long']))
            if dist_start < min_dist:
                closest = str(i[0]) + ',' + str(i[1])
                min_dist = dist_start
        return closest


## Minimum Priority Queue Class , Required for shortest path algorithm
class myMinPQ():

    def __init__(self):
        self.key = []
        self.weight = []

    def insert(self, start, weigth):
        self.key.append(start)
        self.weight.append(weigth)

    def contains(self, key):
        if key in self.key:
            return True
        return False

    def delMin(self):
        index = self.weight.index(min(self.weight))
        self.weight.pop(index)
        return self.key.pop(index)

    def change(self, key, weight):
        index = self.key.index(key)
        self.weight[index] = weight

    def isEmpty(self):
        return len(self.key) == 0

## Class for finding shortest path by Time
class shortest_path:
    distTo = {}
    edgeTo = {}
    marked = {}

    pq = None

    def __init__(self, start, end, nodes_dict):
        self.start = start
        self.end = end
        for i in nodes_dict.keys():
            self.edgeTo[i] = None
            self.marked[i] = False
            self.distTo[i] = float('Inf')
            self.pq = myMinPQ()
            self.distTo[start] = 0.0
            self.pq.insert(start, 0.0)
        while not self.pq.isEmpty():
            v = self.pq.delMin()
            self.marked[v] = True
            for e in nodes_dict[v].items():
                self.relax(v, e)

    def relax(self, start, next):
        v = start
        w, weight = next
        if w not in self.distTo.keys():
            self.distTo[w] = float('Inf')
            self.marked[w] = True
        if self.distTo[w] > self.distTo[v] + weight[1]:
            self.distTo[w] = self.distTo[v] + weight[1]
            self.edgeTo[w] = start
            if self.pq.contains(w):
                self.pq.change(w, self.distTo[w])
            elif self.marked[w] is False:
                self.pq.insert(w, self.distTo[w])

    def get_shortest_path(self):
        temp = self.end
        path = [self.end]
        while self.edgeTo[temp] != self.start:
            temp = self.edgeTo[temp]
            path.append(temp)

        path.append(self.start)
        path.append(self.distTo[self.end])
        path.reverse()
        return path


## Other functions
def api_getToken():
  ## returns the String variable "access_token"
  url = "https://developers.onemap.sg/privateapi/auth/post/getToken"
  auth = {"email": "dinja0666@gmail.com", "password":"One0666mapap!"}
  x = requests.post(url, data=  auth)
  json_dict = json.loads(x.text)
  return json_dict["access_token"]

## Calculate distance between points of coordinates
def distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance.

    Parameters
    ----------
    origin : tuple of float
        (lat, long)
    destination : tuple of float
        (lat, long)

    Returns
    -------
    distance_in_km : float

    Examples
    --------
    >>> origin = (48.1372, 11.5756)  # Munich
    >>> destination = (52.5186, 13.4083)  # Berlin
    >>> round(distance(origin, destination), 1)
    504.2
    """
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def getLat_Long(result):
    if len(result['results']) == 0:
        return None
    return {"lat":result['results'][0]['LATITUDE'] , "long":result['results'][0]['LONGTITUDE']}

def api_Search(search_address):
  search_string = "https://developers.onemap.sg/commonapi/search?searchVal={0}&returnGeom={1}&getAddrDetails={2}"
  x = requests.get(search_string.format(search_address, "Y","Y"))
  result = json.loads(x.text)
  return result

def get_location_map(point):
    mark = "[" + point + ",\"255,255,178\",\"S" + "\"]"
    lat, long = point.split(',')
    url = "https://developers.onemap.sg/commonapi/staticmap/getStaticImage?layerchosen=default&lat={0}&lng={1}&zoom=15&width=512&height=512&points={2}"
    result = requests.get(url.format(lat, long, mark))
    result = Image.open(BytesIO(result.content))
    return result

def get_route_map(path, points):
    midpoint = (len(path) + 1) // 2
    marks = ""
    for id, x in enumerate(points):
        marks = marks + "[" + x[0] + ",\"255,255,178\",\"S" + "\"]|[" + x[1] + ",\"255,255,178\",\"E" + "\"]|"

    marks = marks[:-1]

    text_path = string_pointList(path) + ":255,40,40:3"

    mid_coord = path[midpoint].split(',')

    url = "https://developers.onemap.sg/commonapi/staticmap/getStaticImage?layerchosen=default&lat={0}&lng={1}&zoom=14&width=512&height=512&lines={2}&points={3}"
    result = requests.get(url.format(mid_coord[0], mid_coord[1], text_path, marks))
    result = Image.open(BytesIO(result.content))
    ##[1.31955,103.84223,"255,255,178","B"]
    return result


def string_pointList(path):
    str_path = "["
    for i in path:
        if isinstance(i, float):
            continue
        else:
            str_path = str_path + "[" + str(i) + "],"
    str_path = str_path[:-1] + "]"
    return str_path

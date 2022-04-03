from AppObjects import *

customer_list = []
driver_list = []
journey_list = []
transaction_No = 0
amk_graph = {}
journey_dict = {}

def setup( ):
    global amk_graph
    global driver_list
    global customer_list
    amk_graph = amk_graph()


    return


def book():
    global transaction_No
    transaction_No += 1

    return

def cancel(journey_id):
    return

def complete(journey_id):
    return
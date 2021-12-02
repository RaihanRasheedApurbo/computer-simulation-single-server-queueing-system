import logging
logging.getLogger().setLevel(logging.INFO)


import random
import math
def expexponential_random_variable(mean):
    uniform_random_vairable = random.uniform(0,1)
    ln_uniform_random_variable = math.log(uniform_random_vairable)
    return -1* mean * ln_uniform_random_variable

input_file = open("input.txt", "rt") # r-> read t-> text mode 
output_file = open("output.txt", "wt") # w-> write t-> text mode

number_of_events = 2

input_line = input_file.readline()
numbers = input_line.split()
mean_arrival_time = float(numbers[0])
mean_service_time = float(numbers[1])
number_of_total_customers = int(numbers[2])
logging.info(f"mean arrival time: {mean_arrival_time}")
logging.info(f"mean service time: {mean_service_time}")
logging.info(f"number of customer: {number_of_total_customers}")

from enum import Enum

class Server_Status(Enum):
    BUSY = 1
    IDLE = 0

# initializing state variables

state = {
    "sim_time" : 0.0,
    "server_status" : Server_Status.IDLE,
    "number_of_people_in_queue" : 0,
    "last_event_time" : 0.0,
}

# initializing counter variables

counter = {
    "number_of_customer_delayed" : 0,
    "total_of_delays" : 0.0,
    "area_number_in_queue" : 0.0,
    "area_server_status" : 0.0
}

# initializing event list

time_next_event = []
# departure event is in 0th index
time_next_event.append(0.0) 
# next interarrival time is in 1th index
time_next_event.append(state["sim_time"] + expexponential_random_variable(mean_arrival_time))
# next service time is in 2nd index
time_next_event.append(1.0e+30)

# while(counter["number_of_customer_delayed"] < number_of_total_customers):
    


import logging
from os import stat

logging.getLogger().setLevel(logging.INFO)
import random
import math


def expexponential_random_variable(mean):
    uniform_random_vairable = random.uniform(0, 1)
    ln_uniform_random_variable = math.log(uniform_random_vairable)
    return -1 * mean * ln_uniform_random_variable


input_file = open("input.txt", "rt")  # r-> read t-> text mode
output_file = open("output.txt", "wt")  # w-> write t-> text mode

input_line = input_file.readline()
numbers = input_line.split()
mean_arrival_time = float(numbers[0])
mean_service_time = float(numbers[1])
number_of_total_customers = int(numbers[2])
logging.info(f"mean arrival time: {mean_arrival_time}")
logging.info(f"mean service time: {mean_service_time}")
logging.info(f"number of customer: {number_of_total_customers}")

output_file.write(f"Single-server queueing system\n\n")
output_file.write(f"mean interarrival time {mean_arrival_time} minutes\n\n")
output_file.write(f"Mean service time {mean_service_time}\n\n")
output_file.write(f"Number of customers {number_of_total_customers}\n\n")

from enum import IntEnum


class Server_Status(IntEnum):
    BUSY = 1
    IDLE = 0


# initializing state variables

state = {
    "sim_time": 0.0,
    "server_status": Server_Status.IDLE,
    "number_of_people_in_queue": 0,
    "last_event_time": 0.0,
    "next_event_type": 0,
    "number_of_possible_events": 2,
}

logging.info(f"initialized state variables {state}")

# initializing counter variables

counter = {
    "number_of_customer_delayed": 0,
    "total_of_delays": 0.0,
    "area_number_in_queue": 0.0,
    "area_server_status": 0.0,
}

logging.info(f"initialized counter variables {counter}")


# initializing event list

time_next_event = []
# departure event is in 0th index
time_next_event.append(None)
# next interarrival time is in 1th index
time_next_event.append(
    state["sim_time"] + expexponential_random_variable(mean_arrival_time)
)
# next service time is in 2nd index
time_next_event.append(float("inf"))

# arrival time of every customer will be stored in this array assigning them with None
arrival_time_list = [None] * (number_of_total_customers + 1)


logging.info(f"initialized event array {time_next_event}")


def timing():
    min_time_next_event = float("inf")
    state["next_event_type"] = 0

    # figuring out which event will happen first...
    # antoher arrival or running customer deperature
    for i in range(1, state["number_of_possible_events"] + 1):  # from 1 to 2 actually
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            state["next_event_type"] = i

    # if the event list is empty then we are done we have to finish here
    if state["next_event_type"] == 0:
        output_file.write(f"\nEvent list empty at time {state['sim_time']}")
        exit(1)

    # otherwise if there is some event left
    state["sim_time"] = min_time_next_event


def update_counters():
    time_since_last_event = state["sim_time"] - state["last_event_time"]
    state["last_event_time"] = state["sim_time"]
    counter["area_number_in_queue"] += (
        state["number_of_people_in_queue"] * time_since_last_event
    )
    counter["area_server_status"] += int(state["server_status"]) * time_since_last_event


def arrive():
    # some one arriving so we have to schedule new arrival time for next person
    time_next_event[1] = state["sim_time"] + expexponential_random_variable(
        mean_arrival_time
    )

    if state["server_status"] == Server_Status.BUSY:
        state["number_of_people_in_queue"] += 1

        if state["number_of_people_in_queue"] > number_of_total_customers:
            output_file.write(
                f"\nOverflow of the array time_arrival at time {state['sim_time']}"
            )
            exit(2)

        arrival_time_list[state["number_of_people_in_queue"]] = state["sim_time"]

    else:
        counter["number_of_customer_delayed"] += 1
        state["server_status"] = Server_Status.BUSY
        # scheduling departure time for this customer
        time_next_event[2] = state["sim_time"] + expexponential_random_variable(
            mean_service_time
        )


def depart():
    # if queue is empty make the status IDLE and set departure to infinity
    if state["number_of_people_in_queue"] == 0:
        state["server_status"] = Server_Status.IDLE
        time_next_event[2] = float("inf")
    else:
        # pick the first person from the queue
        state["number_of_people_in_queue"] -= 1
        # calculate delay
        delay = state["sim_time"] - arrival_time_list[1]
        counter["total_of_delays"] += delay
        counter["number_of_customer_delayed"] += 1

        # calculate departure time for this new customer
        time_next_event[2] = state["sim_time"] + expexponential_random_variable(
            mean_service_time
        )

        # shift the queue one step left
        for i in range(1, state["number_of_people_in_queue"] + 1):
            arrival_time_list[i] = arrival_time_list[i + 1]


def report():
    logging.info(f"state: {state}")
    logging.info(f"counters: {counter}")
    average_delay = counter["total_of_delays"] / counter["number_of_customer_delayed"]
    output_file.write(f"\n\nAverage delay in queue {average_delay}\n\n")

    average_length = counter["area_number_in_queue"] / state["sim_time"]
    output_file.write(f"Average number in queue {average_length}\n\n")

    server_utilization = counter["area_server_status"] / state["sim_time"]
    output_file.write(f"Server utilization {server_utilization}\n\n")

    output_file.write(f"Time simulation ended {state['sim_time']}")


while counter["number_of_customer_delayed"] < number_of_total_customers:

    timing()

    update_counters()

    if state["next_event_type"] == 1:
        arrive()
    elif state["next_event_type"] == 2:
        depart()

report()
input_file.close()
output_file.close()

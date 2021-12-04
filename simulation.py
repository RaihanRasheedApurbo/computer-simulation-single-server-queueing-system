import logging
import random
import math
from enum import IntEnum, Enum
import csv

logging.getLogger().setLevel(logging.INFO)


class Server_Status(IntEnum):
    BUSY = 1
    IDLE = 0

class Random_Number_type(Enum):
    ARRIVAL_TIME = 1
    SERVICE_TIME = 2


def expexponential_random_variable(mean, lists, type):
    uniform_random_vairable = random.uniform(0, 1)
    lists["uniform_random_numbers"].append(uniform_random_vairable)
    ln_uniform_random_variable = math.log(uniform_random_vairable)
    return_value = -1 * mean * ln_uniform_random_variable
    if type == Random_Number_type.ARRIVAL_TIME:
        lists["arrival_time_random_numbers"].append(return_value)
    elif type == Random_Number_type.SERVICE_TIME:
        lists["service_time_random_numbers"].append(return_value)
    return return_value


def timing(state, time_next_event, output_file):
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


def update_counters(state, counter):
    time_since_last_event = state["sim_time"] - state["last_event_time"]
    state["last_event_time"] = state["sim_time"]
    counter["area_number_in_queue"] += (
        state["number_of_people_in_queue"] * time_since_last_event
    )
    counter["area_server_status"] += int(state["server_status"]) * time_since_last_event


def arrive(
    state,
    counter,
    time_next_event,
    arrival_time_list,
    mean_service_time,
    mean_arrival_time,
    number_of_total_customers,
    output_file,
    random_number_lists
):
    # some one arriving so we have to schedule new arrival time for next person
    time_next_event[1] = state["sim_time"] + expexponential_random_variable(
        mean_arrival_time, random_number_lists, Random_Number_type.ARRIVAL_TIME
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
            mean_service_time, random_number_lists, Random_Number_type.SERVICE_TIME
        )


def depart(state, counter, time_next_event, arrival_time_list, mean_service_time, random_number_lists):
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
            mean_service_time, random_number_lists, Random_Number_type.SERVICE_TIME
        )

        # shift the queue one step left
        for i in range(1, state["number_of_people_in_queue"] + 1):
            arrival_time_list[i] = arrival_time_list[i + 1]


def report(state, counter, output_file):
    logging.info(f"state after completion: {state}")
    logging.info(f"counter values after completion: {counter}")

    average_delay = counter["total_of_delays"] / counter["number_of_customer_delayed"]
    output_file.write(f"\n\nAverage delay in queue {average_delay}\n\n")

    average_length = counter["area_number_in_queue"] / state["sim_time"]
    output_file.write(f"Average number in queue {average_length}\n\n")

    server_utilization = counter["area_server_status"] / state["sim_time"]
    output_file.write(f"Server utilization {server_utilization}\n\n")

    output_file.write(f"Time simulation ended {state['sim_time']}")


def simulate(mean_arrival_time, mean_service_time, number_of_total_customers):

    output_file = open("output.txt", "wt")  # w-> write t-> text mode

    logging.info(f"mean arrival time: {mean_arrival_time}")
    logging.info(f"mean service time: {mean_service_time}")
    logging.info(f"number of customer: {number_of_total_customers}")

    output_file.write(f"Single-server queueing system\n\n")
    output_file.write(f"mean interarrival time {mean_arrival_time} minutes\n\n")
    output_file.write(f"Mean service time {mean_service_time}\n\n")
    output_file.write(f"Number of customers {number_of_total_customers}\n\n")

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

    # initializing random number lists for part_c
    random_number_lists = {
        "uniform_random_numbers": [],
        "arrival_time_random_numbers": [],
        "service_time_random_numbers": []
    }

    logging.info(f"initialized counter variables {counter}")

    # initializing event list

    time_next_event = []
    # departure event is in 0th index
    time_next_event.append(None)
    # next interarrival time is in 1th index
    time_next_event.append(
        state["sim_time"] + expexponential_random_variable(mean_arrival_time, random_number_lists, Random_Number_type.ARRIVAL_TIME)
    )
    # next service time is in 2nd index
    time_next_event.append(float("inf"))

    # arrival time of every customer will be stored in this array assigning them with None
    arrival_time_list = [None] * (number_of_total_customers + 1)

    logging.info(f"initialized event array {time_next_event}")

    while counter["number_of_customer_delayed"] < number_of_total_customers:

        timing(state, time_next_event, output_file)

        update_counters(state, counter)

        if state["next_event_type"] == 1:
            arrive(
                state,
                counter,
                time_next_event,
                arrival_time_list,
                mean_service_time,
                mean_arrival_time,
                number_of_total_customers,
                output_file,
                random_number_lists
            )
        elif state["next_event_type"] == 2:
            depart(
                state, counter, time_next_event, arrival_time_list, mean_service_time, random_number_lists
            )

    report(state, counter, output_file)
    output_file.close()

    return state, counter, random_number_lists


def part_a():
    input_file = open("input.txt", "rt")  # r-> read t-> text mode

    input_line = input_file.readline()
    numbers = input_line.split()
    mean_arrival_time = float(numbers[0])
    mean_service_time = float(numbers[1])
    number_of_total_customers = int(numbers[2])
    input_file.close()

    simulate(mean_arrival_time, mean_service_time, number_of_total_customers)


def part_b():
    input_file = open("input.txt", "rt")  # r-> read t-> text mode

    input_line = input_file.readline()
    numbers = input_line.split()
    mean_arrival_time = float(numbers[0])
    mean_service_time = float(numbers[1])  # this is not needed for part_b
    number_of_total_customers = int(numbers[2])
    input_file.close()
    
    csv_file = open("report.csv", "wt")
    csv_writer = csv.writer(csv_file)
    header = [
        "k",
        "average delay in queue",
        "average number in queue",
        "server utilization",
        "time the simulation ended",
    ]
    csv_writer.writerow(header)

    k_values = [0.5, 0.6, 0.7, 0.8, 0.9]

    for k in k_values:
        state, counter, _ = simulate(
            mean_arrival_time, k * mean_arrival_time, number_of_total_customers
        )
        logging.info(f"iteration : {k}")
        logging.info(f"state after completion: {state}")
        logging.info(f"counter values after completion: {counter}")

        average_delay = (
            counter["total_of_delays"] / counter["number_of_customer_delayed"]
        )
        average_length = counter["area_number_in_queue"] / state["sim_time"]
        server_utilization = counter["area_server_status"] / state["sim_time"]

        row = [
            str(k),
            str(average_delay),
            str(average_length),
            str(server_utilization),
            state["sim_time"],
        ]
        csv_writer.writerow(row)

    csv_file.close()

def part_c():
    input_file = open("input.txt", "rt")  # r-> read t-> text mode

    input_line = input_file.readline()
    numbers = input_line.split()
    mean_arrival_time = float(numbers[0])
    mean_service_time = float(numbers[1])
    number_of_total_customers = int(numbers[2])
    input_file.close()

    state, counter, random_number_lists = simulate(mean_arrival_time, mean_service_time, number_of_total_customers)

    uniform_random_numbers = random_number_lists["uniform_random_numbers"]
    arrival_time_random_numbers = random_number_lists["arrival_time_random_numbers"]
    service_time_random_numbers = random_number_lists["service_time_random_numbers"]

    logging.info(f"{len(uniform_random_numbers)} {len(arrival_time_random_numbers)}, {len(service_time_random_numbers)}")

    # uniform random variable p(x) f(x) calculation
    bucket_length = 10
    uniform_bucket = [0] * bucket_length
    for i in range(bucket_length):
        uniform_bucket[i] = ((i+1)/bucket_length) # creating bucket ranging from 0-.1, .1-.2 and so on....
    data_frequency = [0] * bucket_length

    for data in uniform_random_numbers:
        for i in range(bucket_length):
            if data <= uniform_bucket[i]:
                data_frequency[i] += 1
                break
    logging.info(uniform_bucket)
    logging.info(data_frequency)

    p_x = [0] * bucket_length
    for i in range(bucket_length):
        p_x[i] = data_frequency[i] / len(uniform_random_numbers)
    logging.info(f"uniform p(x): {p_x}")
    
    f_x = [0] * bucket_length
    f_x[0] = p_x[0]
    for i in range(1,bucket_length):
        f_x[i] = f_x[i-1] + p_x[i]
    logging.info(f"uniform f(x): {f_x}")

    # p(x) and f(x) calculation for arrival time
    bucket_length = 4
    exponential_arrival_bucket = [mean_arrival_time/2, mean_arrival_time, 2*mean_arrival_time, 3*mean_arrival_time]
    data_frequency = [0] * bucket_length

    for data in arrival_time_random_numbers:
        for i in range(bucket_length):
            if data <= exponential_arrival_bucket[i]:
                data_frequency[i] += 1
                break
    
    logging.info(exponential_arrival_bucket)
    logging.info(data_frequency)

    p_x = [0] * bucket_length
    for i in range(bucket_length):
        p_x[i] = data_frequency[i] / len(arrival_time_random_numbers)
    logging.info(f"exponential arrival p(x): {p_x}")
    
    f_x = [0] * bucket_length
    f_x[0] = p_x[0]
    for i in range(1,bucket_length):
        f_x[i] = f_x[i-1] + p_x[i]
    logging.info(f"exponential arrival f(x): {f_x}")

    # p(x) and f(x) calculation for service time
    bucket_length = 4
    exponential_service_bucket = [mean_service_time/2, mean_service_time, 2*mean_service_time, 3*mean_service_time]
    data_frequency = [0] * bucket_length

    for data in service_time_random_numbers:
        for i in range(bucket_length):
            if data <= exponential_service_bucket[i]:
                data_frequency[i] += 1
                break
    
    logging.info(exponential_service_bucket)
    logging.info(data_frequency)

    p_x = [0] * bucket_length
    for i in range(bucket_length):
        p_x[i] = data_frequency[i] / len(service_time_random_numbers)
    logging.info(f"exponential service p(x): {p_x}")
    
    f_x = [0] * bucket_length
    f_x[0] = p_x[0]
    for i in range(1,bucket_length):
        f_x[i] = f_x[i-1] + p_x[i]
    logging.info(f"exponential service f(x): {f_x}")

    




    




part_c()

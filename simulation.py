import logging
logging.getLogger().setLevel(logging.INFO)

input_file = open("input.txt", "rt") # r-> read t-> text mode 
output_file = open("output.txt", "wt") # w-> write t-> text mode

number_of_events = 2

input_line = input_file.readline()
numbers = input_line.split()
mean_arrival_time = float(numbers[0])
mean_service_time = float(numbers[1])
number_of_customers = int(numbers[2])
logging.info(f"mean arrival time: {mean_arrival_time}")
logging.info(f"mean service time: {mean_service_time}")
logging.info(f"number of customer: {number_of_customers}")


import random
import math

# Global variables for the inventory system
amount = bigs = initial_inv_level = inv_level = next_event_type = 0
num_events = num_months = num_values_demand = smalls = 0
area_holding = area_shortage = holding_cost = incremental_cost = 0.0
maxlag = mean_interdemand = minlag = setup_cost = shortage_cost = 0.0
sim_time = time_last_event = total_ordering_cost = 0.0
time_next_event = [0.0] * 5
prob_distrib_demand = []

# Input/Output files
infile = None
outfile = None

def initialize():
    global sim_time, inv_level, time_last_event, total_ordering_cost, area_holding, area_shortage
    sim_time = 0.0
    inv_level = initial_inv_level
    time_last_event = 0.0
    total_ordering_cost = area_holding = area_shortage = 0.0
    time_next_event[1] = float('inf')  # Next order arrival is set to infinite
    time_next_event[2] = sim_time + expon(mean_interdemand)  # Next demand event
    time_next_event[3] = num_months  # End of simulation
    time_next_event[4] = 0.0  # Evaluation time

def timing():
    global sim_time, next_event_type
    min_time_next_event = float('inf')
    next_event_type = 0
    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i
    if next_event_type == 0:
        print("Event list empty at time:", sim_time)
        exit()
    sim_time = min_time_next_event

def order_arrival():
    global inv_level, time_next_event
    inv_level += amount
    time_next_event[1] = float('inf')  # Reset next order arrival time

def demand():
    global inv_level
    inv_level -= random_integer(prob_distrib_demand)
    time_next_event[2] = sim_time + expon(mean_interdemand)

def evaluate():
    global inv_level, amount, total_ordering_cost
    if inv_level < smalls:
        amount = bigs - inv_level
        total_ordering_cost += setup_cost + incremental_cost * amount
        time_next_event[1] = sim_time + uniform(minlag, maxlag)  # Next order arrival based on lag
    time_next_event[4] = sim_time + 1.0  # Evaluation time

def report():
    avg_ordering_cost = total_ordering_cost / num_months
    avg_holding_cost = holding_cost * area_holding / num_months
    avg_shortage_cost = shortage_cost * area_shortage / num_months
    # print(avg_shortage_cost)
    avg_total_cost = avg_ordering_cost + avg_holding_cost + avg_shortage_cost
    outfile.write(f"\n\n({smalls},{bigs})     {avg_total_cost:15.2f}     {avg_ordering_cost:15.2f}     {avg_holding_cost:15.2f}     {avg_shortage_cost:15.2f}")

def update_time_avg_stats():
    global area_holding, area_shortage, time_last_event
    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time
    if inv_level < 0:
        area_shortage -= inv_level * time_since_last_event  # Negative inv_level indicates shortage
    elif inv_level > 0:
        area_holding += inv_level * time_since_last_event  # Positive inv_level indicates holding

def expon(mean):
    return -mean * math.log(random.random())

def random_integer(prob_distrib):
    u = random.random()
    i = 1
    while u >= prob_distrib[i]:
        i += 1
    return i

def uniform(a, b):
    return a + random.random() * (b - a)

def main():
    global initial_inv_level, num_months, num_policies, num_values_demand, num_events
    global mean_interdemand, setup_cost, incremental_cost, holding_cost, shortage_cost
    global minlag, maxlag, prob_distrib_demand, smalls, bigs, infile, outfile

    # Open input and output files
    infile = open("in.txt", "r")
    outfile = open("out.txt", "w")

    num_events = 4  # Constant, based on the events order

    # Read the first line
    initial_inv_level, num_months, num_policies = map(int, infile.readline().split())

    # Read the demand parameters
    num_values_demand, mean_interdemand = map(float, infile.readline().split())

    # Read the cost parameters
    setup_cost, incremental_cost, holding_cost, shortage_cost = map(float, infile.readline().split())
    
    # Read the delivery lag range
    minlag, maxlag = map(float, infile.readline().split())

    # Read the cumulative distribution function for demand sizes
    prob_distrib_demand = [0.0] + [float(x) for x in infile.readline().split()]

    # Write initial information to the output file
    outfile.write("------Single-product inventory system------\n\n")
    outfile.write(f"Initial inventory level: {initial_inv_level} items\n\n")
    outfile.write(f"Number of demand sizes: {int(num_values_demand)}\n\n")
    outfile.write("Distribution function of demand sizes: ")
    outfile.write(" ".join(f"{x:8.2f}" for x in prob_distrib_demand[1:]) + "\n\n")
    outfile.write(f"Mean interdemand time: {mean_interdemand:.2f} months\n\n")
    outfile.write(f"Delivery lag range: {minlag:.2f} to {maxlag:.2f} months\n\n")
    outfile.write(f"Length of the simulation: {num_months} months\n\n")
    outfile.write(f"Costs:\nK = {setup_cost:.2f}\ni = {incremental_cost:.2f}\nh = {holding_cost:.2f}\npi = {shortage_cost:.2f}\n\n")
    outfile.write(f"Number of policies: {num_policies}\n\n")
    outfile.write("Policies:\n")
    outfile.write("--------------------------------------------------------------------------------------------------\n")
    outfile.write(" Policy        Avg_total_cost     Avg_ordering_cost      Avg_holding_cost     Avg_shortage_cost\n")
    outfile.write("--------------------------------------------------------------------------------------------------")

    # Process each policy
    for _ in range(num_policies):
        smalls, bigs = map(int, infile.readline().split())
        initialize()
        while True:
            timing()
            update_time_avg_stats()
            if next_event_type == 1:
                order_arrival()
            elif next_event_type == 2:
                demand()
            elif next_event_type == 4:
                evaluate()
            elif next_event_type == 3:
                report()
                break

    outfile.write("\n--------------------------------------------------------------------------------------------------")
    infile.close()
    outfile.close()

if __name__ == "__main__":
    main()

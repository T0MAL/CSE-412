import math
import random

# Constants
Q_LIMIT = 100  # Limit on queue length
BUSY = 1       # Mnemonics for server being busy
IDLE = 0       # Mnemonics for server being idle
LARGE_NUM = 1.0e+30

# Global variables
next_event_type = None
num_custs_delayed = 0
num_delays_required = None
num_events = 2  
num_in_q = 0
server_status = IDLE
area_num_in_q = 0.0
area_server_status = 0.0
mean_interarrival = None
mean_service = None
sim_time = 0.0
time_arrival = [0.0] * (Q_LIMIT + 1)
time_last_event = 0.0
time_next_event = [0.0, 0.0, LARGE_NUM]  # event 0: arrival, event 1: departure
total_of_delays = 0.0

def expon(mean):
    return -mean*math.log(random.random())

def initialize():
    global sim_time, server_status, num_in_q, time_last_event, num_custs_delayed, total_of_delays, area_num_in_q, area_server_status
    global time_next_event
    sim_time = 0.0
    server_status = IDLE
    num_in_q = 0
    time_last_event = 0.0
    num_custs_delayed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status = 0.0

    time_next_event[0] = sim_time + expon(mean_interarrival) 
    time_next_event[1] = LARGE_NUM  

def timing():
    global next_event_type,sim_time,time_next_event
    min_time_next_event = min(time_next_event)
    next_event_type=time_next_event.index(min_time_next_event)
    sim_time=min_time_next_event

def update_time_avg_stats():
    global time_last_event,area_num_in_q,area_server_status
    time_between_events = sim_time-time_last_event
    area_num_in_q+=num_in_q*time_between_events
    area_server_status+=server_status*time_between_events
    time_last_event=sim_time

def arrive():
    global time_next_event,num_in_q,server_status,num_custs_delayed
    time_next_event[0] = sim_time+expon(mean_interarrival)
    if server_status==BUSY:
        num_in_q+=1
        if num_in_q>Q_LIMIT:
            print(f"Overflow of the array time_arrival at time {sim_time}")
            exit(2)
        time_arrival[num_in_q] = sim_time
    else:
        num_custs_delayed+=1
        server_status=BUSY
        time_next_event[1] = sim_time+expon(mean_service)

def depart():
    global server_status,time_next_event,total_of_delays,num_in_q,num_custs_delayed,time_arrival
    if not num_in_q:
        server_status=IDLE
        time_next_event[1] = LARGE_NUM
    else:
        num_in_q-=1
        delay = sim_time-time_arrival[1]
        total_of_delays+=delay
        num_custs_delayed+=1
        time_next_event[1]=sim_time+expon(mean_service)
        for i in range(1,num_in_q+1):
            time_arrival[i]=time_arrival[i+1]

def report():
    with open('out1.out','w') as outfile:
        outfile.write("Single-server queueing system\n\n")
        outfile.write(f"Mean interarrival time{mean_interarrival:11.3f} minutes\n\n")
        outfile.write(f"Mean service time{mean_service:16.3f} minutes\n\n")
        outfile.write(f"Number of customers{num_delays_required:14d}\n\n\n")
        outfile.write(f"Average delay in queue: {total_of_delays / num_custs_delayed:.3f} minutes\n\n")
        outfile.write(f"Average number in queue: {area_num_in_q / sim_time:.3f}\n\n")
        outfile.write(f"Server utilization: {area_server_status / sim_time:.3f}\n\n")
        outfile.write(f"Time simulation ended: {sim_time:.3f} minutes\n\n")


def report2(event_count):
    with open('out2.out','a') as outfile:
        if next_event_type==0:
            outfile.write(f'{event_count}. Next event: Customer {num_custs_delayed+num_in_q} Arrival\n\n')
            outfile.write(f'---------No of customer delayed: {num_custs_delayed}---------\n\n') 
        else:
            if server_status==BUSY:
                outfile.write(f'{event_count}. Next event: Customer {num_custs_delayed-1} Departure\n')
            else:
                outfile.write(f'{event_count}. Next event: Customer {num_custs_delayed} Departure\n')



def main():
    global mean_interarrival, mean_service, num_delays_required,next_event_type
    with open('out2.out','w') as outfile:
        outfile.write('')
    event_count =1
    with open("in.in", "r") as infile:
        mean_interarrival, mean_service, num_delays_required = map(float, infile.readline().split())
        num_delays_required = int(num_delays_required)  # Convert to integer

        initialize()

        while num_custs_delayed < num_delays_required:
            timing()
            update_time_avg_stats()
            
            if next_event_type == 0:
                arrive()
            elif next_event_type == 1:
                depart()
            report2(event_count)
            event_count+=1

        report()
        

if __name__ == "__main__":
    main()

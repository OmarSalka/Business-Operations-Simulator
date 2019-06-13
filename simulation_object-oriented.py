# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 14:38:01 2018

@author: omari
"""


import pandas as pd
import numpy as np
import math
#discrete random number generator
next_step = ["Exit", "Repair Station"]
probabilities = [0.7, 0.3]
np.random.choice(next_step, p=probabilities)

class simulation:
    
    def __init__(self):
        
        #arrays that build columns for our dataframe
        self.arrival_departure = []
        self.interarrival_time = []
        self.service_time = []
        self.tm = []
        self.system_state = []
        self.waiting_in_line= []
        self.next_arrival = []
        self.next_departure = []
        self.insys = []
        self.next_stop = []
        self.total_wait = []
        self.time_btw_events = []
        
        #system state:
        self.num_in_system = 0
        self.idle_or_busy = 0
        self.queue = 0
        self.index_for_time_btw = 0
        #transition from queue 1 to 2
        self.next_phase = ""
        
        
        #simulation variables
        self.clock = 0.0
        self.t_arrival = self.generate_interarrival()
        self.t_depart = float('inf')
        
        #statistical counters
        self.num_arrivals = 0
        self.num_departures = 0
        self.waiting_time = 0
        
    def advance_time(self):
        
        t_event = min(self.t_arrival, self.t_depart)
        
        self.waiting_time = self.queue*(t_event - self.clock)
        self.total_wait.append(self.waiting_time)
        
        #
        self.clock = t_event
        self.tm.append(self.clock)
        
        
        if self.t_arrival <= self.t_depart:
            self.arrival_departure.append("Arrival")
            self.handle_arrival_event()
            self.service_time.append(self.t_depart - self.clock)
            
        else:
            self.arrival_departure.append("Departure")
            self.handle_departure_event()
            self.service_time.append("")
            
        #system state
        if self.num_in_system > 0:
            self.idle_or_busy = 1
        else:
            self.idle_or_busy = 0
        
        self.system_state.append(self.idle_or_busy)
        
        #waiting in line
        self.waiting_in_line.append(self.queue)
        self.insys.append(self.num_in_system)
        
        #time btw events
        self.generating_time_between_events()
    
        #end
        if self.clock >= 160:
            self.assembling_dataframe()
            self.simulation_stats()
        
    def handle_arrival_event(self):
        
        self.num_in_system += 1
        self.queue = self.num_in_system -1
        self.num_arrivals += 1
        
        if self.num_in_system <= 1:
            self.t_depart = self.clock + self.generate_service_time()
            self.next_departure.append(self.t_depart)
        else:
            self.next_departure.append("")
        self.t_arrival = self.clock + self.generate_interarrival()
        self.interarrival_time.append(self.t_arrival - self.clock)
        self.next_arrival.append(self.t_arrival)
        
        #to avoid dicrepancies
        self.next_stop.append("")
        
    
    
    def handle_departure_event(self):
        self.num_in_system -=1
        if self.num_in_system >0:
            self.queue = self.num_in_system -1
        else:
            self.queue = 0
        self.num_departures += 1
        
        #part 2
        self.exit_or_repair()
        
        if self.num_in_system > 0:
            self.t_depart = self.clock + self.generate_service_time()
        else:
            self.t_depart = float('inf')
        
        self.next_departure.append(self.t_depart)
        
        #to avoid discrepancies
        self.interarrival_time.append("")
        self.next_arrival.append("")
        
    def generate_interarrival(self):
        return np.random.exponential(2)
        #return np.random.exponential(0.5)   
        
        
    def generate_service_time(self):
        return np.random.uniform(0.25, 1.05)
        #return np.random.uniform(0.25*0.6, 1.05*0.6)
    
    def exit_or_repair(self):
        self.next_phase = np.random.choice(next_step, p=probabilities)
        self.next_stop.append(self.next_phase)
        
    def generating_time_between_events(self):
        #generating time between events
        if self.index_for_time_btw > 0:
            tbev = self.tm[self.index_for_time_btw] - self.tm[self.index_for_time_btw - 1]
            self.time_btw_events.append(tbev)
        if len(self.tm) > 1 and self.tm[-1] >= 160:
            self.time_btw_events.append(0)
        
        self.index_for_time_btw += 1
    
    def assembling_dataframe(self):
        #assembling the lists into a dataframe
        self.simulation_dataframe = pd.DataFrame({"event_type":self.arrival_departure,
                                         "clock":self.tm,
                                         "interarrival_time":self.interarrival_time,
                                         "service_time":self.service_time,
                                         "system_state": self.system_state,
                                         "waiting_in_line":self.waiting_in_line,
                                         "next_arrival":self.next_arrival,
                                         "next_departure":self.next_departure,
                                         "insys":self.insys,
                                         "time_btw_events":self.time_btw_events,
                                         "next_stop":self.next_stop,
                                         "waiting_time":self.total_wait})
    
        self.simulation_dataframe = self.simulation_dataframe[["event_type", "clock", "interarrival_time", "service_time", "system_state", "waiting_in_line", "next_arrival", "next_departure", "insys", "time_btw_events", "waiting_time", "next_stop" ]]
    
    def simulation_stats(self):
        sumproduct1 = self.simulation_dataframe.iloc[:, 9].dot(self.simulation_dataframe.iloc[:, 5])
        self.average_delay_in_queue1 = sumproduct1/self.clock
        #self.average_delay_in_queue1 = sum(self.total_wait)/self.num_departures
        self.average_length_of_queue1 = (self.simulation_dataframe['waiting_in_line'].sum()/len(self.simulation_dataframe['waiting_in_line']))
        sumproduct2 = self.simulation_dataframe.iloc[:, 9].dot(self.simulation_dataframe.iloc[:, 4])
        self.utilization_of_queue1 = sumproduct2/self.clock

s1 = simulation()
while(s1.clock <= 160):
    s1.advance_time()    
df1 = s1.simulation_dataframe
    #preparing repair service time
df1_r = df1[df1['next_stop'] == 'Repair Station']
list_sim_1 = df1_r['clock'].values
index = 0
finalized_serv_list_1 = []
for i in range(len(list_sim_1)):
    if index > 0:
        finalized_serv_list_1.append(list_sim_1[index]- list_sim_1[index-1])
    index +=1    

s2 = simulation()
while(s2.clock <= 160):
    s2.advance_time()
df2 = s2.simulation_dataframe
    #preparing repair service time
df2_r = df2[df2['next_stop'] == 'Repair Station']
list_sim_2 = df2_r['clock'].values
index = 0
finalized_serv_list_2 = []
for i in range(len(list_sim_2)):
    if index > 0:
        finalized_serv_list_2.append(list_sim_2[index]- list_sim_2[index-1])
    index +=1 


s3 = simulation()
while(s3.clock <= 160):
    s3.advance_time()
df3 = s3.simulation_dataframe
    #preparing repair service time
df3_r = df3[df3['next_stop'] == 'Repair Station']
list_sim_3 = df3_r['clock'].values
index = 0
finalized_serv_list_3 = []
for i in range(len(list_sim_3)):
    if index > 0:
        finalized_serv_list_3.append(list_sim_3[index]- list_sim_3[index-1])
    index +=1 


s4 = simulation()
while(s4.clock <= 160):
    s4.advance_time()
df4 = s4.simulation_dataframe
    #preparing repair service time
df4_r = df4[df4['next_stop'] == 'Repair Station']
list_sim_4 = df4_r['clock'].values
index = 0
finalized_serv_list_4 = []
for i in range(len(list_sim_4)):
    if index > 0:
        finalized_serv_list_4.append(list_sim_4[index]- list_sim_4[index-1])
    index +=1 


s5 = simulation()
while(s5.clock <= 160):
    s5.advance_time()
df5 = s5.simulation_dataframe
    #preparing service time
df5_r = df5[df5['next_stop'] == 'Repair Station']
list_sim_5 = df5_r['clock'].values
index = 0
finalized_serv_list_5 = []
for i in range(len(list_sim_5)):
    if index > 0:
        finalized_serv_list_5.append(list_sim_5[index]- list_sim_5[index-1])
    index +=1 





#transitoning from inspection to repair
class repair_simulation:
    
    def __init__(self, interarrival_list, clock):
        
        self.interarrival = interarrival_list
        
        self.final_clock = clock
        #arrays that build columns for our dataframe
        self.arrival_departure = []
        self.interarrival_time = []
        self.service_time = []
        self.tm = []
        self.system_state = []
        self.waiting_in_line= []
        self.next_arrival = []
        self.next_departure = []
        self.insys = []
        self.total_wait = []
        self.time_btw_events = []
        
        #for interarrival generator
        self.interarrival_counter = -1
        
        #system state:
        self.num_in_system = 0
        self.idle_or_busy = 0
        self.queue = 0
        self.index_for_time_btw = 0
        
        #simulation variables
        self.clock = 0.0
        self.t_arrival = self.generate_interarrival()
        self.t_depart = float('inf')
        
        #statistical counters
        self.num_arrivals = 0
        self.num_departures = 0
        self.waiting_time = 0
        

    def advance_time(self):
        t_event = min(self.t_arrival, self.t_depart)
        
        self.waiting_time = self.queue*(t_event - self.clock)
        self.total_wait.append(self.waiting_time)
        
        #
        self.clock = t_event
        self.tm.append(self.clock)
        
        
        if self.t_arrival <= self.t_depart:
            self.arrival_departure.append("Arrival")
            self.handle_arrival_event()
            self.service_time.append(self.t_depart - self.clock)
            
        else:
            self.arrival_departure.append("Departure")
            self.handle_departure_event()
            self.service_time.append("")
         
        #system state
        if self.num_in_system > 0:
            self.idle_or_busy = 1
        else:
            self.idle_or_busy = 0
        
        self.system_state.append(self.idle_or_busy)
        
        #waiting in line
        self.waiting_in_line.append(self.queue)
        self.insys.append(self.num_in_system)
        
        #time btw events
        self.generating_time_between_events()
    
        #end
        if self.interarrival_counter >= len(self.interarrival):
            self.assembling_dataframe()
            self.simulation_stats()

    def handle_arrival_event(self):
        self.num_in_system += 1
        if self.num_in_system >1:
            self.queue = self.num_in_system -2
        else:
            self.queue = 0
        
        self.num_arrivals += 1
        
        if self.num_in_system <= 1:
            self.t_depart = self.clock + self.generate_service_time()
            self.next_departure.append(self.t_depart)
        else:
            self.next_departure.append("")
        self.t_arrival = self.clock + self.generate_interarrival()
        self.interarrival_time.append(self.t_arrival - self.clock)
        self.next_arrival.append(self.t_arrival)
        

    def handle_departure_event(self):
        self.num_in_system -=1
        if self.num_in_system > 1:
            self.queue = self.num_in_system -2
        else:
            self.queue = 0
        self.num_departures += 1
        
        if self.num_in_system > 0:
            self.t_depart = self.clock + self.generate_service_time()
        else:
            self.t_depart = float('inf')
        
        self.next_departure.append(self.t_depart)
        
        #to avoid discrepancies
        self.interarrival_time.append("")
        self.next_arrival.append("")
    
    def generate_interarrival(self):
        self.interarrival_counter +=1
        #return finalized_serv_list_1[self.interarrival_counter]
        return self.interarrival[self.interarrival_counter]
    def generate_service_time(self):
        return np.random.uniform(2.1, 4.5)

    def generating_time_between_events(self):
        #generating time between events
        if self.index_for_time_btw > 0:
            tbev = self.tm[self.index_for_time_btw] - self.tm[self.index_for_time_btw - 1]
            self.time_btw_events.append(tbev)
        if len(self.tm) > 1 and self.tm[-1] >= 160:
            self.time_btw_events.append(0)
        
        self.index_for_time_btw += 1
    
    def assembling_dataframe(self):
        #assembling the lists into a dataframe
        self.simulation_dataframe = pd.DataFrame({"event_type":self.arrival_departure,
                                                 "clock":self.tm,
                                                 "interarrival_time":self.interarrival_time,
                                                 "service_time":self.service_time,
                                                 "system_state": self.system_state,
                                                 "waiting_in_line":self.waiting_in_line,
                                                 "next_arrival":self.next_arrival,
                                                 "next_departure":self.next_departure,
                                                 "insys":self.insys,
                                                 "time_btw_events":self.time_btw_events,
                                                 "waiting_time":self.total_wait})
    
        self.simulation_dataframe = self.simulation_dataframe[["event_type", "clock", "interarrival_time", "service_time", "system_state", "waiting_in_line", "next_arrival", "next_departure", "insys", "time_btw_events", "waiting_time" ]]
    
    def simulation_stats(self):
        sumproduct1 = self.simulation_dataframe.iloc[:, 9].dot(self.simulation_dataframe.iloc[:, 5])
        self.average_delay_in_queue2 = sumproduct1/self.final_clock
        self.average_length_of_queue2 = (self.simulation_dataframe['waiting_in_line'].sum()/len(self.simulation_dataframe['waiting_in_line']))
        sumproduct2 = self.simulation_dataframe.iloc[:, 9].dot(self.simulation_dataframe.iloc[:, 4])
        self.utilization_of_queue2 = sumproduct2/self.final_clock

    
r1 = repair_simulation(finalized_serv_list_1, s1.clock)
for i in range(len(list_sim_1)):
    r1.advance_time()
r1.time_btw_events.append(0)
r1.assembling_dataframe()
r1.simulation_stats()
rep1 = r1.simulation_dataframe

r2 = repair_simulation(finalized_serv_list_2, s2.clock)
for i in range(len(list_sim_2)):
    r2.advance_time()
r2.time_btw_events.append(0)
r2.assembling_dataframe()
r2.simulation_stats()
rep2 = r2.simulation_dataframe

r3 = repair_simulation(finalized_serv_list_3, s3.clock)
for i in range(len(list_sim_3)):
    r3.advance_time()    
r3.time_btw_events.append(0)
r3.assembling_dataframe()
r3.simulation_stats()
rep3 = r3.simulation_dataframe

r4 = repair_simulation(finalized_serv_list_4, s4.clock)
for i in range(len(list_sim_4)):
    r4.advance_time()    
r4.time_btw_events.append(0)
r4.assembling_dataframe()
r4.simulation_stats()
rep4 = r4.simulation_dataframe

r5 = repair_simulation(finalized_serv_list_5, s5.clock)
for i in range(len(list_sim_5)):
    r5.advance_time()
r5.time_btw_events.append(0)
r5.assembling_dataframe()
r5.simulation_stats()
rep5 = r5.simulation_dataframe



#Matrix of stats
stats = ['average delay of que', 'average length of queue', 'Utilization', 'total_arrivals']
Simulation_1 = ['','','', '']
inspection_s1 = [s1.average_delay_in_queue1, s1.average_length_of_queue1, s1.utilization_of_queue1, s1.num_arrivals]
repair_s1 = [r1.average_delay_in_queue2, r1.average_length_of_queue2, r1.utilization_of_queue2, r1.num_arrivals]
Simulation_2 = ['','','','']
inspection_s2 = [s2.average_delay_in_queue1, s2.average_length_of_queue1, s2.utilization_of_queue1, s2.num_arrivals]
repair_s2 = [r2.average_delay_in_queue2, r2.average_length_of_queue2, r2.utilization_of_queue2, r2.num_arrivals]
Simulation_3 = ['','','','']
inspection_s3 = [s3.average_delay_in_queue1, s3.average_length_of_queue1, s3.utilization_of_queue1, s3.num_arrivals]
repair_s3 = [r3.average_delay_in_queue2, r3.average_length_of_queue2, r3.utilization_of_queue2, r3.num_arrivals]
Simulation_4 = ['','','','']
inspection_s4 = [s4.average_delay_in_queue1, s4.average_length_of_queue1, s4.utilization_of_queue1, s3.num_arrivals]
repair_s4 = [r4.average_delay_in_queue2, r4.average_length_of_queue2, r4.utilization_of_queue2, r4.num_arrivals]
Simulation_5 = ['','','','']
inspection_s5 = [s5.average_delay_in_queue1, s5.average_length_of_queue1, s5.utilization_of_queue1, s5.num_arrivals]
repair_s5 = [r5.average_delay_in_queue2, r5.average_length_of_queue2, r5.utilization_of_queue2, r5.num_arrivals]

matrix = pd.DataFrame({'Stats':stats,
                       'Simulation_1':Simulation_1, 'inspection_s1':inspection_s1, 'repair_s1':repair_s1,
                       'Simulation_2':Simulation_2, 'inspection_s2':inspection_s2, 'repair_s2':repair_s2,
                       'Simulation_3':Simulation_3, 'inspection_s3':inspection_s3, 'repair_s3':repair_s3,
                       'Simulation_4':Simulation_4, 'inspection_s4':inspection_s4, 'repair_s4':repair_s4,
                       'Simulation_5':Simulation_5, 'inspection_s5':inspection_s5, 'repair_s5':repair_s5}, index = ['average delay of que', 'average length of queue', 'Utilization', 'total_arrivals'])

matrix = matrix[['Simulation_1', 'inspection_s1', 'repair_s1',
                 'Simulation_2', 'inspection_s2', 'repair_s2',
                 'Simulation_3', 'inspection_s3', 'repair_s3', 
                 'Simulation_4', 'inspection_s4', 'repair_s4', 
                 'Simulation_5', 'inspection_s5', 'repair_s5']]

#exporting files
    #inspection
df1.to_csv("inspection_s1_sq.csv")
df2.to_csv("inspection_s2_sq.csv")
df3.to_csv("inspection_s3_sq.csv")
df4.to_csv("inspection_s4_sq.csv")
df5.to_csv("inspection_s5_sq.csv")
    #repair
rep1.to_csv("repair_s1_sq.csv")
rep2.to_csv("repair_s2_sq.csv")
rep3.to_csv("repair_s3_sq.csv")
rep4.to_csv("repair_s4_sq.csv")
rep5.to_csv("repair_s5_sq.csv")
    #matrix
matrix.to_csv("matrix_sq.csv")

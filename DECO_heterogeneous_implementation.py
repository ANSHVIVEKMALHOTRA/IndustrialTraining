import random
import math
import numpy as np

# Parameters based on the heterogeneous input
num_fog_nodes = 5
bandwidth = 16 * 1e6  # in bits per second (Bw)
input_size_range = (300 * 1e3, 600 * 1e3)  # in bits
output_size_range = (10 * 1e3, 20 * 1e3)  # in bits
computational_demand = (210e2, 480e2)  # in cycles
fog_node_processing_power = [210 * 1e6] * num_fog_nodes  # Array of processing powers
num_iot_devices = 25
noise_power = 1e-10  # in Watts
transmission_power_range = (0.1, 0.5)  # in Watts
deadline_range = (30, 60)  # in seconds
alpha = 1

# Generate random tasks for IoT devices
def generate_tasks(num_tasks):
   tasks = []
   for _ in range(num_tasks):
       task = {
           "input_size": random.uniform(*input_size_range),
           "output_size": random.uniform(*output_size_range),
           "transmission_power": random.uniform(*transmission_power_range),
           "deadline": random.uniform(*deadline_range),
           "computational_demand": random.uniform(*computational_demand)
       }
       tasks.append(task)
   return tasks

# Generate y_{i,j} matrix (binary decision variables for link usage)
def generate_y_matrix(num_tasks, num_links):
   return [[random.choice([0, 1]) for _ in range(num_links)] for _ in range(num_tasks)]

def generate_z_matrix(num_tasks, num_fog_nodes):
   z_matrix = [[0 for _ in range(num_fog_nodes)] for _ in range(num_tasks)]
   for task_idx in range(num_tasks):
       assigned_node = random.randint(0, num_fog_nodes - 1)
       z_matrix[task_idx][assigned_node] = 1
   return z_matrix

def make_offload_decision(task, Tk_loc, Tkl_tx, Ek_loc, Ek_tx):
  if Tk_loc <= Tkl_tx and Ek_loc <= Ek_tx:
    xk = 0
  elif Tkl_tx <= Tk_loc and Ek_tx <= Ek_loc:
    xk = 1
  elif Tk_loc < Tkl_tx and Ek_tx < Ek_loc:
    if Tkl_tx <= task["deadline"]:
      xk = 1
    else:
      xk = 0
  else:
    if Tk_loc <= Tkl_tx:
      xk = 0
    else:
      xk = 1

  return xk

def calculate_delays_and_energy(task, Dk_f):
   # Local task completion time
   Tk_loc = task["computational_demand"] / Dk_f

   # Channel gain
   lg = 1 + ((task["transmission_power"] * 1.577e-8)/noise_power)
   rkl = bandwidth * math.log(lg, 2)

   # Uplink-data rate
   Tkl_tx = task["input_size"] / rkl

   # Local energy consumption
   Ek_loc = alpha * (Dk_f * Dk_f) * task["computational_demand"]

   # Transmission energy consumption
   Ek_tx = task["transmission_power"] * Tkl_tx

   return Tk_loc, Tkl_tx, Ek_loc, Ek_tx


def main():
   print(f"Number of IoT devices: {num_iot_devices}")
   tasks = generate_tasks(num_iot_devices)

   # First part: Make offloading decisions
   print("\nPart 1: Offloading Decisions")
   print("-" * 50)

   offload_decisions = []
   total_transmission_delay = 0
   total_processing_delay = 0
   total_local_energy = 0
   total_transmission_energy = 0

   for task_idx, task in enumerate(tasks):
       Tk_loc, Tkl_tx, Ek_loc, Ek_tx = calculate_delays_and_energy(task, Dk_f=16e6)
       xk = make_offload_decision(task, Tk_loc, Tkl_tx, Ek_loc, Ek_tx)
       offload_decisions.append(xk)

       print(f"\nTask {task_idx + 1}:")
       print(f"Local Processing Delay: {Tk_loc:.6f} seconds")
       print(f"Transmission Delay: {Tkl_tx:.6f} seconds")
       print(f"Local Energy Consumption: {Ek_loc:.6f} Joules")
       print(f"Transmission Energy Consumption: {Ek_tx:.6f} Joules")
       print(f"Decision (xk): {xk} ({'Offload' if xk == 1 else 'Local Processing'})")
       total_energy=Ek_loc*(1-xk)+Ek_tx*xk
       print(f"Total Energy Consumption: {total_energy:.6f} Joules")

   # Print first part summary
   print("\nPart 1 Summary:")
   print(f"Total tasks: {len(tasks)}")
   print(f"Tasks to be offloaded: {offload_decisions.count(1)}")
   print(f"Tasks for local processing: {offload_decisions.count(0)}")


if __name__ == "__main__":
   main()









import random

# Constants and Parameters
num_fog_nodes = 5  # Number of ECSs
bandwidth = 16 * 1e6  # Bandwidth in bits per second (B_l)
noise_power = 1e-10  # Noise power in Watts
num_iot_devices = 250  # Reduced for the example
input_size = 450 * 1e3  # Static input size in bits
output_size = 15 * 1e3  # Static output size in bits
computational_demand = 210 * 1e6  # Computational demand in cycles
transmission_power = 0.5  # Static transmission power in Watts
alpha = 1e-13  # Energy coefficient
deadline = 45  # Static deadline in seconds
graph = {  # Network graph (base stations and edges with weights)
    0: {1: 2, 2: 4},
    1: {0: 2, 2: 1, 3: 7},
    2: {0: 4, 1: 1, 3: 3, 4: 5},
    3: {1: 7, 2: 3, 4: 2},
    4: {2: 5, 3: 2}
}

# Generate tasks for IoT devices
def generate_tasks(num_tasks):
    tasks = []
    for _ in range(num_tasks):
        task = {
            "input_size": input_size,
            "output_size": output_size,
            "computational_demand": computational_demand,
            "transmission_power": transmission_power,
            "deadline": deadline,
        }
        tasks.append(task)
    return tasks

# Create ECSs
def create_ecs(num_ecs):
    ecs_list = [{"ecs_id": i, "capacity": 1e9} for i in range(num_ecs)]
    return ecs_list

# Perform DECO scheduling with randomized timings
def deco_scheduling(tasks, ecs_list, graph, bandwidth):
    assignments = []
    for i, task in enumerate(tasks):
        ecs_id = i % len(ecs_list)  # Round-robin assignment
        start_time = random.uniform(0, 10)  # Random start time between 0 and 10 seconds
        completion_time = start_time + random.uniform(0, 65)  # Random completion time between start_time and start_time + 65 seconds
        assignments.append({
            "ecs_id": ecs_id,
            "start_time": start_time,
            "completion_time": completion_time
        })
    return assignments

def main():
    # Generate tasks
    tasks = generate_tasks(num_iot_devices)

    # Create ECSs
    ecs_list = create_ecs(num_fog_nodes)

    # Perform DECO scheduling
    assignments = deco_scheduling(tasks, ecs_list, graph, bandwidth)

    total_completion_time = sum(a['completion_time'] for a in assignments)
    average_completion_time = total_completion_time / len(assignments) if assignments else 0

    # Count of tasks in outage
    outage_count = 0
    total_offloading_delay = 0  # Initialize total offloading delay
    total_energy_consumed = 0  # Initialize total energy consumed

    # Output results
    if assignments:
        print("\nTask Assignments:")
        for idx, assignment in enumerate(assignments):
            print(f"Task {idx + 1} → ECS {assignment['ecs_id']}")
            completion_time = assignment['completion_time'] - assignment['start_time']
            total_offloading_delay += completion_time  # Accumulate the offloading delay
            
            # Calculate energy consumed
            E_loc = alpha * computational_demand  # Energy for local computation
            E_tx = transmission_power * completion_time  # Energy for transmission
            total_energy = E_loc + E_tx  # Total energy for the task
            total_energy_consumed += total_energy  # Accumulate total energy consumed
            
            if completion_time > 50:  # Check if the completion time exceeds 50 seconds
                outage_count += 1
                print(f"  Start Time: {assignment['start_time']:.6f} seconds")
                print(f"  Completion Time: {assignment['completion_time']:.6f} seconds")
                print("  This task did not get executed as it took longer than 50 seconds.")
            else:
                print(f"  Start Time: {assignment['start_time']:.6f} seconds")
                print(f"  Completion Time: {assignment['completion_time']:.6f} seconds")
            
            print(f"  Energy Consumed: {total_energy:.6f} Joules")  # Print energy consumed for the task

        print("\nTotal Completion Time:", total_completion_time)
        print("Average Completion Time:", average_completion_time)
        print("Number of tasks in outage:", outage_count)
        print("Total Offloading Delay (Latency):", total_offloading_delay)
        print("Total Energy Consumed:", total_energy_consumed)
    else:
        print("No tasks were assigned.")

if __name__ == "__main__":
    main()

import numpy as np
import math

# Input parameters
Dk_f = 16 * 1e6  # CPU frequency in Hz
Tk_c = 210      # Computation workload in cycles
Bl = 10 * 1e6  # Bandwidth in Hz
Bw = 10 * 1e6    # Bandwidth in Hz
Tk_in = 300 * 1e3 # Input data size in bits
alpha = 1e-13        # Energy consumption factor
pk_tx = 0.5      # Transmission power in Watts
Tk_d = 30        # Deadline in seconds

# Local task completion time (Equation 1)
Tk_loc = Tk_c / Dk_f
print("Local Processing Delay of task Tk:", Tk_loc)

# Uplink data rate (Equation 3)
lg = 1 + ((0.5 * 1.577e-8) / (10 * 1e-10))
rkl = Bw * math.log(lg, 2)

# Transmission delay (Equation 3)
Tkl_tx = Tk_in / rkl
print("Transmission delay for sending data to nearest server:", Tkl_tx)

# Local energy consumption (Equation 9)
Ek_loc = alpha * (Dk_f**2) * Tk_c                                                                   # energy 1
print("Local Energy Consumption of task Tk:", Ek_loc)

# Transmission energy consumption (Equation 10)
Ek_tx = pk_tx * Tkl_tx                                                                              #energy 2
print("Energy Consumption for Transmission of task Tk:", Ek_tx)


# Decision variable calculation (Corrected logic)
if Tk_loc <= Tkl_tx and Ek_loc <= Ek_tx:  # Prioritize local processing if feasible
    xk = 0
elif Tkl_tx <= Tk_loc and Ek_tx <= Ek_loc:  # Offload if transmission is more efficient
    xk = 1
elif Tk_loc < Tkl_tx and Ek_loc < Ek_tx:  # Compare both, prioritize feasibility within the deadline
    if Tkl_tx <= Tk_d:
        xk = 1
    else:
        xk = 0
else:  # Otherwise, fallback to local processing
    if Tk_loc <= Tk_d:
        xk = 0
    else:
        xk = 1

print("")
print("The decision variable xk is:", xk)


#
Ek= Ek_loc * (1 - xk)  + Ek_tx * xk
print("energy consumption at fog ", Ek)







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


# Placeholder: Create ECSs
def create_ecs(num_ecs):
    ecs_list = [{"ecs_id": i, "capacity": 1e9} for i in range(num_ecs)]
    return ecs_list


# Perform DECO scheduling with randomized completion times
def deco_scheduling(tasks, ecs_list, graph, bandwidth):
    assignments = []
    for i, task in enumerate(tasks):
        ecs_id = i % len(ecs_list)  # Round-robin assignment
        start_time = i * 5.0  # Example start time
        # Randomize the completion time between 5 and 50 seconds
        completion_time = start_time + random.uniform(5, 50)
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

    # Output results
    total_completion_time = 0
    outaged_tasks = 0

    if assignments:
        print("\nTask Assignments:")
        for idx, assignment in enumerate(assignments):
            task_duration = assignment['completion_time'] - assignment['start_time']
            total_completion_time += task_duration
            print(f"Task {idx + 1} → ECS {assignment['ecs_id']}")
            if task_duration > 30:
                outaged_tasks += 1
                print(f"  Outaged Task: Task {idx + 1} exceeded 30 seconds (Duration: {task_duration:.6f} seconds)")
            else:
                print(f"  Start Time: {assignment['start_time']:.6f} seconds")
                print(f"  Completion Time: {assignment['completion_time']:.6f} seconds")

        average_completion_time = total_completion_time / len(assignments)
        print(f"\nSummary:")
        print(f"  Total Completion Time: {total_completion_time:.6f} seconds")
        print(f"  Average Completion Time: {average_completion_time:.6f} seconds")
        print(f"  Number of Outaged Tasks: {outaged_tasks}")
    else:
        print("No tasks were assigned.")


if __name__ == "__main__":
    main()

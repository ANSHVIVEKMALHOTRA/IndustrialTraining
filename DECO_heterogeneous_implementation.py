import numpy as np
import math

# Input parameters
Dk_f = 16 * 1e6  # CPU frequency in Hz
Tk_c = 210e2       # Computation workload in cycles
Bl = 10 * 1e6    # Bandwidth in Hz
Bw = 10 * 1e6    # Bandwidth in Hz
Tk_in = 300 * 1e3 # Input data size in bits
alpha = 1        # Energy consumption factor
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
Ek_loc = alpha * (Dk_f**2) * Tk_c
print("Local Energy Consumption of task Tk:", Ek_loc)

# Transmission energy consumption (Equation 10)
Ek_tx = pk_tx * Tkl_tx
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






import random
import math
import heapq  # For Dijkstra's algorithm

# Constants and Parameters
num_fog_nodes = 5  # Number of ECSs
bandwidth = 16 * 1e6  # Bandwidth in bits per second (B_l)
noise_power = 1e-10  # Noise power in Watts
num_iot_devices = 7  # Number of IoT devices/tasks
input_size_range = (300 * 1e3, 600 * 1e3)  # Input size range in bits
output_size_range = (10 * 1e3, 20 * 1e3)  # Output size range in bits
computational_demand = 210 * 1e6  # Computational demand in cycles
transmission_power_range = (0.1, 1)  # Transmission power range in Watts
deadline_range = (30, 60)  # Deadline range in seconds
graph = {  # Network graph (base stations and edges with weights)
    0: {1: 2, 2: 4},
    1: {0: 2, 2: 1, 3: 7},
    2: {0: 4, 1: 1, 3: 3, 4: 5},
    3: {1: 7, 2: 3, 4: 2},
    4: {2: 5, 3: 2}
}


# Generate random tasks for IoT devices
def generate_tasks(num_tasks):
    tasks = []
    for _ in range(num_tasks):
        task = {
            "input_size": random.uniform(*input_size_range),
            "output_size": random.uniform(*output_size_range),
            "computational_demand": computational_demand,
            "transmission_power": random.uniform(*transmission_power_range),
            "deadline": random.uniform(*deadline_range),
        }
        tasks.append(task)
    return tasks


# Create ECSs with initial available times
def create_ecs(num_fog_nodes):
    return [{"id": i, "available_time": 0, "processing_speed": 16e6} for i in range(num_fog_nodes)]


# Function to calculate transmission delay
def calculate_transmission_delay(task, bandwidth, transmission_power):
    lg = 1 + ((transmission_power * 1.577e-8) / noise_power)
    rkl = bandwidth * math.log(lg, 2)  # Uplink data rate
    t= task["input_size"] / rkl
    return t+((task["input_size"]+task["output_size"])/bandwidth)


# Function to calculate processing delay
def calculate_processing_delay(task, processing_speed):
    return task["computational_demand"] / processing_speed


# Dijkstra's algorithm for shortest path
def dijkstra(graph, start, end):
    queue = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))

    return distances[end]


# Assign tasks to ECSs using DECO
def deco_scheduling(tasks, ecs_list, graph, bandwidth):
    # Sort tasks by their deadline
    tasks.sort(key=lambda x: x["deadline"])
    print(tasks)
    assignments = []  # To store task assignments

    for task in tasks:
        min_delay = float('inf')
        selected_ecs = None

        for ecs in ecs_list:
            # Compute transmission delay
            transmission_delay = calculate_transmission_delay(
                task, bandwidth, task["transmission_power"]
            )

            # Compute queuing and processing delay
            processing_delay = calculate_processing_delay(task, ecs["processing_speed"])
            queuing_delay = ecs["available_time"]

            # Total delay
            total_delay = (
                transmission_delay
                + processing_delay
                + queuing_delay
            )

            # Select the ECS with the minimum delay
            if total_delay < min_delay:
                min_delay = total_delay
                selected_ecs = ecs

        # Assign task to the selected ECS
        if selected_ecs:
            assignments.append({
                "task": task,
                "ecs_id": selected_ecs["id"],
                "start_time": selected_ecs["available_time"],
                "completion_time": min_delay,
            })
            # Update the available time of the ECS
            selected_ecs["available_time"] = min_delay

    return assignments


def main():
    # Generate tasks for IoT devices
    print("Generating tasks for IoT devices...")
    tasks = generate_tasks(num_iot_devices)

    # Create ECSs
    print("Creating ECSs...")
    ecs_list = create_ecs(num_fog_nodes)
    print(tasks)
    # Perform DECO scheduling
    print("\nScheduling tasks using DECO...")
    assignments = deco_scheduling(tasks, ecs_list, graph, bandwidth)

    # Output results
    if assignments:
        print("\nTask Assignments:")
        for idx, assignment in enumerate(assignments):
            print(f"Task {idx + 1} → ECS {assignment['ecs_id']}")
            print(f"  Start Time: {assignment['start_time']:.6f} seconds")
            print(f"  Completion Time: {assignment['completion_time']:.6f} seconds")

        # Calculate scheduling metrics
        max_completion_time = max(a["completion_time"] for a in assignments)
        avg_completion_time = sum(a["completion_time"] for a in assignments) / len(assignments)

        print("\nScheduling Metrics:")
        print(f"Maximum Completion Time: {max_completion_time:.6f} seconds")
        print(f"Average Completion Time: {avg_completion_time:.6f} seconds")
    else:
        print("No tasks were assigned.")


if __name__ == "__main__":
    main()

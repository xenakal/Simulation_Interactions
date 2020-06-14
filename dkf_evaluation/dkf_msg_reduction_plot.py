# script to plot the measurements of file inovation_measurements

##### COLLECT MEASUREMENTS IN VARIABLES #######

measurements_file = open("INNOVATION_BOUND_evaluation")
number_of_iterations = 15

[measurements_file.readline() for _ in range(3)]

innovation_bounds = []
mean_local_mse = []
mean_global_mse = []
mean_percentage_dkf_messages = []

iteration_local_sum = 0
iteration_global_sum = 0
iteration_messages_sum = 0
first_iteration = True
while True:
    line = measurements_file.readline()
    if line == "":
        mean_local_mse.append(iteration_local_sum / number_of_iterations)
        mean_global_mse.append(iteration_global_sum / number_of_iterations)
        mean_percentage_dkf_messages.append(iteration_messages_sum / number_of_iterations)
        measurements_file.close()
        break

    elif line[0:8] == "SCENARIO":
        innovation_bounds.append(float(line[29:33]))
        if first_iteration:
            first_iteration = False
        else:
            mean_local_mse.append(iteration_local_sum / number_of_iterations)
            mean_global_mse.append(iteration_global_sum / number_of_iterations)
            mean_percentage_dkf_messages.append(iteration_messages_sum / number_of_iterations)
            iteration_local_sum = 0
            iteration_global_sum = 0
            iteration_messages_sum = 0

    elif line[1:10] == "ITERATION":
        pass

    elif line[2:7] == "local":
        iteration_local_sum += float(line[14:22])
    elif line[2:8] == "global":
        iteration_global_sum += float(line[14:22])
    elif line[2:12] == "percentage":
        iteration_messages_sum += float(line[31:35])*100

print("mean local mse: ", mean_local_mse)
print("mean global mse: ", mean_global_mse)
print("mean percentage of DKF messages: ", mean_percentage_dkf_messages)
print("innovation bounds: ", innovation_bounds)

local_global_diff_percentage = [100*(mean_local_mse[i] - mean_global_mse[i])/mean_local_mse[i] for i in range(len(mean_global_mse))]

##### PLOT GRAPH #######
import matplotlib.pyplot as plt

fig, ax1 = plt.subplots()

color = 'tab:blue'
ax1.set_xlabel('innovation lower bound [m]', fontsize=15)
ax1.set_ylabel('DKF messages [%]', color=color, fontsize=15)
ax1.plot(innovation_bounds, mean_percentage_dkf_messages, '--', color=color)
ax1.scatter(innovation_bounds, mean_percentage_dkf_messages, color=color)
ax1.tick_params(axis='y', labelcolor=color, labelsize=16)
ax1.tick_params(axis='x', labelsize=16)
plt.xticks(fontsize=16)


ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:red'
ax2.set_ylabel(r'$\Delta_{rmse}$ [%]', color=color, fontsize=15)  # we already handled the x-label with ax1
ax2.plot(innovation_bounds, local_global_diff_percentage, '--', color=color)
ax2.scatter(innovation_bounds, local_global_diff_percentage, color=color)
ax2.tick_params(axis='y', labelcolor=color, labelsize=16)
plt.grid(True)
"""
fig = plt.figure()
plt.scatter(innovation_bounds, mean_percentage_dkf_messages, label='percentage of DKF messages', facecolors='none', edgecolors='b')
plt.scatter(innovation_bounds, local_global_diff_percentage, label='local-global RMSE', facecolors='none', edgecolors='r')
plt.plot(innovation_bounds, mean_percentage_dkf_messages, '--', color='b')
plt.plot(innovation_bounds, local_global_diff_percentage, '--', color='r')

plt.ylabel('Normalized values')
plt.title('')
plt.tick_params(axis='x', labelsize=15.0)
plt.tick_params(axis='y', labelsize=18.0)
plt.xlabel("Innovation lower bound", fontsize=25)
plt.ylabel("Normalized values", fontsize=25)
plt.legend(loc='best')
plt.grid(True)
"""

fig.tight_layout()
plt.show()

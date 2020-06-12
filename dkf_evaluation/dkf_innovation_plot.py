# script to plot the measurements of file inovation_measurements

##### COLLECT MEASUREMENTS IN VARIABLES #######

measurements_file = open("MSE_vs_INNOVATION_LOWER_BOUND")
number_of_iterations = 20

[measurements_file.readline() for _ in range(3)]

innovation_bounds = []
mean_local_mse = []
mean_global_mse = []
mean_number_messages = []

iteration_local_sum = 0
iteration_global_sum = 0
iteration_messages_sum = 0
first_iteration = True
while True:
    line = measurements_file.readline()
    if line == "":
        mean_local_mse.append(iteration_local_sum / number_of_iterations)
        mean_global_mse.append(iteration_global_sum / number_of_iterations)
        mean_number_messages.append(iteration_messages_sum / number_of_iterations)
        measurements_file.close()
        break

    elif line[0:8] == "SCENARIO":
        print("scenario: ", float(line[29:33]))
        innovation_bounds.append(float(line[29:33]))
        if first_iteration:
            print("first")
            first_iteration = False
        else:
            mean_local_mse.append(iteration_local_sum / number_of_iterations)
            mean_global_mse.append(iteration_global_sum / number_of_iterations)
            mean_number_messages.append(iteration_messages_sum / number_of_iterations)
            iteration_local_sum = 0
            iteration_global_sum = 0
            iteration_messages_sum = 0

    elif line[1:10] == "ITERATION":
        pass

    elif line[2:7] == "local":
        iteration_local_sum += float(line[14:22])
    elif line[2:8] == "global":
        iteration_global_sum += float(line[14:22])
    elif line[2:7] == "numer":
        iteration_messages_sum += float(line[26:29])

print("mean local mse: ", mean_local_mse)
print("mean global mse: ", mean_global_mse)
print("mean number of messages: ", mean_number_messages)
print("innovation bounds: ", innovation_bounds)

##### NORMALISE DATA #######
max_local_mse = max(mean_local_mse)
max_global_mse = max(mean_global_mse)
max_sent_messages = max(mean_number_messages)
mean_local_mse = [_/max_local_mse*100 for _ in mean_local_mse]
mean_global_mse = [_/max_global_mse*100 for _ in mean_global_mse]
mean_number_messages = [_/max_sent_messages*100 for _ in mean_number_messages]

##### PLOT GRAPH #######
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
plt.scatter(innovation_bounds, mean_number_messages, label='number exchanged messages')
plt.scatter(innovation_bounds, mean_local_mse, label='local rmse')
plt.scatter(innovation_bounds, mean_global_mse, label='global rmse')
plt.plot(innovation_bounds, mean_number_messages)
plt.plot(innovation_bounds, mean_local_mse)
plt.plot(innovation_bounds, mean_global_mse)

# Add some text for labels, title and custom x-axis tick labels, etc.
plt.ylabel('Normalized values')
plt.title('')
plt.tick_params(axis='x', labelsize=15.0)
plt.tick_params(axis='y', labelsize=18.0)
plt.xlabel("Innovation lower bound", fontsize=25)
plt.ylabel("Normalized values", fontsize=25)
plt.legend(loc='best')


fig.tight_layout()

plt.show()

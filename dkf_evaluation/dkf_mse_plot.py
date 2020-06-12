# script to plot the measurements of file MSE_measurements

##### COLLECT MEASUREMENTS IN VARIABLES #######

measurements_file = open("MSE_measurements")
number_of_iterations = 5.0

[measurements_file.readline() for _ in range(4)]

mean_local_mse = []
mean_global_mse = []

iteration_local_sum = 0
iteration_global_sum = 0
while True:
    line = measurements_file.readline()
    if line == "":
        mean_local_mse.append(iteration_local_sum / number_of_iterations)
        mean_global_mse.append(iteration_global_sum / number_of_iterations)
        print("break")
        break

    elif line[0:8] == "SCENARIO":
        print("scenario")
        mean_local_mse.append(iteration_local_sum / number_of_iterations)
        print("mean local rmse: ", mean_local_mse[-1])
        mean_global_mse.append(iteration_global_sum / number_of_iterations)
        print("mean global rmse: ", mean_global_mse[-1])
        iteration_local_sum = 0
        iteration_global_sum = 0

    elif line[1:10] == "ITERATION":
        print("iteration")
        pass

    elif line[2:7] == "local":
        iteration_local_sum += float(line[14:22])
        print("local mse = ", float(line[14:22]))
        print("local sum = ", iteration_local_sum)
    elif line[2:8] == "global":
        iteration_global_sum += float(line[14:22])
        print("global mse = ", float(line[14:22]))
        print("global sum = ", iteration_global_sum)

print(mean_local_mse)
print(mean_global_mse)
##### PLOT GRAPH #######
import matplotlib.pyplot as plt
import numpy as np

labels = ['2', '3', '4', '5']

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width / 2, mean_local_mse, width, label='local RMSE')
rects2 = ax.bar(x + width / 2, mean_global_mse, width, label='global RMSE')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('RMSE [m^2]')
ax.set_title('')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.xaxis.set_tick_params(labelsize=15)
ax.yaxis.set_tick_params(labelsize=18)
ax.set_xlabel("Number of cameras", labelsize=18)
ax.set_ylabel("RMSE [m^2]", fontsize=20)
ax.legend()


def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('%.4f' % height,
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


autolabel(rects1)
autolabel(rects2)

fig.tight_layout()

plt.show()

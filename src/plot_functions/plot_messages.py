import matplotlib.pyplot as plt
import numpy as np
import re
from src import constants

def load_message_file(map_name,agent_id):
        constants.ResultsPath.folder = "../../results"
        constants.ResultsPath.name_simulation = map_name
        fichier = open(constants.ResultsPath.DATA_MESSAGES+"/message-agent-" + str(agent_id)+".txt", "r")


        lines = fichier.readlines()
        fichier.close()

        data = []
        for line in lines:
            if line[0] == "#":
                pass
            else:
                line = line.replace("\n", "")
                line = line.replace(" ", "")
                values = re.split(",", line)

                values[3] = re.split(":", values[3])[1]
                values[4] =  re.split(":", values[4])[1]
                data.append(values)
        return data

def filter_message_type(data,message_type):
    filtered_list = []

    for item in data:
        if item[2] == message_type:
            filtered_list.append(item)

    return filtered_list

def filter_send_received(data):
    filtered_send = []
    filtered_received = []

    for item in data:
        if item[1] == "sent":
           filtered_send.append(item)
        elif item[1] == "received":
           filtered_received.append(item)
        else:
            print("error")

    return filtered_send,filtered_received,len(filtered_send)+len(filtered_received)


def filter_and_plot(data,filters_names,ax1,ax2):

    all_data_send,all_data_received,n_all_data = filter_send_received(data)

    sizes_sent = []
    sizes_rec = []
    colors = ['g', 'b', 'r', 'c','k']

    for name,color in zip(filters_names,colors):
        data_send, data_rec, n_mes = filter_send_received(filter_message_type(data, name))
        sizes_sent.append(len(data_send)/len(all_data_send)*100)
        sizes_rec.append(len(data_rec)/len(all_data_received)*100)
        plot_message_time(ax1, data_send,color)
        plot_message_time(ax2, data_rec,color)

    ax1.legend(loc=4)
    ax1.legend(filters_names)
    ax1.set_title("Sent messages summary", fontsize=15, fontweight='bold')

    ax2.legend(loc=4)
    ax2.legend(filters_names)
    ax2.set_title("Received messages summary", fontsize=15, fontweight='bold')

    plot_message_bar(ax3, sizes_sent, filters_names, colors)
    plot_message_bar(ax4, sizes_rec, filters_names, colors)




def plot_message_time(ax, data,color):
    times = []
    senders= []
    for item in data:
        times.append(float(item[0]))
        senders.append("agent"+str(int(item[4])))

    sc1 = ax.scatter(times, senders,s=10,color=color) #, c=np.array(cov), cmap="hot", linewidth=0.01)
    ax.set_yticklabels(senders, rotation=20)
    ax.set_xlabel("time [s]", fontsize=10)

def plot_message_bar(ax,sizes,labels,colors):
    '''ax.pie(sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)'''
    width = .5
    ax.bar(labels, sizes, width,color=colors)
    ax.set_xticklabels(labels, rotation=20, ha='center')
    ax.set_ylabel("propotion [%]",rotation=90)

def plot_message_pie(ax, sizes, labels, colors):

    '''ax.pie(sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)'''

    ax.pie(sizes, labels=labels,
           autopct='%1.1f%%', shadow=False, startangle=90)


if __name__ == '__main__':
    data = load_message_file("My_new_map",0)
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle('Exchange messages', fontsize=17, fontweight='bold', y=0.98)
    fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)

    filter_and_plot(data,["heartbeat","agentEstimator","targetEstimator","loosing_target","tracking_target"],ax1,ax2)

    plt.show()




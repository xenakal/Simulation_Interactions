import matplotlib.pyplot as plt
import numpy as np
import re
from src import constants


def load_message_file(agent_id):
    fichier = open(constants.ResultsPath.DATA_MESSAGES + "/message-agent-" + str(agent_id) + ".txt", "r")

    lines = fichier.readlines()
    fichier.close()

    data = []
    for line in lines:
        print(line)
        if line[0] == "#":
            pass
        else:
            line = line.replace("\n", "")
            line = line.replace(" ", "")
            values = re.split(",", line)

            values[3] = re.split(":", values[3])[1]
            values[4] = re.split(":", values[4])[1]
            data.append(values)
    return data


def filter_message_type(data, message_type):
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

    return filtered_send, filtered_received, len(filtered_send) + len(filtered_received)


def number_messages_sent(data):
    return sum([1 for item in data if item[1] == "sent"])


def filter_and_plot(id, data, filters_names, colors):
    try:
        fig = plt.figure(figsize=(12, 10))
        fig.suptitle('Messages échangés', fontsize=17, fontweight='bold', y=0.98)
        fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, 3)
        ax4 = fig.add_subplot(2, 2, 4)

        all_data_send, all_data_received, n_all_data = filter_send_received(data)

        sizes_sent = []
        sizes_rec = []

        senders_label = []
        receiver_label = []
        for name, color in zip(filters_names, colors):
            data_send, data_rec, n_mes = filter_send_received(filter_message_type(data, name))
            if len(all_data_send) > 0:
                sizes_sent.append(len(data_send) / len(all_data_send) * 100)
            else:
                sizes_sent.append(len(data_send))

            if len(all_data_received) > 0:
                sizes_rec.append(len(data_rec) / len(all_data_received) * 100)
            else:
                sizes_sent.append(len(all_data_received))

            senders_label = plot_message_time(ax1, data_send, color, senders_label)
            receiver_label = plot_message_time(ax2, data_rec, color, receiver_label)

        # ax1.legend(filters_names,loc=4,fontsize="x-large")
        # ax1.set_title("messages envoyés", fontsize=15, fontweight='bold')

        # ax2.legend(filters_names,loc=3, fontsize="x-large")
        # ax2.set_title("messages reçus", fontsize=15, fontweight='bold')

        plot_message_bar(ax3, sizes_sent, filters_names, colors)
        plot_message_bar(ax4, sizes_rec, filters_names, colors)
        fig.savefig(constants.ResultsPath.PLOT_MESSAGE + "/message_agent_" + str(id))
    except:
        print("error in message plot creation")


def plot_message_time(ax, data, color, senders_label):
    times = []
    senders = []
    for item in data:
        times.append(float(item[0]))
        senders.append("agent" + str(int(item[4])))

    sc1 = ax.scatter(times, senders, s=10, color=color)  # , c=np.array(cov), cmap="hot", linewidth=0.01)

    for sender in senders:
        if sender not in senders_label:
            senders_label.append(sender)

    ax.set_yticklabels(senders_label, rotation=20)
    ax.set_xlabel("time [s]", fontsize=10)
    #ax.set_xbound(0,20)
    return senders_label


def plot_message_bar(ax, sizes, labels, colors):
    '''ax.pie(sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)'''
    width = .5
    ax.bar(labels, sizes, width, color=colors)
    ax.set_xticklabels(labels, rotation=20, ha='center')
    ax.set_ylabel("propotion [%]", rotation=90)


def plot_message_pie(ax, sizes, labels, colors):
    '''ax.pie(sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)'''

    ax.pie(sizes, labels=labels,
           autopct='%1.1f%%', shadow=False, startangle=90)


def get_num_dkf_messages_percentage(agent_id):
    data = load_message_file(agent_id)
    n_mess_dkf = number_messages_sent(filter_message_type(data, "info_DKF"))
    n_mess_tot = number_messages_sent(data)
    print("total = ", n_mess_tot, " dkf = ", n_mess_dkf, " ratio = ", n_mess_dkf/n_mess_tot)
    return float(n_mess_dkf)/float(n_mess_tot)


class MessagePlot:
    def __init__(self, agent_id):
        self.data = load_message_file(agent_id)
        self.id = agent_id
        self.colors = ['g', 'b', 'r', 'gold', 'c', 'k']
        self.names = ["heartbeat", "agentEstimation", "targetEstimation", "info_DKF", "loosing_target",
                      "tracking_target"]

    def plot(self):
        filter_and_plot(self.id, self.data, self.names, self.colors)


if __name__ == '__main__':
    constants.ResultsPath.folder = "../../results"
    constants.ResultsPath.name_simulation = "test1-Random_map_7884"
    plot_creator = MessagePlot(100)
    plot_creator.plot()

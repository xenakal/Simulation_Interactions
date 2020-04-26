import csv
import os
import shutil
import logging
from src import constants


def create_structur_to_save_data():

    shutil.rmtree(constants.ResultsPath.MAIN_FOLDER, ignore_errors=True)

    try:
        """Create the main folder to save the result after folder"""
        os.mkdir(constants.ResultsPath.MAIN_FOLDER)

        """Screen shot"""
        """---------------------------------------"""
        os.mkdir(constants.ResultsPath.DATA_SCREENSHOT)

        """LOG folder"""
        """---------------------------------------"""
        os.mkdir(constants.ResultsPath.LOG_FOLDER)
        os.mkdir(constants.ResultsPath.LOG_AGENT)
        os.mkdir(constants.ResultsPath.LOG_MEMORY)
        os.mkdir(constants.ResultsPath.LOG_KALMAN)


        """Create data and it subfolder"""
        """----------------------------"""
        os.mkdir(constants.ResultsPath.DATA_FOLDER)

        "create ideal folder and it subfolder"
        os.mkdir(constants.ResultsPath.DATA_IDEAL)
        os.mkdir(constants.ResultsPath.DATA_MEMORY_RELATED_TO_TARGET)
        os.mkdir(constants.ResultsPath.DATA_MEMORY_RELATED_TO_AGENT)
        os.mkdir(constants.ResultsPath.DATA_MESSAGES)

        """Create memory agent and it subfolder"""
        os.mkdir(constants.ResultsPath.DATA_MEMORY_AGENT_TARGET)
        """Create memory all agent and it subfolder"""
        os.mkdir(constants.ResultsPath.DATA_MEMORY_ALL_AGENT_TARGET)

        """Create subfolder in data ideal"""
        os.mkdir(constants.ResultsPath.DATA_STATIC_REGION)

        """Create folder Kalman and it subfolder"""
        os.mkdir(constants.ResultsPath.DATA_KALMAN)
        os.mkdir(constants.ResultsPath.DATA_KALMAN_GLOBAL)
        os.mkdir(constants.ResultsPath.DATA_KALMAN_DISTRIBUE)

        """Create folder prediction and it subfolder"""
        os.mkdir(constants.ResultsPath.DATA_KALMAN_FILTER)
        os.mkdir(constants.ResultsPath.DATA_KALMAN_GLOBAL_PREDICTION)
        os.mkdir(constants.ResultsPath.DATA_KALMAN_GLOBAL_PREDICTION_TPLUS1)
        os.mkdir(constants.ResultsPath.DATA_KALMAN_GLOBAL_PREDICTION_TPLUS2)

        """Create plot and it subfolder"""
        """----------------------------"""
        os.mkdir(constants.ResultsPath.PLOT_FOLDER)
        os.mkdir(constants.ResultsPath.PLOT_MEMORY_AGENT)
        os.mkdir(constants.ResultsPath.PLOT_MEMORY_ALL_AGENT)
        os.mkdir(constants.ResultsPath.PLOT_MESSAGE)
        os.mkdir(constants.ResultsPath.PLOT_AGENT_ESTIMATOR)

        os.mkdir(constants.ResultsPath.PLOT_KALMAN)
        os.mkdir(constants.ResultsPath.PLOT_KALMAN_GLOBAL)
        os.mkdir(constants.ResultsPath.PLOT_KALMAN_GLOBAL_FILTERED)
        os.mkdir(constants.ResultsPath.PLOT_KALMAN_PREDICTION)
        os.mkdir(constants.ResultsPath.PLOT_KALMAN_PREDICTION_T_PLUS_1)
        os.mkdir(constants.ResultsPath.PLOT_KALMAN_PREDICTION_T_PLUS_2)

        os.mkdir(constants.ResultsPath.PLOT_KALMAN_DISTRIBUE)
    except:
        print("file exist already")


def create_logger(path, name, agent_id):
    # log_room
    logger = logging.getLogger(name + str(agent_id))
    logger.setLevel(constants.LOG_LEVEL)

    # create file handler which log_messages even debug messages
    fh = logging.FileHandler(path + name + " -  agent " + str(agent_id) + " " + ".txt", "w+")
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log_message level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger_message
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def create_logger_save_data(path, name, agent_id):
    # log_room
    logger = logging.getLogger(name + str(agent_id))
    logger.setLevel(constants.LOG_LEVEL)

    # create file handler which log_messages even debug messages
    fh = logging.FileHandler(path + name + "-agent-"+str(agent_id)+".txt", "w+")
    # create console handler with a higher log_message level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger_message
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger



def save_in_csv_file(name, data_to_save):
    with open(name + ".csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data_to_save)


def save_in_csv_file_dictionnary(name, data_to_save):
    with open(name + ".csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data_to_save[0])
        writer.writeheader()
        for data in data_to_save[1]:
            writer.writerow(data)


def load_csv_file(name):
    data = []
    with open(name + ".csv", newline='') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            data.append(row)
    return data


def load_csv_file_dictionnary(name):
    data = []
    with open(name + ".csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

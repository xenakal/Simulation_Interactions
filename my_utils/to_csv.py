import csv
import os
import shutil
import constants

def create_structur_to_save_data():
    shutil.rmtree(constants.SavePlotPath.MAIN_FOLDER, ignore_errors=True)
    """Create the main folder to save the result after folder"""
    os.mkdir(constants.SavePlotPath.MAIN_FOLDER)

    """Create data and it subfolder"""
    """----------------------------"""
    os.mkdir(constants.SavePlotPath.DATA_FOLDER)

    """Create memory agent and it subfolder"""
    os.mkdir(constants.SavePlotPath.DATA_MEMORY_AGENT)

    """Create memory all agent and it subfolder"""
    os.mkdir(constants.SavePlotPath.DATA_MEMORY_ALL_AGENT)

    """Create folder Kalman and it subfolder"""
    os.mkdir(constants.SavePlotPath.DATA_KALMAN)
    os.mkdir(constants.SavePlotPath.DATA_KALMAN_GLOBAL)
    os.mkdir(constants.SavePlotPath.DATA_KALMAN_DISTRIBUE)

    """Create folder prediction and it subfolder"""
    os.mkdir(constants.SavePlotPath.DATA_PREDICTION)
    os.mkdir(constants.SavePlotPath.DATA_PREDICTION_TPLUS1)
    os.mkdir(constants.SavePlotPath.DATA_PREDICTION_TPLUS2)

    """Create plot and it subfolder"""
    """----------------------------"""
    os.mkdir(constants.SavePlotPath.PLOT_FOLDER)
    os.mkdir(constants.SavePlotPath.PLOT_MEMORY_AGENT)
    os.mkdir(constants.SavePlotPath.PLOT_MEMORY_ALL_AGENT)


def save_in_csv_file(name,data_to_save):
    with open(name+".csv", 'w',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data_to_save)


def save_in_csv_file_dictionnary(name,data_to_save):
    with open(name+".csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=data_to_save[0])
        writer.writeheader()
        for data in data_to_save[1]:
            writer.writerow(data)

def load_csv_file(name):
    data = []
    with open(name+".csv", newline='') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            data.append(row)
    return data

def load_csv_file_dictionnary(name):
    data = []
    with open(name+".csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data


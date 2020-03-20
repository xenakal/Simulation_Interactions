import csv

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


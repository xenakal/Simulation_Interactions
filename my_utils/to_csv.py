import csv

def save_in_csv_file(name,data_to_save):
    with open(name+".csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=data_to_save[0])
        writer.writeheader()
        for data in data_to_save[1]:
            writer.writerow(data)


from tkinter import filedialog
import csv


filename = filedialog.askopenfile()
print(filename.name)

with open(filename.name, 'r') as csv_file:
    reader = csv.reader(csv_file)
    list_of_votes = list(reader)

for vote in list_of_votes:
    print(vote)

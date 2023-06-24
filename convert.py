import re
import os

# Prototype to extract transactional data from Westpac transaction activity from web interface in csv file
fileName = "test.txt"
with open(fileName) as file:
    # assign date, transaction details, value, final cost

    for line in file:
        convert = line.strip()
        convert = convert.split('\t')
        convert = [item for item in convert if item.strip()]
        print(convert)


    
import re
import json
from datetime import datetime

# Prototype to extract transactional data from Westpac transaction activity from web interface in csv file
fileName = "test.txt"
storage = "data.json"
transData = []


with open(storage, "w+") as store:
    with open(fileName) as file:
        # assign Transdate, transaction details, value, final cost, Date

        for line in file:
            convert = line.strip()
            convert = convert.split('\t')
            convert = [item for item in convert if item.strip()]

            transDate = convert[0]
            transDate = str(datetime.strptime(transDate, '%d %b %Y'))[0:10]

            detail = convert[1]
            detail = re.sub(r'Click for details$', '', detail)
            date = re.findall(r'[0-9][0-9]/[0-9][0-9]$', detail)
            if (date == []):
                date = None
            else:
                date = ''.join(date)
            detail = (re.sub(r'[0-9][0-9]/[0-9][0-9]$', '', detail)).split()[3:]

            isExpense = True
            if (convert[2][0] == '$'):
                isExpense = False

            transDict = {
                "transDate": transDate,
                "date": date,
                "detail": ' '.join(detail),
                "transValue": convert[2],
                "finAmount": convert[3],
                "isExpense": isExpense
            }

            transData.append(transDict)
        jsonData = json.dumps(transData, indent=6)
        store.write(jsonData)
        # json.dump(transData, store)

    
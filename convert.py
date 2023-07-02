import re
import json
from datetime import datetime

# Prototype to extract transactional data from Westpac transaction activity from web interface in csv file
# input data from test.txt example below:
# 22 Jun 2023		EFTPOS DEBIT 0046656 KEBAB DELIGHT NSW KENSINGTON 22/06Click for details	-$15.00		$1,790.57


fileName = "test.txt"
storage = "test.json"
transData = []

with open(storage, "w") as store:
    with open(fileName) as file:
        # assign Transdate, transaction details, value, final cost, Date
        id = 1
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
                date = ''.join(date).replace("/", "-")
                # make date in transDate format
                date = transDate[:5] + date[-2:] + date[2:-2] + date[:2]

            detail = (re.sub(r'[0-9][0-9]/[0-9][0-9]$', '', detail)).split()[3:]
            isExpense = True
            transVal = convert[2]
            if (transVal[0] == '$'):
                isExpense = False
            else:
                transVal = float(transVal[2:].replace(",", ""))

            finalAmount = float(convert[3][1:].replace(",", ""))

            transDict = {
                "id": id,
                "transDate": transDate,
                "date": date,
                "detail": ' '.join(detail),
                "transValue": transVal,
                "finAmount": finalAmount,
                "isExpense": isExpense
            }
            #print(transDict)
            id += 1
            transData.append(transDict)
        jsonData = json.dumps(transData, indent=6)
        store.write(jsonData)
        # json.dump(transData, store)

    
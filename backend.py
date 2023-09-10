import psycopg2
import json
import matplotlib.pyplot as plt
import calendar
import datetime
import re
import json
import os
from datetime import datetime

tmpJson = "tmp.json"

with open('password.txt', 'r') as f:
    password = f.read()

# actions
# Drop table script
dropTrans = """
            DROP TABLE IF EXISTS transaction;
            """

# create transact table script
createTrans = """ CREATE TABLE IF NOT EXISTS transaction (
                    id INT PRIMARY KEY,
                    account VARCHAR(255),
                    finAmount FLOAT,
                    details VARCHAR(255),
                    transDate DATE,
                    date DATE,
                    transVal FLOAT,
                    isExpense BOOL); """

# insert transact table script
insertTrans = """ 
    INSERT INTO transaction (
    id, 
    account,
    finAmount, 
    details, 
    transDate, 
    date, 
    transVal, 
    isExpense) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""

# get latest finAmount of each month
getAmountMonthFunc = """    
    CREATE OR REPLACE FUNCTION get_amount_month(accName varchar(255))
    RETURNS TABLE (
        id INT,
        transDate date,
        finAmount float
    )
    AS $$
    DECLARE
        result_row record;
        year_row int;
    BEGIN
        FOR year_row in select distinct DATE_PART('year', t.transDate) as year 
            from transaction t
            order by year 

        LOOP
            raise notice 'year: %', year_row;

                FOR counter IN 1..12 LOOP
                SELECT *
                FROM transaction t
                WHERE DATE_PART('month', t.transDate) = counter and DATE_PART('year', t.transDate) = year_row and account = accName
                ORDER BY t.transDate DESC, id 
                LIMIT 1
                INTO result_row;

                IF FOUND THEN
                    -- Return the result_row
                    RETURN query select result_row.id, result_row.transDate, result_row.finAmount;
                END IF;
                END LOOP;

        END LOOP;

        RETURN;
    END;
    $$ LANGUAGE plpgsql;
"""

# convert txt file to a json file
def convert(fileName, accName):
    transData = []

    with open(tmpJson, "w") as store:
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
                    date = ''.join(date).replace("/", "-")

                    # make date in transDate format
                    date = transDate[:5] + date[-2:] + date[2:-2] + date[:2]

                detail = (re.sub(r'[0-9][0-9]/[0-9][0-9]$', '', detail)).split()[3:]
                isExpense = True
                transVal = convert[2]
                if (transVal[0] == '$'):
                    isExpense = False
                    transVal = float(transVal[1:].replace(",", ""))
                else:
                    transVal = float(transVal[2:].replace(",", ""))

                finalAmount = float(convert[3][1:].replace(",", ""))

                transDict = {
                    "account": accName,
                    "transDate": transDate,
                    "date": date,
                    "detail": ' '.join(detail),
                    "transValue": transVal,
                    "finAmount": finalAmount,
                    "isExpense": isExpense
                }
                transData.append(transDict)
            jsonData = json.dumps(transData, indent=6)
            store.write(jsonData)

# connect psycopg2
def connect():
    conn = psycopg2.connect(
        host="localhost",
        dbname="transact",
        user="postgres",
        password=password,
        port=5432
    )
    return conn

# create table and insert transact table
def setup(fileName, accName):

    convert(fileName, accName)
    
    conn = connect()
    cur = conn.cursor()

    # setup table
    cur.execute(createTrans)

    # setup functions for queries
    cur.execute(getAmountMonthFunc)

    # insert data from json to transact table
    with open(tmpJson, 'r') as file:
        data = json.load(file)
        for trans in data:

            # check if the details are unique compared to the database entries(transDate, detail)
            cur.execute("SELECT * FROM transaction WHERE transDate = %s AND details = %s", (trans['transDate'], trans['detail']))
            result = cur.fetchall()
            
            # no duplicates entry already in table
            if (len(result) == 0):

                ### TODO: unique id needs testing

                # define a entry id using largest id from records in table
                # if table is empty first id is 1
                cur.execute("SELECT * FROM transaction")
                if (len(cur.fetchall()) == 0):
                    curId = 1

                # else use the next largest id
                else:
                    cur.execute("SELECT id FROM transaction ORDER BY id DESC")
                    curId = cur.fetchone()[0]
                    curId += 1

                insertVal = (
                            curId,
                            trans['account'],
                            trans['finAmount'],
                            trans['detail'],
                            trans['transDate'],
                            trans['date'],
                            trans['transValue'],
                            trans['isExpense']
                            )
                cur.execute(insertTrans, insertVal)

    conn.commit()
    cur.close()
    conn.close
    os.remove(tmpJson)


# reset tables
def reset():
    conn = connect()
    cur = conn.cursor()
    cur.execute(dropTrans)
    conn.commit()
    cur.close()
    conn.close

def plotProto(plotName, accNames, startYear, endYear = None):
    conn = connect()
    cur = conn.cursor()
    records = {}

    for accName in accNames:
        getAmountMonth = "SELECT * FROM get_amount_month(" +"'" + accName + "'" +");"
        cur.execute(getAmountMonth)
        result = cur.fetchall()
        # print(result)

    # holds data separated by year, containing month and amount value
        # setup dictionary if empty
        if len(records) == 0:
            for res in result:
                records[res[1].year] = {}
    
        for res in result:
            # get year, month and val
            year = res[1].year
            month = res[1].month
            val = res[2]

            # check if month exists in that year
            if month in records[year]:
                
                # adds the old amount onto the new record
                oldAmount = records[year][month]
                # print(oldAmount)
                val = oldAmount + val

            # insert the new record
            records[year][month] = val

    x = []
    y = []

    # checks args to determine year display
    # if no endYear, display only the start year
    if endYear == None:

        # access month and amount in that year
        for month in records[startYear]:
            x.append(calendar.month_abbr[month])
            y.append(records[startYear][month])

        plt.figure(figsize=(10,10))
        plt.plot(x,y)
        plt.xlabel('Months', fontweight='bold', fontsize='12', labelpad=15)

        # account for multiple accounts
        if len(accNames) > 1:
            plt.title('Amount in ' + ', '.join(accNames) + ' during ' + str(startYear), fontweight='bold', fontsize='15', pad=15)
        else:
            plt.title('Amount in ' + accName + ' during ' + str(startYear), fontweight='bold', fontsize='15', pad=15)

    # take range of years
    else:
        # access month and amount in the range of years
        year = startYear
        while year <= endYear:

            # loop through months in each year
            for month in records[year]:
                x.append(str(year) + '/' + str(calendar.month_abbr[month])) 
                y.append(records[year][month])
            year += 1

        plt.figure(figsize=(10 * (endYear - startYear + 1), 10))
        plt.plot(x,y)
        plt.xlabel('Year/Month', fontweight='bold', fontsize='12', labelpad=15)

        # account for multiple accounts
        if len(accNames) > 1:
            plt.title('Amount in ' + ', '.join(accNames) + ' between ' + str(startYear) + ' and ' + str(endYear), fontweight='bold', fontsize='15', pad=15)
        else:
            plt.title('Amount in ' + accName + ' between ' + str(startYear) + ' and ' + str(endYear), fontweight='bold', fontsize='15', pad=15)

    # y axes account for multiple accounts
    if len(accNames) > 1:
        plt.ylabel('Amount in ' + ', '.join(accNames) + ' ($)', fontweight='bold', fontsize='12', labelpad=15)
    else: 
        plt.ylabel('Amount in ' + accName + ' ($)', fontweight='bold', fontsize='12', labelpad=15)

    # annotate the data points
    for x,y in zip(x,y):
        plt.annotate(
            f"{round(y, 2)}",
            (x,y),
            textcoords="offset points",
            xytext=(0,10),
            ha='center'
        )

    plt.savefig(plotName)
    plt.clf()

    # Line plot of transaction amount vs time (day, montly, yearly)
    
def printTable():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""select * from transaction;""")
    for record in cur:
        print(record)
    cur.close()
    conn.close()

def main():
    reset()
    setup('1.txt', 'acc1')
    setup('2.txt', 'acc2')

    plotProto('2020-2023 acc1', ['acc1'], 2020, 2023)
    plotProto('2020-2021 acc1', ['acc1'], 2020, 2021)
    plotProto('2020 acc1', ['acc1'], 2020)
    plotProto('2023 acc1', ['acc1'], 2023)

    plotProto('2020-2023 acc2', ['acc2'], 2020, 2023)
    plotProto('2020-2021 acc2', ['acc2'], 2020, 2021)
    plotProto('2020 acc2', ['acc2'], 2020)
    plotProto('2023 acc2', ['acc2'], 2023)

    plotProto('2020-2023 acc1+2', ['acc1', 'acc2'], 2020, 2023)
    plotProto('2020-2021 acc1+2', ['acc1', 'acc2'], 2020, 2021)
    plotProto('2020 acc1+2', ['acc1', 'acc2'], 2020)
    plotProto('2023 acc1+2', ['acc1', 'acc2'], 2023)

if __name__ == "__main__":
    main()


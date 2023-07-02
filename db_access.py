import psycopg2
import json

conn = psycopg2.connect(
    host="localhost",
    dbname="transact",
    user="postgres",
    password="123",
    port=5432
)
# start
cur = conn.cursor()

# actions
# create transact table script
createTrans = """ CREATE TABLE IF NOT EXISTS transaction (
                    id INT PRIMARY KEY,
                    finAmount FLOAT,
                    details VARCHAR(255),
                    transDate DATE,
                    date DATE,
                    transVal FLOAT,
                    isExpense BOOL); """
insertTrans = """ INSERT INTO transaction (
                    id, 
                    finAmount, 
                    details, 
                    transDate, 
                    date, 
                    transVal, 
                    isExpense) VALUES (%s, %s, %s, %s, %s, %s, %s);"""
cur.execute(createTrans)

# insert data from json to transact table
jsonLoc = "test.json"
with open(jsonLoc, 'r') as file:
    data = json.load(file)
    for trans in data:

        ### TODO: issue determine id of transaction before inserting, need to assign id at the convert.py part
        insertVal = (
                    trans['id'],
                    trans['finAmount'],
                    trans['detail'],
                    trans['transDate'],
                    trans['date'],
                    trans['transValue'],
                    trans['isExpense']
                    )
        print(insertVal)
        cur.execute(insertTrans, insertVal)
# end
conn.commit()
cur.close()
conn.close


# values = [(14, 'Ian', 78), (15, 'John', 88), (16, 'Peter', 92)]
 
# # cursor.mogrify() to insert multiple values
# args = ','.join(cursor.mogrify("(%s,%s,%s)", i).decode('utf-8')
#                 for i in values)
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
                    isExpense) VALUES (%s, %s, %s, %s, %s, %s, %s));"""
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
                    trans['details'],
                    trans['transDate'],
                    trans['date'],
                    trans['transVal'],
                    trans['isExpense']
                    )

# end
conn.commit()
cur.close()
conn.close
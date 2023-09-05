import psycopg2
import json

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
                    finAmount FLOAT,
                    details VARCHAR(255),
                    transDate DATE,
                    date DATE,
                    transVal FLOAT,
                    isExpense BOOL); """

# insert transact table script
insertTrans = """ INSERT INTO transaction (
                    id, 
                    finAmount, 
                    details, 
                    transDate, 
                    date, 
                    transVal, 
                    isExpense) VALUES (%s, %s, %s, %s, %s, %s, %s);"""


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

# reset tables
def reset():
    conn = connect()
    cur = conn.cursor()
    cur.execute(dropTrans)
    conn.commit()
    cur.close()
    conn.close

# create table and insert transact table
def setup():
    conn = connect()
    cur = conn.cursor()


    cur.execute(createTrans)

    # insert data from json to transact table
    jsonLoc = "test.json"
    with open(jsonLoc, 'r') as file:
        data = json.load(file)
        for trans in data:

            # check if the details are unique compared to the database entries(transDate, detail)
            cur.execute("SELECT * FROM transaction WHERE transDate = %s AND details = %s", (trans['transDate'], trans['detail']))
            result = cur.fetchall()
            if (len(result) == 0):
                ### TODO: issue determine id of transaction before inserting, need to assign id at the convert.py part

                cur.execute("SELECT if FROM transcation ORDER BY id DESC")
                curId = cur.fetchone()
                curId += 1

                insertVal = (
                            curId,
                            trans['finAmount'],
                            trans['detail'],
                            trans['transDate'],
                            trans['date'],
                            trans['transValue'],
                            trans['isExpense']
                            )
                #print(insertVal)
                cur.execute(insertTrans, insertVal)

    conn.commit()
    cur.close()
    conn.close





def main():
    # reset()
    setup()

    # print('setup done')
    conn = connect()
    cur = conn.cursor()

    # print('checking')

    cur.execute("""select * from transaction;""")
    for record in cur:
        print(record)
    cur.close()
    conn.close

if __name__ == "__main__":
    main()








# conn = psycopg2.connect(
#     host="localhost",
#     dbname="transact",
#     user="postgres",
#     password=password,
#     port=5432
# )
# # start
# cur = conn.cursor()


# cur.execute(createTrans)

# # insert data from json to transact table
# jsonLoc = "test.json"
# with open(jsonLoc, 'r') as file:
#     data = json.load(file)
#     for trans in data:

#         ### TODO: issue determine id of transaction before inserting, need to assign id at the convert.py part
#         insertVal = (
#                     trans['id'],
#                     trans['finAmount'],
#                     trans['detail'],
#                     trans['transDate'],
#                     trans['date'],
#                     trans['transValue'],
#                     trans['isExpense']
#                     )
#         #print(insertVal)
#         cur.execute(insertTrans, insertVal)
# # end
# conn.commit()
# cur.close()
# conn.close


# values = [(14, 'Ian', 78), (15, 'John', 88), (16, 'Peter', 92)]
 
# # cursor.mogrify() to insert multiple values
# args = ','.join(cursor.mogrify("(%s,%s,%s)", i).decode('utf-8')
#                 for i in values)


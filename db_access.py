import psycopg2
import json
import matplotlib.pyplot as plt

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

# get latest finAmount of each month
getAmountMonthFunc = """    CREATE OR REPLACE FUNCTION get_amount_month()
                        RETURNS TABLE (
                            id INT,
                            transDate date,
                            finAmount float
                        )
                        AS $$
                        DECLARE
                            result_row record;
                        BEGIN
                            FOR counter IN 1..12 LOOP
                                SELECT *
                                FROM transaction t
                                WHERE DATE_PART('month', t.transDate) = counter
                                ORDER BY t.transDate DESC, id 
                                LIMIT 1
                                INTO result_row;
                                
                                IF FOUND THEN
                                    -- Return the result_row
                                    RETURN query select result_row.id, result_row.transDate, result_row.finAmount;
                                END IF;
                            END LOOP;
                            
                            RETURN;
                        END;
                        $$ LANGUAGE plpgsql;    """

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

    # setup table
    cur.execute(createTrans)

    # setup functions for queries
    cur.execute(getAmountMonthFunc)

    # insert data from json to transact table
    jsonLoc = "test.json"
    with open(jsonLoc, 'r') as file:
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


def plotProto():

    conn = connect()
    cur = conn.cursor()

    # Line plot of amount in account vs time (day, monthly, yearly)
    # cur.execute("SELECT transDate, finAmount FROM transaction ORDER BY transDate ASC")
    getAmountMonth = "SELECT * FROM get_amount_month();"

    # cur.execute("SELECT finAmount, DATE_PART('year', transDate) as year, DATE_PART('month', transDate) as month FROM transaction")

    cur.execute(getAmountMonth)

    result = cur.fetchall()
    print(result)
    for res in result:
        print(res[2])
    # print(type(result))
    # for res in result:
    #     print(int(res[0]))
    # line plot based on month
    # for res in result:
        


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
    setup()
    plotProto()
    # printTable()

if __name__ == "__main__":
    main()


import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="transact",
    user="postgres",
    password="SProZer@117M",
    post=5432
)
# start
cur = conn.cursor()

# actionss
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS transaction (
        id INT PRIMARY KEY,
        amount FLOAT,
        details VARCHAR(255),
        transDate DATE,
        date DATE,
        transVal FLOAT,
        isExpense: BOOL
    );

    """
)


# end
conn.commit()
cur.close()
conn.close
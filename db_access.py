import psycopg2

hostname = 'localhost'
database = 'transact'
username = 'postgres'
pwd = 'admin'
port_id = 5433

psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port = port_id
)

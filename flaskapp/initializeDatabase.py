import csv
import sqlite3

conn = sqlite3.connect('Project2AWS.db')
cur = conn.cursor()
cur.execute("""DROP TABLE IF EXISTS AWSusers""")
cur.execute("""CREATE TABLE AWSusers
        (Username text, Password text, FirstName text, LastName text, Email text)""")

with open('AWSusers.csv', 'r') as f:
    reader = csv.reader(f.readlines()[1:]) # exclude header line
    cur.executemany("""INSERT INTO AWSusers VALUES (?,?,?,?,?)""",
            (row for row in reader))
conn.commit()
conn.close()

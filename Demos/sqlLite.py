import sqlite3 as sl

con = sl.connect('my-test.db') #Create and / or connect to a database (exsisting or not)

'''
#Once the table is created we don't need to run this again

#Create a table named user, with columns id, name and age
with con:
    con.execute("""
        CREATE TABLE USER (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER
        );
    """)

#only needed when we need to add new records to the database
sql = 'INSERT INTO USER (id, name, age) values(?, ?, ?)' #insert command of a new record
data = [
    (1, 'Alice', 21),
    (2, 'Bob', 22),
    (3, 'Chris', 23)
]

#actual insertion code
with con:
    con.executemany(sql, data)
'''

#Query the table and get the results
with con:
    data = con.execute("SELECT * FROM USER WHERE age <= 22")
    for row in data:
        print(row)
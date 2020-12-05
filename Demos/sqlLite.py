import sqlite3 as sl

#https://www.sqlitetutorial.net/sqlite-where/
#that link helped a lot

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

'''
#only needed when we need to add new records to the database
sql = 'INSERT INTO USER (id, name, age) values(?, ?, ?)' #insert command of a new record
data = [
	[4, 'Joe', 25]
]

try:
	#actual insertion code
	with con:
		con.executemany(sql, data)
except sqlite3.IntegrityError:
	print('yea')

with con:	
	data = con.execute("SELECT * FROM USER")
    #data = con.execute("UPDATE USER SET name = 'Bobby' WHERE id = 2")
	
	temp = data.fetchall()
	
	print( type(temp) )
	print( temp )

'''

#Query the table and get the results
test = "Bob"
with con:
    data = con.execute("SELECT * FROM USER WHERE name = '" + test + "'")
    for row in data:
        print(row)

	#or we can do
	#data.fetchall() to get all the rows in a list1

with con:
	con.execute("DELETE FROM USER WHERE id = 3")


	with con:
	data = con.execute("SELECT * FROM USER")

	print(data.fetchall())


sql = 'INSERT INTO USER (id, name, age) values(?, ?, ?)' #insert command of a new record
data = [
    (3, 'Chris', 23)
]

#actual insertion code
with con:
    con.executemany(sql, data)
'''

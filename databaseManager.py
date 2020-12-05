import sqlite3 as sl


DATABASE_NAME = 'manga.db'
TABLE_NAME = 'MANGA'
COLUMNS = ['MangaID', 'MangaName', 'LastUploadedTime', 'LastCheckedChapterID']

def connectDB():
	#create or connect to an existing database
	return sl.connect( DATABASE_NAME )


def initializeDB(connection):
	createDBstring = """
						CREATE TABLE MANGA (
							{} INTEGER NOT NULL PRIMARY KEY,
							{} TEXT,
							{} INTEGER,
							{} INTEGER
						);
					""".format(*COLUMNS) #the '*' unpacks the string (essentially make it a tupple, i guess)
	
	with connection:
		connection.execute( createDBstring )


#--------------------- RECORD ADDITION METHODS --------------------------------

def addRecord(data, connection):
	addRecString = 'INSERT OR IGNORE INTO ' + TABLE_NAME + ' ({}, {}, {}, {}) values(?, ?, ?, ?)'.format(*COLUMNS) #insert command of a new record

	#actual insertion code
	with connection:
		connection.executemany(addRecString, data)

#------------------------- GET METHODS --------------------------------

def getAllRecords(connection):
	data = None

	with connection:
		data = connection.execute("SELECT * FROM " + TABLE_NAME)

	return data.fetchall()


def getMangaByName(name, connection):
	data = None

	with connection:
		data = connection.execute("SELECT * FROM " + TABLE_NAME + "WHERE " + COLUMNS[1] + " = '" + name + "'")

	return data.fetchall()


def getMangaByID(id, connection):
	data = None

	with connection:
		data = connection.execute( "SELECT * FROM {} WHERE {} = {}".format(TABLE_NAME, COLUMNS[0], id) )
	
	return data.fetchall()


#--------------------- DELETE METHODS --------------------------------

def deleteMangabyName( name, connection ):
	with connection:
		connection.execute("DELETE FROM " + TABLE_NAME + "WHERE " + COLUMNS[1] + " = '" + name + "'")


def deleteMangabyID( id, connection ):
	with connection:
		connection.execute("DELETE FROM " + TABLE_NAME + "WHERE " + COLUMNS[0] + " = " + id)


#--------------------- UPDATE METHODS --------------------------------

def updateAllMangaData( id, data, connection ):
	# data has [MANGA-NAME, LAST-UPLOADED-TIME, LAST-CHECKED-CHAPTER-ID]
	updateString = """
					UPDATE 
						{} 
					SET 
						{} = '{}'
						{} = {}
						{} = {}
					WHERE
						{} = {}
					""".format( TABLE_NAME, COLUMNS[1], data[1], COLUMNS[2], data[2], COLUMNS[3], data[3], COLUMNS[0], id )
	with connection:
		connection.execute( updateString )


def updateCheckedData( id, data, connection ):
	# data has [LAST-UPLOADED-TIME, LAST-CHECKED-CHAPTER-ID]
	updateString = """
					UPDATE 
						{} 
					SET 
						{} = {}
						{} = {}
					WHERE
						{} = {}
					""".format( TABLE_NAME, COLUMNS[2], data[2], COLUMNS[3], data[3], COLUMNS[0], id )

	with connection:
		connection.execute( updateString )


def updateUploadTime( id, data, connection ):
	# data is LAST-UPLOADED-TIME only
	updateString = """
					UPDATE 
						{} 
					SET 
						{} = {}
					WHERE
						{} = {}
					""".format( TABLE_NAME, COLUMNS[2], data, COLUMNS[0], id )

	with connection:
		connection.execute( updateString )


def updateCheckedChapterId( id, data, connection ):
	# data is LAST-CHECKED-CHAPTER-ID only
	updateString = """
					UPDATE 
						{} 
					SET 
						{} = {}
					WHERE
						{} = {}
					""".format( TABLE_NAME, COLUMNS[3], data, COLUMNS[0], id )

	with connection:
		connection.execute( updateString )

def printDataBase():
	dbConnection = connectDB()
	data = getAllRecords(dbConnection)

	for item in data:
		print(item)

#printDataBase()
import sqlite3 as sl
from Record import Record 


DATABASE_NAME = 'manga.db'
TABLE_NAME = 'MANGA'
COLUMNS = ['MangaID', 'MangaName', 'LastCheckedChapterID']

def connectDB():
	#create or connect to an existing database
	return sl.connect( DATABASE_NAME )


def initializeDB(connection):
	createDBstring = """
						CREATE TABLE MANGA (
							{} INTEGER NOT NULL PRIMARY KEY,
							{} TEXT,
							{} INTEGER
						);
					""".format(*COLUMNS) #the '*' unpacks the string (essentially makes it a tupple, i guess)
	
	with connection:
		connection.execute( createDBstring )

def createRecord(recordData):
	return Record( recordData[0], recordData[1], recordData[2] )

def createRecordsFromData(data):
	records = []
	
	for record in data:
		records.append( createRecord( record ) )

	return records

#--------------------- RECORD ADDITION METHODS --------------------------------
#START

def addRecord(data, connection):
	addRecString = 'INSERT OR IGNORE INTO ' + TABLE_NAME + ' ({}, {}, {}) values(?, ?, ?)'.format(*COLUMNS) #insert command of a new record

	#actual insertion code
	with connection:
		connection.executemany(addRecString, data)

#END
#--------------------- RECORD ADDITION METHODS --------------------------------

#------------------------- GET METHODS --------------------------------
#START

def getAllRecords(connection):
	data = None

	with connection:
		data = connection.execute("SELECT * FROM " + TABLE_NAME)

	return createRecordsFromData( data.fetchall() )


def getMangaByName(name, connection):
	data = None

	with connection:
		data = connection.execute("SELECT * FROM " + TABLE_NAME + "WHERE " + COLUMNS[1] + " = '" + name + "'")

	return createRecordsFromData( data.fetchall() )


def getMangaByID(id, connection):
	data = None

	with connection:
		data = connection.execute( "SELECT * FROM {} WHERE {} = {}".format(TABLE_NAME, COLUMNS[0], id) )
	
	return createRecordsFromData( data.fetchall() )

#END
#------------------------- GET METHODS --------------------------------

#--------------------- DELETE METHODS --------------------------------
#START

def deleteMangabyName( name, connection ):
	with connection:
		connection.execute("DELETE FROM " + TABLE_NAME + "WHERE " + COLUMNS[1] + " = '" + name + "'")


def deleteMangabyID( id, connection ):
	with connection:
		connection.execute("DELETE FROM " + TABLE_NAME + "WHERE " + COLUMNS[0] + " = " + id)

#END
#--------------------- DELETE METHODS --------------------------------

#--------------------- UPDATE METHODS --------------------------------
#START

def updateAllMangaData( id, data, connection ):
	# data has [MANGA-NAME, LAST-CHECKED-CHAPTER-ID]
	updateString = """
					UPDATE 
						{} 
					SET 
						{} = '{}'
						{} = {}
					WHERE
						{} = {}
					""".format( TABLE_NAME, COLUMNS[1], data[1], COLUMNS[2], data[2], COLUMNS[0], id )
	with connection:
		connection.execute( updateString )

def updateMangaName( id, data, connection ):
	# data is MANGA-NAME
	updateString = """
					UPDATE 
						{} 
					SET 
						{} = '{}'
					WHERE
						{} = {}
					""".format( TABLE_NAME, COLUMNS[1], data, COLUMNS[0], id )
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

#END
#--------------------- UPDATE METHODS --------------------------------

def printDataBase():
	dbConnection = connectDB()
	data = getAllRecords(dbConnection)

	for item in data:
		print(item)

#printDataBase()
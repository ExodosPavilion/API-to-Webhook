import databaseManager as dbMan
import requests, discord, json, time
from requests.auth import HTTPBasicAuth 
from discord import Webhook, RequestsWebhookAdapter, File
from multiprocessing import Process
from Record import Record

JSON_DATA_FILE = "data.json"

AUTH_DATA = None
JSON_DATA = None

DB_CONNECTION = None

WEBHOOK = None


#----------------------- JSON FUNCTIONS ------------------------------
#START

def getJsonData(jsonFileName):
	'''
		Used to get JSON file data

		parameters:
			jsonFileName = file name of the JSON file
		
		returns:
			data = a dict of the JSON data
	'''
	data = None

	with open(jsonFileName, "r") as read_file:
		data = json.load(read_file)
	
	return data


def saveJsonData(data, jsonFileName):
	'''
		Used to save changes to JSON data
		
		parameters:
			jsonFileName = file name of the JSON file
		
		returns:
			None
	'''
	with open(jsonFileName, "w") as write_file:
		json.dump(data, write_file, indent=4)

#END
#----------------------- JSON FUNCTIONS ------------------------------

def getEnvironmentVariables():
	return	{
		'WEBHOOK_ID': int( os.getenv('WEBHOOK_ID') )
		'WEBHOOK_TOKEN': os.getenv('WEBHOOK_TOKEN'),

		'userID': int( os.getenv('userID') ),
		'mangadex_session': os.getenv('mangadex_session'),
		'mangadex_rememberme_token': os.getenv('mangadex_rememberme_token'),
		'User-Agent': os.getenv('User-Agent')
	}

def startUp():
	'''
		Run when the script is first run, used to get info to run properly

		parameters:
			None
		
		returns:
			auth_data = JSON data used to access to things like the discord webhook and mangadex MDList
			json_data = JSON data used to determine if the database is initialized and if the MDList data was added to the database or not
			webhook = discord webhook object allows the script to send data to the webhook
			db_connection = connection to the manga database
	'''
	
	auth_data = getEnvironmentVariables()
	'''
		will have the following 2 items:
		
		WEBHOOK_ID: id-number
		WEBHOOK_TOKEN: token
		
		userID: id of the user
		mangadex_session: the session id,
		mangadex_rememberme_token: the rememberme token,
		User-Agent: local useragent
	'''
	try:
		json_data = getJsonData(JSON_DATA_FILE)
	except FileNotFoundError:
		#since the JSON file would not exist
		json_data = { 'Database Created': False, 'MDList Added': False }
		saveJsonData(json_data, JSON_DATA_FILE) #save the JSON data
	'''
		will have the following 2 items:
		
		Database Created: whether the database was created or not
		MDList Added:  whether the MDList data added or not
	'''
	
	# Create webhook
	webhook = Webhook.partial(auth_data['WEBHOOK_ID'], auth_data['WEBHOOK_TOKEN'], adapter=RequestsWebhookAdapter())
	
	db_connection = dbMan.connectDB() #connect to the database
	
	#if the database was not initialized before
	if not ( json_data['Database Created'] ):
		dbMan.initializeDB(db_connection) #initialize database
		json_data['Database Created'] = True #set Database Created to true so that the it is not run the next time
		saveJsonData(json_data, JSON_DATA_FILE) #save the JSON data
	
	return auth_data, json_data, webhook, db_connection


#----------------------- API GET FUNCTIONS ------------------------------
#START

def getFollowedMangaAPIData():
	'''
		Get the MDList data
		
		parameters:
			None
		
		returns:
			dict of all the MDList data
	'''
	apiSite = 'https://mangadex.org/api/v2/user/{}/followed-manga'.format( AUTH_DATA['userID'] ) #MDList api site
	
	#header for the reqest being sent so that we get access to the MDList
	headers={}
	headers['Cookie'] = "mangadex_session={}; mangadex_rememberme_token={}".format( AUTH_DATA['mangadex_session'], AUTH_DATA['mangadex_rememberme_token'] )
	headers['User-Agent'] = AUTH_DATA['User-Agent']
	
	res = requests.get(apiSite, headers=headers) #get the API website
	res.raise_for_status()
	
	return json.loads( res.text )


def getMangaAPIData( mangaID ):
	'''
		Get the data from the manga api site
		
		parameters:
			mangaID = id of the manga whose data we need
		
		returns:
			dict of the manga API data
	'''
	apiSite = 'https://mangadex.org/api/v2/manga/{}'.format(mangaID) #manga API site
	
	res = requests.get(apiSite) #get the API website
	res.raise_for_status()
	
	return json.loads( res.text )


def getMangaChaptersAPIData( mangaID ):
	'''
		Get all the chapters of a particular manga
		
		parameters:
			mangaID = id of the manga whose chapter data we need
		
		returns:
			dict of the manga chapter API data
	'''
	apiSite = 'https://mangadex.org/api/v2/manga/{}/chapters'.format(mangaID) #manga chapters API site
	
	res = requests.get(apiSite) #get the API website
	res.raise_for_status()
	
	return json.loads( res.text )


def getChapterAPIData( chapterID ):
	'''
		Get the data of a particular chapter
		
		parameters:
			chapterID = id of the chapter whose data we need
		
		returns:
			dict of the chapter API data
	'''
	apiSite = 'https://mangadex.org/api/v2/chapter/{}'.format(chapterID) #chapter API site
	
	res = requests.get(apiSite) #get the API website
	res.raise_for_status()
	
	return json.loads( res.text )


def getEnglishChapters( mangaChapterAPIData ):
	'''
		Filter the manga chapters to only english chapters (gb)
		
		parameters:
			mangaChapterAPIData = what the getMangaChaptersAPIData function returns, essentially a dict / JSON data
		
		returns:
			englishChapters = a list of dicts that have manga chapters API data filtered to have only the english ones
	'''
	englishChapters = []

	for chapterData in mangaChapterAPIData['data']['chapters']:
		if chapterData['language'] == 'gb':
				englishChapters.append(chapterData)

	return englishChapters

#END
#----------------------- API GET FUNCTIONS ------------------------------

def prettyPrintJson( jsonData ):
	'''
		Print JSON data in way a human can read
		
		parameters:
			jsonData = the JSON data that needs to be printed
		
		returns:
			None
	'''
	print( json.dumps( jsonData, indent=4, sort_keys=False) )
	#enabling sort_keys (sort_keys = True) will change the order of the JSON data


def mdListToDB(dbConnection):
	'''
		Get the MDList data and add it to the manga database
		
		parameters:
			dbConnection = connection to the manga database
		
		returns:
			None
	'''
	followedManga = getFollowedMangaAPIData() #get the MDList JSON data
	
	print('Got MDList\n')
		
	listData = [] #used to store the data to be added
	
	totalItems = len( followedManga['data'] ) #how many manga are there to add to the database
	count = 1 #currently proccessing manga number
	
	for item in followedManga['data']:
		try:
			print('Adding (' + str(count) + '/' + str(totalItems) + '): ' + item['mangaTitle'])
			
			recordData = [] #list of the relevant data to added as a record to the database
			recordData.append( item['mangaId'] ) #the id of the manga
			recordData.append( item['mangaTitle'] ) #the name of the manga
			
			chapters = getEnglishChapters( getMangaChaptersAPIData( item['mangaId'] ) ) #get the intrested chapter data
			recordData.append( chapters[0]['id'] ) #the id of the latest english chapter
			print('\tGot latest manga')
			
			listData.append( recordData )
		except:
			#this a try except block so as to continue adding the data to listData
			count += 1
			continue
		
		count += 1
	
	dbMan.addRecord(listData, dbConnection) #add the data to the database


#---------------------------- UPDATE METHODS ----------------------------
#START

def updateOne(recordData, dbConnection):
	'''
		Check if a single managa has been updated with an english chapter
		
		parameters:
			recordData = record from the database
			dbConnection = connection to the manga database
		
		returns:
			updateDict = dict of relevant data to send to the webhook
	'''
	updateDict = {'mangaId': recordData.mangaID, 'mangaName': recordData.mangaName, 'updated': False, 'chapterLink': ''} 

	#recordData = dbMan.getMangaByID(mangaID, dbConnection) #get the manga data from the database

	print('Checking ' + updateDict['mangaName'])
	
	chaptersData = getEnglishChapters( getMangaChaptersAPIData(recordData.mangaID) ) #get the english chapter data
	
	#if the mangaid was found in the database AND the latest chapter id from the API data doesn't match the one stored in the database
	if chaptersData[0]['id'] != recordData.lastCheckedChapterID:
		dbMan.updateCheckedChapterId( recordData.mangaID, chaptersData[0]['id'], dbConnection ) #update the latest chapter id in the database
		updateDict['updated'] = True #set the updated value to true in the update dict
		updateDict['chapterLink'] = 'https://mangadex.org/chapter/' + chaptersData[0]['id'] #set the link to the chapter
	
	return updateDict


def checkForUpdates(dbConnection):
	'''
		Check if any of the manga stored in the database have been updated
		
		parameters:
			dbConnection = connection to the manga database
		
		returns:
			updateDicts = dict of relevant data to send to the webhook
	'''
	allRecords = dbMan.getAllRecords(dbConnection) #get the database records
	updateDicts = []

	for record in allRecords:
		updateDicts.append( updateOne( record, dbConnection) )
	
	return updateDicts

#END
#---------------------------- UPDATE METHODS ----------------------------


#---------------------------- WEBHOOK METHODS ----------------------------
#START

def runUpdatesToWebHook(webHook, dbConnection):
	'''
		Send messages to the channel the webhook is linked to about manga updates
		
		parameters:
			webHook = connection to the discord webhook
			dbConnection = connection to the manga database
		
		returns:
			None
	'''
	webHook.send('Checking for Updates') #send a message indicating that the script is checking for updates

	dataToSend = checkForUpdates(dbConnection) 
	
	for data in dataToSend:
		#if the manga has been updated
		if data['updated']:
			e = discord.Embed( title = data['mangaName'] )
			e.add_field( name="Link", value=data['chapterLink'] )
		
			webHook.send( embed=e )
	
	webHook.send( 'Update check finished' ) #send a message indicating that the script is finished checking

#END
#---------------------------- WEBHOOK METHODS ----------------------------


#-------------------- MULTI-THREAD RELATED METHODS --------------------
#START

def dailyUpdateCheck(webHook, dbCon):
	'''
		function that the multi-thread processers will use
		function will check for updates and send to the webhook every day
		
		parameters:
			webHook = connection to the discord webhook
			dbCon = connection to the manga database
		
		returns:
			None
	'''
	while True:
		runUpdatesToWebHook(WEBHOOK, dbCon)
		time.sleep(60 * 60 * 24) #sleep the function for 1 day (60 sec * 60 min * 24 hr)

def weeklyMDCheck(dbCon):
	'''
		function that the multi-thread processers will use
		function will check for changes to the MDList and add them to the database
		
		parameters:
			dbCon = connection to the manga database
		
		returns:
			None
	'''
	while True:
		time.sleep(60 * 60 * 24 * 7) #sleep the function for 7 days (60 sec * 60 min * 24 hr * 7 days)
		mdListToDB(dbCon)

#END
#-------------------- MULTI-THREAD RELATED METHODS --------------------

AUTH_DATA, JSON_DATA, WEBHOOK, DB_CONNECTION = startUp()

if not ( JSON_DATA['MDList Added'] ):
	mdListToDB(DB_CONNECTION) #add MDList data to database
	JSON_DATA['MDList Added'] = True #set MDList Added to true so that the it is not run the next time
	saveJsonData(JSON_DATA, JSON_DATA_FILE) #save the JSON data


process1 = Process(target=dailyUpdateCheck, args=(WEBHOOK, DB_CONNECTION,))
process2 = Process(target=weeklyMDCheck, args=(DB_CONNECTION,))
process1.start()
process2.start()
import databaseManager as dbMan
import requests, discord, json, time
from requests.auth import HTTPBasicAuth 
from discord import Webhook, RequestsWebhookAdapter, File
from multiprocessing import Process

GENERAL_AUTH_DATA_FILE = "authData.json"
JSON_DATA_FILE = "data.json"

AUTH_DATA = None
JSON_DATA = None

DB_CONNECTION = None

WEBHOOK = None

def getJsonData(jsonFileName):
	data = None

	with open(jsonFileName, "r") as read_file:
		data = json.load(read_file)
	
	return data


def saveJsonData(data, jsonFileName):
	with open(jsonFileName, "w") as write_file:
		json.dump(data, write_file, indent=4)



def startUp():
	auth_data = getJsonData(GENERAL_AUTH_DATA_FILE)
	'''
		will have the following 2 items:

		WEBHOOK_ID: id-number
		WEBHOOK_TOKEN: token
		
		userID: id of the user
		mangadex_session: the session id,
		mangadex_rememberme_token: the rememberme token,
		User-Agent: local useragent
	'''

	json_data = getJsonData(JSON_DATA_FILE)
	'''
		will have the following 2 items:

		Last_Checked_time: 1606572866,
		Intialized: false,
	'''

	# Create webhook
	webhook = Webhook.partial(auth_data['WEBHOOK_ID'], auth_data['WEBHOOK_TOKEN'], adapter=RequestsWebhookAdapter())

	db_connection = dbMan.connectDB()

	if not (json_data):
		dbMan.initializeDB(db_connection)
		mdListToDB(db_connection)
		json_data['Intialized'] = True
		saveJsonData(json_data, JSON_DATA_FILE)


	return auth_data, json_data, webhook, db_connection


#----------------------- API Get functions ------------------------------

def getFollowedMangaAPIData():
	apiSite = 'https://mangadex.org/api/v2/user/{}/followed-manga'.format( AUTH_DATA['userID'] )

	headers={}
	headers['Cookie'] = "mangadex_session={}; mangadex_rememberme_token={}".format( AUTH_DATA['mangadex_session'], AUTH_DATA['mangadex_rememberme_token'] )
	headers['User-Agent'] = AUTH_DATA['User-Agent']

	res = requests.get(apiSite, headers=headers)
	res.raise_for_status()

	return json.loads( res.text )


def getMangaAPIData( mangaID ):
	apiSite = 'https://mangadex.org/api/v2/manga/{}'.format(mangaID)

	res = requests.get(apiSite)
	res.raise_for_status()

	return json.loads( res.text )


def getMangaChaptersAPIData( mangaID ):
	apiSite = 'https://mangadex.org/api/v2/manga/{}/chapters'.format(mangaID)

	res = requests.get(apiSite)
	res.raise_for_status()

	return json.loads( res.text )


def getChapterAPIData( chapterID ):
	apiSite = 'https://mangadex.org/api/v2/chapter/{}'.format(chapterID)

	res = requests.get(apiSite)
	res.raise_for_status()

	return json.loads( res.text )


def prettyPrintJson( jsonData ):
	print( json.dumps( jsonData, indent=4, sort_keys=False) )

def getEnglishChapters( mangaChapterAPIData ):
	englishChapters = []

	for chapterData in mangaChapterAPIData['data']['chapters']:
		if chapterData['language'] == 'gb':
				englishChapters.append(chapterData)

	return englishChapters


def mdListToDB(dbConnection):
	followedManga = getFollowedMangaAPIData()
	print('Got MDList\n')
	listData = []
	totalItems = len( followedManga['data'] )
	count = 1

	for item in followedManga['data']:
		try:
			print('Adding (' + str(count) + '/' + str(totalItems) + '): ' + item['mangaTitle'])
			recordData = []
			recordData.append( item['mangaId'] )
			recordData.append( item['mangaTitle'] )
			
			mangaData = getMangaAPIData( item['mangaId'] )
			recordData.append( mangaData['data']['lastUploaded'] )
			print('\tGot Manga API data')

			chapters = getEnglishChapters( getMangaChaptersAPIData( item['mangaId'] ) )
			recordData.append( chapters[0]['id'] )
			print('\tGot latest manga')
			
			listData.append(recordData)
		except:
            print(item['mangaTitle'] + ' already in database')
			count += 1
			continue

		count += 1
	
	dbMan.addRecord(listData, dbConnection)


def updateOne(mangaID, dbConnection):
	updateDict = {'mangaId': mangaID, 'mangaName': '', 'updated': False, 'chapterLink': ''}

	recordData = dbMan.getMangaByID(mangaID, dbConnection)
	
	updateDict['mangaName'] = recordData[0][1]

	print('Checking ' + updateDict['mangaName'])
	
	chaptersData = getEnglishChapters( getMangaChaptersAPIData(mangaID) )
	
	if chaptersData[0]['id'] != recordData[0][3]:
		dbMan.updateCheckedChapterId( managaID, chaptersData[0]['id'], dbConnection )
		updateDict['updated'] = True 
		updateDict['chapterLink'] = 'https://mangadex.org/chapter/' + chaptersData[0]['id']
	
	return updateDict


def checkForUpdates(dbConnection):
	allRecords = dbMan.getAllRecords(dbConnection)
	updateDicts = []

	for record in allRecords:
		updateDicts.append( updateOne( int( record[0] ), dbConnection) )
	
	return updateDicts


def runUpdatesToWebHook(webHook, dbConnection):
	webHook.send('Checking for Updates')

	dataToSend = checkForUpdates(dbConnection)
	
	for data in dataToSend:
		if data['updated']:
			e = discord.Embed( title = data['mangaName'] )
			e.add_field( name="Link", value=data['chapterLink'] )
		
		webHook.send( embed=e )
	
	webHook.send( 'Update check finished' )


AUTH_DATA, JSON_DATA, WEBHOOK, DB_CONNECTION = startUp()

def dailyUpdateCheck(webHook, dbCon):
	while True:
		time.sleep(60 * 60 * 24)
		runUpdatesToWebHook(WEBHOOK, dbCon)

def weeklyMDCheck(dbCon):
	while True:
		time.sleep(60 * 60 * 24 * 7)
		mdListToDB(dbCon)


process1 = Process(target=dailyUpdateCheck, args=(WEBHOOK, DB_CONNECTION,))
process2 = Process(target=weeklyMDCheck, args=(DB_CONNECTION,))
process1.start()
process2.start()
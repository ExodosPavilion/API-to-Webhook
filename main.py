import databaseManager as dbMan
import requests, discord, json
from requests.auth import HTTPBasicAuth 
from discord import Webhook, RequestsWebhookAdapter, File

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
		Database Intialized: false,
	'''

	# Create webhook
	webhook = Webhook.partial(auth_data['WEBHOOK_ID'], auth_data['WEBHOOK_TOKEN'], adapter=RequestsWebhookAdapter())

	db_connection = dbMan.connectDB()

	if not (json_data):
		dbMan.initializeDB(DB_CONNECTION)
		json_data['Database Intialized'] = True
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
			count += 1
			continue

		count += 1
	
	dbMan.addRecord(listData, dbConnection)


def updateOne(mangaID, dbConnection):
	updateDict = {'mangaId': mangaID, 'mangaName': '', 'updated': False, 'chapterLink': ''}

	recordData = dbMan.getMangaByID(mangaID, dbConnection)
	
	updateDict['mangaName'] = recordData[0][1]
	
	chaptersData = getEnglishChapters( getMangaChaptersAPIData(mangaID) )
	
	if chaptersData[0]['id'] != recordData[3]:
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
		strToSend =  + ' status: '
		e = discord.Embed( title = data['mangaName'] )
		
		if data['updated']:
			e.add_field( name="Updated", value="Yes" )
			e.add_field( name="Link", value=data['chapterLink'] )
		else:
			e.add_field( name="Updated", value="No" )
		
		webHook.send( embed=e )



AUTH_DATA, JSON_DATA, WEBHOOK, DB_CONNECTION = startUp()

runUpdatesToWebHook(WEBHOOK, DB_CONNECTION)

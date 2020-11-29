import databaseManager as dbMan
import requests, discord, json
from requests.auth import HTTPBasicAuth 
from discord import Webhook, RequestsWebhookAdapter, File

GENERAL_AUTH_DATA_FILE = "accessData.json"
JSON_DATA_FILE = "data.json"


def getJsonData(jsonFileName):
	data = None

	with open(jsonFileName, "r") as read_file:
		data = json.load(read_file)
	
	return data


def saveJsonData(data, jsonFileName):
	with open(jsonFileName, "w") as write_file:
		json.dump(data, write_file, indent=4)



authData = getJsonData(GENERAL_AUTH_DATA_FILE)
'''
	will have the following 2 items:

	WEBHOOK_ID: id-number
	WEBHOOK_TOKEN: token
	
	userID: id of the user
	mangadex_session: the session id,
	mangadex_rememberme_token: the rememberme token,
	User-Agent: local useragent
'''

jsonData = getJsonData(JSON_DATA_FILE)
'''
	will have the following 2 items:

	Last_Checked_time: 1606572866,
	Database Intialized: false,
'''

# Create webhook
webhook = Webhook.partial(authData['WEBHOOK_ID'], authData['WEBHOOK_TOKEN'], adapter=RequestsWebhookAdapter())

dbConnection = dbMan.connectDB()

if !jsonData['Database Intialized']:
	dbMan.initializeDB(dbConnection)
	jsonData['Database Intialized'] = True
	saveJsonData(jsonData, JSON_DATA_FILE)


def getFollowedMangaAPIData():
	apiSite = 'https://mangadex.org/api/v2/user/{}/followed-manga'.format( authData['userID'] )

	headers={}
	headers['Cookie'] = "mangadex_session={}; mangadex_rememberme_token={}".format( authData['mangadex_session'], authData['mangadex_rememberme_token'] )
	headers['User-Agent'] = authData['User-Agent']

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
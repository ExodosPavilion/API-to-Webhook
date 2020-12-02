import requests, json
from requests.auth import HTTPBasicAuth 


def getJsonData(jsonFileName):
	data = None

	with open(jsonFileName, "r") as read_file:
		data = json.load(read_file)
	
	return data


def saveJsonData(data, jsonFileName):
	with open(jsonFileName, "w") as write_file:
		json.dump(data, write_file, indent=4)


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

def prettyPrintJson(jsonData):
        print( json.dumps( jsonData, indent=4, sort_keys=False) )

mangaId = 30461
chapters = getMangaChaptersAPIData(mangaId)


englishChapters = []

for chapterData in chapters['data']['chapters']:
        if chapterData['language'] == 'gb':
                englishChapters.append(chapterData)

prettyPrintJson(englishChapters)
print(len(englishChapters))

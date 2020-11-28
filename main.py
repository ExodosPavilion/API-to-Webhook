import requests, discord, json
from discord import Webhook, RequestsWebhookAdapter, File

WEBHOOK_ACCESS_DATA_FILE = "accessData.json"


def getJsonData(jsonFileName):
	data = None

	with open(jsonFileName, "r") as read_file:
		data = json.load(read_file)
	
	return data


webhookData = getJsonData(WEBHOOK_ACCESS_DATA_FILE)
'''
	will have the following 2 items:
	WEBHOOK_ID: id-number
	WEBHOOK_TOKEN: token
'''

# Create webhook
webhook = Webhook.partial(webhookData['WEBHOOK_ID'], webhookData['WEBHOOK_TOKEN'], adapter=RequestsWebhookAdapter())
 
# Send webhook message
webhook.send('test')
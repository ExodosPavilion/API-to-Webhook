import requests
import discord
from discord import Webhook, RequestsWebhookAdapter, File

WEBHOOK_ID = 687052430675935232
WEBHOOK_TOKEN = 'M9GbJRsMXpNxlNdEYgoA0fq-UiNa5RNGj79yyeReT-3gTJN-xtPSDrSWk-SxIDhM4Kk6'
CURRENT_TEMP = 0
imageName = 'testImage.png'

# Create webhook
webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
 
# Send temperature as text
webhook.send('Current Temp: ' + str(CURRENT_TEMP))
#Note that with this command you cannot do string + int. It is advised to "Build" the string before sending
 
# Upload image to server
webhook.send(file=discord.File(imageName))

print('done')

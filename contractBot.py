import discord
import asyncio
from parsers import ContractsParser

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
server_id = '273281172413480960'
channel_id = '278643145992830987'
bot_token = 'MjgwMTg2ODYzMDg2NDY5MTIw.C4Vurg.0BXWxATT1IW21pDYWg4-N6P00sI'

courier_channel_id = '281274282124771339'
fuel_channel_id = '281274423682531328'
other_channel_id = '278643145992830987'

client = discord.Client()
contracts_parser = ContractsParser()

@asyncio.coroutine
async def import_contracts():
    await client.wait_until_ready()

    while not client.is_closed:
        try:
            messages = contracts_parser.import_contracts()

            if len(messages) > 0:
                for message in messages:
                    if message['type'] == 'courier':
                        channel_id = courier_channel_id
                    elif message['type'] == 'fuel':
                        channel_id = fuel_channel_id
                    else:
                        channel_id = other_channel_id

                    await client.send_message(discord.Object(id=channel_id), message['message'])
                    asyncio.sleep(0.1)

                print('%d messages sent' % (len(messages)))
            else:
                print('No messages to send.')
        except Exception:
            print('Exception occurred! Sleeping...')
            raise

        # Sleep for 10 minutes
        await asyncio.sleep(10*60)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!fuelqueue') \
        or message.content.startswith('!fuelsummary'):
        active = message.content.startswith('!fuelqueue')
        await client.send_message(message.channel, contracts_parser.summarize_fuel(active))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.loop.create_task(import_contracts())
client.run(bot_token)

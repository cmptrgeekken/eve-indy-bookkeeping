import discord
import asyncio
from functions.contractsParser.contractsParser import ContractsParser

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
server_id = '273281172413480960'
channel_id = '278643145992830987'
bot_token = 'MjgwMTg2ODYzMDg2NDY5MTIw.C4Fv7g.zZj0B9EzHK7bfCXKQkjfoEyJ0dk'

contracts_parser = ContractsParser()

channel = discord.Object(id=channel_id)


client = discord.Client()

async def import_contracts():
    await client.wait_until_ready()

    while not client.is_closed:
        messages = contracts_parser.import_contracts()

        if len(messages) > 0:
            full_message = ""

            for message in messages:
                if len(message) + len(full_message) > 2000:
                    await client.send_message(channel, full_message)

                    full_message = message
                else:
                    full_message += '%s\r\n' % (message)

            await client.send_message(channel, full_message)

            print('%d messages sent' % (len(messages)))
        else:
            print('No messages to send.')

        await asyncio.sleep(60*60)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.loop.create_task(import_contracts())
client.run(bot_token)
# Modules
import discord
import sqlite3
import os
import dotenv

# Variables
dotenv.load_dotenv()
webhook_url = os.getenv('WEBHOOK_URL')
token = os.getenv('DISCORD_TOKEN')

# Bot functions
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

# On ready
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

# Run the client
client.run(token)

import discord
from discord.ext import commands
import sqlite3
import os
import dotenv

# Variables
dotenv.load_dotenv()
webhook_url = os.getenv('WEBHOOK_URL')
token = os.getenv('DISCORD_TOKEN')

# Bot
client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Bot events
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.command(name='hello', description='Say hello to the bot')
async def hello(ctx: commands.Context):
    await ctx.send('Hello!')

@client.command(name='add', description='Add two numbers')
async def add(ctx: commands.Context, num1: int, num2: int):
    result = num1 + num2
    await ctx.send(f'The sum of {num1} and {num2} is {result}')

# Run the client
client.run(token)

import discord
from discord.ext import commands
import sqlite3
import os
import dotenv
import time

# Variables
dotenv.load_dotenv()
webhook_url = os.getenv('WEBHOOK_URL')
token = os.getenv('DISCORD_TOKEN')

# addSubnet function create subnet database if it doesn't exist and adds a subnet to the database
def add_subnet(subnet):
    conn = sqlite3.connect('subnets.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS subnets (subnet TEXT, timestamp INTEGER)")
    c.execute("INSERT INTO subnets VALUES (?, ?)", (subnet, int(time.time())))
    conn.commit()
    conn.close()

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
    
### addSubnet command
@client.command(name='addSubnet', description='Add a subnet to the database')
async def add(ctx: commands.Context, subnet: str):
    # Check if the subnet is valid and if it has a valid range
    subnet_parts = subnet.split('.')
    if len(subnet_parts) != 4:
        await ctx.send('Invalid subnet')
        return
    # Check if there is a valid range
    if '/' not in subnet:
        await ctx.send('Invalid subnet')
        return
    # Add the subnet to the database
    add_subnet(subnet)
    print(f'Added subnet {subnet} to the database')
    await ctx.send(f'Added subnet {subnet} to the database :white_check_mark:')

### listSubnets command
@client.command(name='listSubnets', description='List all subnets in the database')
async def list_subnets(ctx: commands.Context):
    # Retrieve subnets from the database
    conn = sqlite3.connect('subnets.db')
    c = conn.cursor()
    c.execute("SELECT subnet FROM subnets")
    subnets = [row[0] for row in c.fetchall()]
    conn.close()
    # Create inline embed with all subnets
    embed = discord.Embed(title='Subnets', description='All subnets in the database', color=0x00ff00)
    subCount = 0
    for subnet in subnets:
        subCount += 1
        embed.add_field(name=f'Subnet {subCount}', value=subnet, inline=True)
    await ctx.send(embed=embed)


# Run the client
client.run(token)

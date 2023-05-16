import discord
from discord.ext import commands
import sqlite3
import os
import dotenv
import time

from scan import fullScan

# Variables

### MUST FIX DATABASE LOCKING ISSUE - CREATE DATABASE HANDLER
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

### listServers command
@client.command(name='listServers', description='List all servers in the database')
async def list_servers(ctx: commands.Context):
    # Retrieve servers from the database
    conn = sqlite3.connect('servers.db')
    c = conn.cursor()
    c.execute("SELECT ip, port FROM servers")
    servers = [row for row in c.fetchall()]
    conn.close()

    # Create a list to hold embeds
    embeds = []

    # Split servers into chunks to fit within embeds
    chunk_size = 10  # Adjust as needed
    server_chunks = [servers[i:i+chunk_size] for i in range(0, len(servers), chunk_size)]

    # Create embeds for each chunk of servers
    for i, chunk in enumerate(server_chunks):
        embed = discord.Embed(title='Servers', description='All servers in the database', color=0x00ff00)
        for j, server in enumerate(chunk):
            server_number = i * chunk_size + j + 1
            embed.add_field(name=f'Server {server_number}', value=f'IP: {server[0]}\nPort: {server[1]}', inline=True)
        embeds.append(embed)

    # Send embeds as separate messages
    for embed in embeds:
        await ctx.send(embed=embed)


### fullScan command
@client.command(name='fullScan', description='Scan all subnets in the database')
async def full_scan(ctx: commands.Context):
    # Count the number of servers in the database
    conn = sqlite3.connect('servers.db')
    c = conn.cursor()
    c.execute("SELECT ip, port FROM servers")
    servers = [row for row in c.fetchall()]
    conn.close()
    serverCount = len(servers)
    # Scan all subnets in the database
    fullScan()
    # New count of servers in the database
    conn = sqlite3.connect('servers.db')
    c = conn.cursor()
    c.execute("SELECT ip, port FROM servers")
    servers = [row for row in c.fetchall()]
    conn.close()
    newServerCount = len(servers)
    # Calculate the number of new servers
    newServers = newServerCount - serverCount
    # Send message to Discord
    await ctx.send(f'Full scan completed :white_check_mark:\nNew servers found: {newServers}')

# Run the client
client.run(token)

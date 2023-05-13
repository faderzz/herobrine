# Modules
import socket
import threading
import sqlite3
import time
import requests
import json
import dotenv
import os

# Variables
dotenv.load_dotenv()
webhook_url = os.getenv('WEBHOOK_URL')

# Create subnet database
def create_subnet_database():
    conn = sqlite3.connect('subnets.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS subnets (subnet TEXT, timestamp INTEGER)")
    conn.commit()
    conn.close()
create_subnet_database()

# Function to scan a specific IP address and port
def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set the timeout to 1 second
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"Port {port} is open on {ip}")
            add_server(ip, port)
        sock.close()
    except socket.error:
        pass

# Function to scan a subnet for Minecraft servers on multiple threads
def scan_subnet(subnet, port):
    subnet_parts = subnet.split('.')
    base_ip = '.'.join(subnet_parts[:3])

    for i in range(1, 256):
        ip = base_ip + '.' + str(i)
        threading.Thread(target=scan_port, args=(ip, port)).start()

# Main function
if __name__ == "__main__":
    # Retrieve subnets from the database
    conn = sqlite3.connect('subnets.db')
    c = conn.cursor()
    c.execute("SELECT subnet FROM subnets")
    subnets = [row[0] for row in c.fetchall()]
    conn.close()

    port = 25565  # Default Minecraft server port

    for subnet in subnets:
        scan_subnet(subnet, port)

def fullScan():
    # Retrieve subnets from the database
    conn = sqlite3.connect('subnets.db')
    c = conn.cursor()
    c.execute("SELECT subnet FROM subnets")
    subnets = [row[0] for row in c.fetchall()]
    conn.close()

    port = 25565  # Default Minecraft server port

    for subnet in subnets:
        scan_subnet(subnet, port)

### Database functions
# Create database if it doesn't exist
def create_database():
    conn = sqlite3.connect('servers.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS servers (ip TEXT, port INTEGER, timestamp INTEGER)")
    conn.commit()
    conn.close()

# Add server to database
def add_server(ip, port):
    create_database()
    conn = sqlite3.connect('servers.db')
    c = conn.cursor()
    timestamp = int(time.time())
    # Check if server already exists in database
    c.execute("SELECT * FROM servers WHERE ip=? AND port=?", (ip, port))
    if c.fetchone() is None:
        c.execute("INSERT INTO servers VALUES (?, ?, ?)", (ip, port, timestamp))
        send_webhook(ip, port)
        conn.commit()
    conn.close()

# Send embed to Discord webhook
def send_webhook(ip, port):
    data = {
        "embeds": [
            {
                "title": "Minecraft Server Found!",
                "description": f"IP: {ip}\nPort: {port}",
                "timestamp": str(time.strftime("%Y-%m-%dT%H:%M:%S.000Z")),
                "color": 16711680
            }
        ]
    }
    requests.post(webhook_url, json=data)

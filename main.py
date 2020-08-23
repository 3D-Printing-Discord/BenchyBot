import os
import discord
from discord.ext import commands
import sys
import platform
import datetime
import json
import bot_utils
import sqlite3
import TerminalLogger
import database

print(f"[✓] {os.path.basename(sys.argv[0])} Started")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ LOAD CONFIG VARIABLES ~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# LOAD CONFIG
try:
    with open('config.json') as f:
        config_data = json.load(f)
except:
    print("[✘] Config Read Failed. Please create config.json.")
    exit()

# LOAD ACCESS TOKEN
try:
    token = open("token.txt", "r").read()
    print(f"[✓] Token Read: {token}")
except:
    print("[✘] Token Read Failed. Please create token.txt with your access token.")
    exit()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ CHECK SYSTEM ~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# DISCORD.PY
print(f"[✓] Discord.py Version: {discord.__version__}")

# PYTHON VERSION
if sys.version_info[0] < 3 or sys.version_info[1] < 7:
    print(f"[✘] Python Version: {platform.python_version()}")
    print("[✘] Please run Python 3.7.0 or later")
    exit()
print(f"[✓] Python Version: {platform.python_version()}")

# CHECK DATABASE EXISTS
if os.path.isfile(config_data['database']):
    print("[✓] Database Found")
else:
    print("[X] Database Not Found! Try Running 'ini_database.py' to create the database.")
    exit()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ CREATE BOT ~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# SETUP BOT
bot = commands.Bot(command_prefix=config_data["prefix"], description=config_data['description'])

# ATTACH CONFIG DATA
bot.config = config_data

# ATTACH BOT INFO
bot.version = "v1.0.0"
bot.start_time = datetime.datetime.utcnow()

# CONNECT TO DATABASE
databasehandler = database.DatabaseHandler(config_data['database'])
bot.databasehandler = databasehandler

# CHECK FOR READY
@bot.event 
async def on_ready(): 
    print(f"[✓] Bot Ready! Logged in as {bot.user}")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~ IMPORT MODULES ~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("[!] LOADING MODULES:")

for module in config_data["modules"]:
    try:
        bot.load_extension(f"modules.{module}.{module}")
        print(f"   [✓] {module} Loaded")
    except:
        print(f"   [✘] ERROR Loading \'{module}\' module. Check config files.")

print("[✓] Modules Loaded")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~ RUN BOT ~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

try:
    bot.run(token)
except:
    print("[✘] Fatal Bot Runtime Exception")
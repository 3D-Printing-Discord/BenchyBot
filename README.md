# Discord Bot
This bot is designed to supply a core bot with a range of plug in 'modules' that can be used to alter the function to fit your needs. It is not currently optimised to run in multiple servers at once. Loading / unloading of modules during runtime allows updates to be made without having to close down the bot.

## Config
This bot takes a config file to set key parameters.

### Example Config
```
{
    "description": "BenchyBot",
    "log_level": "FULL",
    "prefix": "!",
    "modules": ["Blacklist", "Bot_Management", "CommandsDB", "DM", "Dynamic_Help", "Help_Hub", "ReactRoles", "Report", "Showcase", "Thanks"],
    "admin_roles": [640523571575259146],
    "mod_roles": [640523571575259146],
    "bot_log_channel": 695039236117889054,
    "database": "database.db"
}
```

## To Run This Bot
* Download the Repo.

* Create a virtual enviroment to run the bot. You can place it in the venv folder: 
```
python3 -m venv /venv/discord-venv
```

* Enter your virtual enviroment:
```
source /venv/discord-venv/bin/activate
```

* Install requirements:
```
pip install -r requirements.txt
```

* Install SQLite3:
```
sudo apt-get install sqlite3
```

* Configure your bot by changing the main config and module config files to suit your discord server. Create 'token.txt' with your access token. 

* Initilise the databse with:
```
python3 init_database.py
```

* Run the bot:
```
python3 bot.py
```

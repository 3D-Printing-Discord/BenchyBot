# Discord Bot
This bot is designed for the 3DPrinters discord server and consists of a core bot with a range of plug in 'modules' that can be used to alter the function to fit various needs. It is not currently optimised to run in multiple servers at once. Loading / unloading of modules during runtime allows updates to be made without having to close down the bot so service can be uninturrupted.

## Config
This bot takes a config file to set key parameters.

### Example Config
```
{
    "description": "Benchybot Mk2",
    "log_level": "FULL",
    "prefix": "?",
    "modules": ["Bot_Management", "Report", "ReactRoles", "Unit_Conversion", "DM", "Wiki", "CommandsDB", "Poll", "User_Management"],
    "admin_roles": [640523571575259146, 167872530860867586, 167872106644635648],
    "mod_roles": [724004523814682767, 260945795744792578],
    "bot_channels": [700421839872327741, 339978089411117076, 471446895089156108, 667463307963138058],
    "secret_channels": [],
    "bot_log_channel": 695039236117889054,
    "database": "database_prod.db"
}
```

## To Run This Bot
* Clone and open the repo.

* Create a virtual enviroment to run the bot. You can place it in the venv folder which is ignored by git: 
```
python3 -m venv /venv/discord-venv
```

* Enter your virtual enviroment:
```
On POSIX:
source /venv/discord-venv/bin/activate
```
```
On Windows (Powershell):
venv/discord-venv\Scripts\Activate.ps1
```

* Install requirements:
```
pip3 install -r requirements.txt
```

* Configure your bot by changing the main config and module config files to suit the discord server. 

* Create 'token.txt' with your access token. 

* Initilise the databse for chosen modules:
```
python3 init_database.py
```

* Run the bot:
```
python3 main.py
```

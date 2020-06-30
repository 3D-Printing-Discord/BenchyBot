# Bot Modules

This folder contains the bots modules which can be loaded and unloaded from the bot.

Each module should consist of the following structure:
* modules/
    * ModuleName/
        * readme.md (A readme file describing the module and its config)
        * ModuleName.py (Must be identical to the folder name but with a .py extension)
        * config.json (The module specific config file)
        * init_database.py (Use this script to initilise the databse for your modules requriements such as creating tables)
        * token.txt (Access tokens or other sensitive information should be stored in a token.txt file which is ignored by git)
        * any other required files for the module.

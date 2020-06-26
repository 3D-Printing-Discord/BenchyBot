# Bot Modules

This folder contains the bots modules which can be loaded and unloaded from the main bot config file.

Each module should consist of the following structure:
* modules/
    * ModuleName/
        * readme.md (A readme file describing the module and its config)
        * ModuleName.py (Must be identical to the folder name)
        * config.json (The module specific config file)
        * init_database.py (Use this script to initilise the databse for your modules requriements such as creating tables)
        * any other required files for the module.

# Blacklist Module

The Blacklist module removes messages containing a banned substring.

Banned substrings are stored in the database and can be changed through bot commands.

## Config
This module loads a json config file and requires an initilised database.

### blacklist_message: string
String sent as a direct message to users when their message is removed. Use a blank string to disable this feature. You can use discord markdown here.

### Example config:
```json
{
    "blacklist_message": "Your recent message was removed due to containing a blacklisted term. If you beleive this was an error please contact a mod."
}
```
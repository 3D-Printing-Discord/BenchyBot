# Direct Message

The Direct Message module forwards DMs sent to the bot to a specified channel. This can be useful as a "contact the mods" tool.

## Config
This module loads a json config file.

### bot_mail_channel: int
The channel to forward bot messages to. Must be an int.

### bot_response: string
The bots response to messages. Useful to confirm messages have been received. Use a blank string ("") to disable the response.

### Example config:
```json
{
    "bot_mail_channel": 694903299316514916,
    "bot_response": "Message Received!"
}
```
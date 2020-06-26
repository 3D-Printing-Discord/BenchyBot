# Dynamic Help

The Dynamic-Help module manages a number of help channels.

Help channels are allocated to users if a message is sent to an available channel. The channel is closed automatically after a period of inactivity or after either a mod or the channel owner uses the `!solved` command.

## Config
This module loads a json config file.

### help_channels: [list]
The channels for the plugin to manage. Must be provided as a list (even if only a single channel is to be used) of the channel IDs. Channels will be numbered in the order they are listed.

### timout: int
The timeout of the channel in seconds. Timeout is disabled with a value of 0. 

### channel_name: string
The names to be used for the help channels. This string can use tags to input data:

* <\emoji>: Replaced with the status emoji,
* <\number>: Replaced with the channel number,
* <\status>: Repalaced with the status of the channel (either "Available" or the owners name)

### available_message: string
Is the string that is sent in the embed on available channels. You can use discord markdown for formatting. Use \n for newlines.

### direct_message: string
The string that is sent to users when they claim a channel. Enter a blank string ("") to disable. 

### multiple_message: string
The string that is sent to users when they attempt to claim more than one channel.

### offline_message: string
A string sent to the help channels when the bot is shut down.

### Example config:
```json
{
    "help_channels": [700121596987179091, 700121607619739718, 700121616486629447, 708068535292919868, 708068557979648071, 708068562727600228],
    "timeout": 60,
    "channel_name": "<emoji>Help-<number>-<status>",
    "available_message": "This help channel is now **available**, which means that you can claim it by simply typing your question into it. Once claimed, the channel will be yours until it has been inactive for 10 seconds. When that happens it will be made available again for another user.\n\nTry to write the best question you can by providing a detailed description and telling us what you've tried already.",
    "direct_message": "**You have been allocated a help channel.**\n\nThis channel is now yours until it has been innactive for **10 mins**. If your question isn't answered before the channel times out feel free to claim another available channel.\n\nIf your question is resolved **please release the channel by sending the `!solved` command.** This will allow someone else to use the channel.",
    "multiple_message": "You may only claim one help channel at a time. If you are done with your other channel you can close it with `!solved`.",
    "offline_message": "The bot is offline. Help channels will not be allocated. You may still use the help channels."
}
```
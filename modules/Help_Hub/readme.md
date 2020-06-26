# Help Hub

The Help-Hub module manages a number of help channels and a central help-hub.

Help channels are allocated to users from the help hub (using the `!topic` command) which is also used as a contents of currently open help topics. Channels are locked after a period of inactivity.

## Config
This module loads a json config file.

### help_hub: int
The channel ID for the help hub channel.

### help_channels: list
A list of channel IDs for the bot to manage as part of the help hub. 

### timout: int
The number of seconds before channel timout.

### closed_message
The string content of the embed sent to closed channels.

### channel_name: string
The names to be used for the help channels. This string can use tags to input data:

* <\emoji>: Replaced with the status emoji,
* <\number>: Replaced with the channel number,
* <\status>: Repalaced with the status of the channel (either "Available" or the owners name)

### wrong_channel_message: string
The bot response when the `!topic` command is used outside of the help-hub.

### Example config:
```json
{
    "help_hub": 686177877829746787,
    "help_channels": [686701126132826146, 686701142846996530, 686701157212618806, 686701178440253453],
    "timeout": 30,
    "channel_name": "<emoji>｜Help-<number>-<status>",
    "closed_message": "This channel is now closed. If you have a question you can open a new help channel by posting in the help-hub.",
    "wrong_channel_message": "Use this command in the help-hub to get help!"
}
```
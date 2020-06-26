# Showcase Module

The showcase module removes any messages without attachments in a specified channel.

## Config

### showcase_channels: list
Takes a list of channel IDs to use showcase mode on. Must be a list, even for single channels.

### showcase_message: string
A string sent to memebers when their message is deleted by this module.

### Example config:
```json
{
    "showcase_channels": [700456705682702392],
    "showcase_message": "Your recent message was removed as it does not contain an image. The showcase channels are specifically for showcasing work and not for discussion"
}
```
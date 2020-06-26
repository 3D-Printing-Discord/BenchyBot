# Report Module 

The Report module allows users to report messages through a reaction.

## Config
This module loads a json config file.

### report_channel: int
The ID of the channel to log reports to. 

### report_message: string
The message sent to the user making the report.

### report_emoji: string
The name of the report emoji on the server. 

### Example config:
```json
{
    "report_channel": 694903299316514916,
    "report_message": "Your report has been received. Your report reaction has been automatically removed to maintain anonymity.\nYour report will be reviewed as soon as possible",
    "report_emoji": ":report:"
}
```
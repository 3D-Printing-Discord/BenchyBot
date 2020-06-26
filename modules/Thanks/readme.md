# Template Module

The thanks module lets users thank other users by reacting with an emoji to messages.

## Config
This module loads a config JSON and requires database access. 

### check_message: string
Message sent when the user queries how much thanks they have.

### check_message_none: string
Message sent when the user checks their thanks but doesnt have any.

### thanks_detected: string
String that is sent when a message on the server contains the string "thanks". Useful to notify people of the existance of this function. Can be disabled by setting an empty string: `""`

Example config:
```json
{
    "check_message": "Thanks for making the server a great place!",
    "check_message_none": "Thanks are awarded for when you help people out!",
    "thanks_detected": "Looks like you might be thanking someone. You can record your thanks by reacting with the :thanks: emoji to their message!"
}
```
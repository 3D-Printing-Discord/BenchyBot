# Long Service Module

The long service module will award roles to users based on their time in the server. 

## Config
This module loads a JSON config file. The file includes nested keys and must be constructed correclty.

### servers: dict
The servers key is a dict of each server you want the module to run on.

### * server_name: dict
The server name is a human readable server name and can be any value. It contains a dict of all the info for the server.

### * * server_id: int
The server ID

### * * roles: dict
This key includes a dict of all the roles that are to be allocated for this server.

### * * * role_name: dict
The role name is a human readable role name and can be any value. It contains a dict that holds all of the role information. 

### * * * * role_id: int
The id of the role to be allocated after the period of time has elapsed.

### * * * * days:int
The number of days after becoming a server member the role is awarded.

### * * * * message: string
The message sent to the user when the role is awarded. Use a string of "" to disable this feature.

Example config:
```json
{
    "servers": {
        "Eds_Test_Server": {
            "server_id": 640522864214278155,
            "roles": {
                "100-day-award":{
                    "role_id": 712788392022376478,
                    "days": 100,
                    "message": "You have now been a part of Eds Test Server for 100 days! You have been allocated the 100+ role! This does nothing. Dont get excited."
                },
                "250-day-award":{
                    "role_id": 712955122845614121,
                    "days": 250,
                    "message": "You have now been a part of Eds Test Server for 250 days! You have been allocated the 250+ role! This does nothing. Dont get excited."
                },
                "500-day-award":{
                    "role_id": 712955169876344863,
                    "days": 500,
                    "message": "You have now been a part of Eds Test Server for 500 days! You have been allocated the 500+ role! This does nothing. Dont get excited."
                }
            }
        }
    }
}
```
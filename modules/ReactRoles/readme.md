# React Roles Module

The react roles module manages members roles through reactions.

## Config
This module does not load a json config file. Widgets are created and configured through discord commands. This module uses flag arguments. 

### --title
The title of the created embed.

### --text
The main text of the embed.

### --roles
The roleIDs to be controlled by the embed. Provided as a string, roles seperated by spaces. Max 15 roles per embed. You must supply some roles. 

### --emoji
The emojis to use with the embed sent as a space seperated list of unicode emoji. (Note not all emoji are supported by discord.) If not emoji flag is supplied a default set of emoji will be used. 

### Example Command
```
!create_reaction_roles_widget 

--title="Add your own roles!" 

--text="To add a role react to this message with the following emojis." 

--roles="703295162532495451 703295239196246036 711347154412765198 711347156166115329"
```
import discord
from discord.ext import tasks, commands
import json
import datetime
import bot_utils

DEBUG = True

class Help_Channel():
    def __init__(self, bot, id):
        self.bot = bot

        self.id = id
        self.channel_object = bot.get_channel(id)

        self.owner = None
        self.title_update_at = None
        self.new_topic = False

    def __str__(self):
        return f"Help Channel: {str(self.channel_object)}"

    async def title_update(self, title):
        # SET TIMESTAMP
        self.title_update_at = datetime.datetime.utcnow()

        # SET CHANNEL NAME
        await self.channel_object.edit(name=title)

    def generate_channel_name(self, **replacements):
        new_name = self.config_data['channel_name']

        for k, v in kwargs.items():
            new_name = new_name.replace(f"<{k}>", str(v))

        return new_name

class Dynamic_Help(commands.Cog):
    version = "v1.0.0"

    def __init__(self, bot):
        self.bot = bot

        # GET CONFIG DATA
        self.config_data = []
        with open('modules/Dynamic_Help/config.json') as f:
            self.config_data = json.load(f)

        # CREATE VARIABLES
        self.help_channel_list = {}
        for i, chan_id in enumerate(self.config_data['help_channels']):
            self.help_channel_list[chan_id] = Help_Channel(self.bot, chan_id)

        for i in self.help_channel_list.values():
            if DEBUG: print(i)

        self.owner =     [None for i in self.config_data['help_channels']]
        self.pins =      [None for i in self.config_data['help_channels']]
        self.title_update_at = [None for i in self.config_data['help_channels']]
        self.new_topic = [True for i in self.config_data['help_channels']]

        # CREATE EMBEDS
        self.available_embed = discord.Embed(title="Channel Available", description=self.config_data['available_message'], color=bot_utils.green)
        self.closed_embed = discord.Embed(title="Channel Closed", description=self.config_data['closed_message'], color=bot_utils.red)
        self.directMessage_embed = discord.Embed(title="Channel Allocated", description=self.config_data['direct_message'], color=bot_utils.green)

        # START BACKGROUND TASKS
        if self.config_data['timeout'] != 0:
            self.background_ActivityCheck.start()

    @commands.Cog.listener()
    async def on_message(self, message):

        if DEBUG: print("--- RUNNING ON_MESSAGE LISTENER IN DYANMIC HELP ---")

        # CHECK IF USER IS THE BOT
        if message.author == self.bot.user:
            if DEBUG: print("  - User is the bot")
            return

        # CHECK IF ITS A COMMAND
        if message.content[:1] == self.bot.config['prefix']:
            if DEBUG: print("  - Message Not Is A Command")
            return

        # CHECK IF ITS IN A HELP CHANNEL
        if message.channel.id not in self.config_data['help_channels']:
            if DEBUG: print("  - Message Not In Help Channel")
            return

        # GET CHANNEL NUMBER
        channel_number = self.config_data['help_channels'].index(message.channel.id)
        if DEBUG: print(f"  - Channel Number: {channel_number}")

        # GET USER_NAME
        user_name = self.get_name(message.author)
        if DEBUG: print(f"  - User Name: {user_name}")

        # CHECK IF CHANNEL IS AVAILABLE
        if not self.owner[channel_number] == None:
            if DEBUG: print(" - CHANNEL NOT AVAILABLE")
            
            # CHECK IF OWNER
            if not self.owner[channel_number] == user_name:
                # UPDATE TITLE
                if DEBUG: print(" - NON-OWNER MESSAGE")

                if self.new_topic[channel_number]:
                    self.new_topic[channel_number] = False
                    if DEBUG: print(" - CHANGING NAME: NON-OWNER MESSAGE")
                    await self.update_channel_name(message.channel, emoji="❕", number=(channel_number+1), status=self.owner[channel_number])
                    self.title_update_at[channel_number] = datetime.datetime.utcnow()
            
            return
            
        # CHECK IF REQUESTER ALREADY OWNS A CHANNEL
        if user_name in self.owner:
            if DEBUG: print(" - Sender already owns a channel")
            await message.delete()
            await message.author.send(self.config_data['multiple_message'])
            return

        # ----- ALLOCATE CHANNEL -----
        # SET OWNER
        if DEBUG: print("  - Setting Owner")
        self.owner[channel_number] = user_name
        self.title_update_at[channel_number] = datetime.datetime.utcnow()

        # SET CHANNEL NAME
        if DEBUG: print("  - Setting Channel Name")

        await self.update_channel_name(message.channel, emoji="❗", number=(channel_number+1), status=user_name)
        if DEBUG: print("  - Channel Name Set")

        if self.config_data['pin_messages'] == "True":
            if DEBUG: print("  - Pinning Message")
            await message.pin()
            self.pins[channel_number] = message

        # SEND DM
        if DEBUG: print("  - Sending DM")
        if not self.config_data['direct_message'] == "":
            await message.author.send(embed=self.directMessage_embed)        

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def end_help(self, message):
        '''
        Ends Dynamic Help and resets the help names.
        '''
        for index, channel in enumerate(self.config_data['help_channels']):
            target_channel = self.bot.get_channel(channel)
            await target_channel.edit(name=f"help-{index+1}")
            await target_channel.send(self.config_data['offline_message'])

        self.bot.unload_extension(f"modules.Dynamic_Help.Dynamic_Help")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def setup_help(self, ctx):
        '''
        Makes all help channels available. (Admin-Only)
        '''

        for channel in self.config_data['help_channels']:
            target_channel = self.bot.get_channel(channel)
            await self.close_channel(target_channel)

    @commands.command()
    async def solved(self, ctx):
        '''
        Command to close an open help channel that is no longer required.
        '''

        # CHECK IF IN HELP CHANNEL
        if ctx.channel.id not in self.config_data['help_channels']:
            return

        # GET USERNAME
        user_name = self.get_name(ctx.author)

        # GET CHANNEL NUMBER 
        channel_number = self.config_data['help_channels'].index(ctx.channel.id)

        # CHECK CHANNEL IS OPEN
        if self.owner[channel_number] == None:
            return

        # IF OWNER OR MOD
        if self.owner[channel_number] == user_name or await bot_utils.is_mod(ctx):
            await self.close_channel(ctx.channel)
        else:
            await ctx.send("Sorry, you dont have permission to do that.")

    @tasks.loop(seconds=10)
    async def background_ActivityCheck(self):

        print(f" -- RUNNING ACTIVITY CHECK -- ")

        # AWAIT BOT TO BE READY
        await self.bot.wait_until_ready()

        temp_chan = "\n     ".join( [ str(i) for i in self.config_data['help_channels'] ] )
        print(f" -- CHECKING HELP CHANNELS --\n     {temp_chan}")

        print(" -- LOOPING OVER CHANNELS -- ")

        # LOOP OVER ALL CHANNELS IN LIST
        for index, c in enumerate(self.config_data['help_channels']):
            print("     ------------------------------")

            print(f"     INDEX: {index}\n     ID: {c}")

            # GET THE CHANNEL OBJECT
            channel_object = self.bot.get_channel(c)

            print(f"     CHANNEL OBJECT: {channel_object}")

            # IF CHANNEL HAS A LAST MESSAGE
            if channel_object.last_message == None:
                continue 

            print(f"     LAST MESSAGE: {channel_object.last_message}")

            # CONVERT EMBEDS DICTS 
            embeds_dict = [i.to_dict() for i in channel_object.last_message.embeds]

            # CHECK IF LAST MESSAGE IS THE AVAILABLE DICT
            if self.available_embed.to_dict() in embeds_dict: 
                continue
                
            print(f"     EMBED MATCHES")

            # GET TIME SINCE LAST MESSAGE 
            seconds_since_last_message = (datetime.datetime.utcnow() - channel_object.last_message.created_at).total_seconds()
            print(f"     SECONDS OF INACTIVITY: {seconds_since_last_message}")

            # CHECK IF TIMEOUT CONDITION HAS HAPPENED
            if seconds_since_last_message < self.config_data['timeout']:
                continue
        
            # CLOSE CHANNEL
            print(f"     CHANNEL CLOSING")
            await self.close_channel(channel_object)

        print(f"Owners: {self.owner}")
        print(f"Channels: {self.config_data['help_channels']}")
        print("---------------------------------")

    async def close_channel(self, channel_object):
        print("Closing Channel")
        channel_number = self.config_data['help_channels'].index(channel_object.id)

        # CHECK IF CHANNEL HAS HAD AN UPDATE IN THE LAST 10 MINS - THIS IS TO AVOID THE RATE LIMIT FOR CHANGING CHANNEL NAMES
        seconds_open = (datetime.datetime.utcnow() - self.title_update_at[channel_number]).total_seconds()
        if seconds_open < 600: 

            # CLOSE THE CHANNEL
            await channel_object.send(embed=self.closed_embed)
            await channel_object.set_permissions(channel_object.guild.default_role, send_messages=False)

            # AWAIT 10 MIN PERIOD 
            await discord.utils.sleep_until(self.title_update_at[channel_number] + datetime.timedelta(seconds=600))

            # RE-OPEN CHANNEL
            await channel_object.set_permissions(channel_object.guild.default_role, send_messages=True)

        # REMOVE OWNER
        self.owner[channel_number] = None
        self.new_topic[channel_number] = True

        await self.update_channel_name(channel_object, emoji="✅", number=(channel_number+1), status="available")

        if self.config_data['pin_messages'] == "True":
            if self.pins[channel_number] != None: 
                await self.pins[channel_number].unpin()

        await channel_object.send(embed=self.available_embed)

    def get_name(self, author):
        if author.nick == None: 
            name = author.name
        else: 
            name = author.nick

        return name

    async def update_channel_name(self, channel_object, **kwargs):
        if DEBUG: print("  --- Updating Channel Name ---")

        channel_number = self.config_data['help_channels'].index(channel_object.id)
        self.title_update_at[channel_number] = datetime.datetime.utcnow()

        new_name = self.config_data['channel_name']

        for k, v in kwargs.items():
            new_name = new_name.replace(f"<{k}>", str(v))

        if DEBUG: print(f"      - Channel Name Generated as: {new_name}")

        await channel_object.edit(name=new_name)

        return new_name

def setup(bot):
    bot.add_cog(Dynamic_Help(bot))
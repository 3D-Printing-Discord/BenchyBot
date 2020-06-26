import discord
from discord.ext import tasks, commands
import json
import datetime
import bot_utils

DEBUG = False

class Help_Channel():
    version = "v1.0"

    def __init__(self, bot, discord_id, channel_number, config_data, channel_id):
        self.bot = bot
        self.config_data = config_data

        self.discord_id = discord_id
        self.channel_id = channel_id

        self.channel_number = channel_number

        self.owner = None
        self.title_update_at = None
        self.new_topic = False

        # CREATE EMBEDS
        self.available_embed = discord.Embed(title="Channel Available", description=self.config_data['available_message'], color=bot_utils.green)
        self.closed_embed = discord.Embed(title="Channel Closed", description=self.config_data['closed_message'], color=bot_utils.red)
        self.directMessage_embed = discord.Embed(title="Channel Allocated", description=self.config_data['direct_message'], color=bot_utils.green)

    def __str__(self):
        return f"Help Channel: {str(self.bot.get_channel(self.channel_id))}"

    async def close_channel(self):

        # CHECK IF CHANNEL HAS HAD AN UPDATE IN THE LAST 10 MINS - THIS IS TO AVOID THE RATE LIMIT FOR CHANGING CHANNEL NAMES
        seconds_open = (datetime.datetime.utcnow() - self.title_update_at).total_seconds()
        if seconds_open < 600: 

            channel_object = self.bot.get_channel(self.channel_id)

            # CLOSE THE CHANNEL
            await channel_object.send(embed=self.closed_embed)
            await channel_object.set_permissions(channel_object.guild.default_role, send_messages=False)
            if self.new_topic:
                await self.title_update(emoji="❕", status="Closed")

            # AWAIT 10 MIN PERIOD 
            await discord.utils.sleep_until(self.title_update_at + datetime.timedelta(seconds=600))

            # RE-OPEN CHANNEL
            await channel_object.set_permissions(channel_object.guild.default_role, send_messages=True)


        await self.release_channel()

        if self.config_data['pin_messages'] == "True":
            pinned_messages = await channel_object.pins()
            for pinned_message in pinned_messages: 
                await pinned_message.unpin()

        await channel_object.send(embed=self.available_embed)

    async def title_update(self, **replacements):
        # COMPLETE REPLACEMENTS
        new_name = self.config_data['channel_name']
        for k, v in replacements.items():
            new_name = new_name.replace(f"<{k}>", str(v))

        new_name = new_name.replace("<number>", str(self.channel_number))

        # SET TIMESTAMP
        self.title_update_at = datetime.datetime.utcnow()

        # SET CHANNEL NAME
        await self.bot.get_channel(self.channel_id).edit(name=new_name)

    async def allocate_channel(self, user_name):
        self.owner = user_name
        self.new_topic = True
        await self.title_update(emoji="❗", status=user_name)

    async def release_channel(self):
        self.new_topic = True
        self.owner = None
        await self.title_update(emoji="✅", status="available")



class Dynamic_Help(commands.Cog):
    version = "v1.0.0"

    def __init__(self, bot):
        self.bot = bot

        # GET CONFIG DATA
        self.config_data = []
        with open('modules/DynamicHelp/config.json') as f:
            self.config_data = json.load(f)

        # CREATE CHANNELS DICT
        self.help_channel_list = {}
        for index, chan_id in enumerate(self.config_data['help_channels'], start=1):
            self.help_channel_list[chan_id] = Help_Channel(self.bot, chan_id, index, self.config_data, chan_id)

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

        # GET USER_NAME
        user_name = self.get_name(message.author)
        if DEBUG: print(f"  - User Name: {user_name}")

        # CHECK IF CHANNEL IS AVAILABLE
        if not self.help_channel_list[message.channel.id].owner == None:
            if DEBUG: print(" - CHANNEL NOT AVAILABLE")
            
            # CHECK IF OWNER
            if self.help_channel_list[message.channel.id].owner != user_name:

                # UPDATE TITLE
                if DEBUG: print(" - NON-OWNER MESSAGE")
                if self.help_channel_list[message.channel.id].new_topic:

                    if DEBUG: print(" - CHANGING NAME: NON-OWNER MESSAGE")
                    await self.help_channel_list[message.channel.id].title_update(emoji="❕", status=user_name)
            
            return
            
        # CHECK IF REQUESTER ALREADY OWNS A CHANNEL
        if any(user_name == x.owner for x in self.help_channel_list.values()):
            if DEBUG: print(" - Sender already owns a channel")
            await message.delete()
            await message.author.send(self.config_data['multiple_message'])
            return

        # ----- ALLOCATE CHANNEL -----
        # ALLOCATE CHANNEL
        if DEBUG: print("  - Allocating Channel")
        await self.help_channel_list[message.channel.id].allocate_channel(user_name)

        # PIN MESSAGE
        if self.config_data['pin_messages'] == "True":
            if DEBUG: print("  - Pinning Message")
            await message.pin()

        # SEND DM
        if DEBUG: print("  - Sending DM")
        if not self.config_data['direct_message'] == "":
            await message.author.send(embed=self.directMessage_embed)        

    @commands.command()
    @commands.check(bot_utils.is_admin)
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
    @commands.check(bot_utils.is_admin)
    async def setup_help(self, ctx):
        '''
        Makes all help channels available. (Admin-Only)
        '''

        for channel in self.help_channel_list:
            channel.title_update(emoji='✅', status="Available")

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

        # CHECK CHANNEL IS OPEN
        if self.help_channel_list[ctx.channel.id].owner == None:
            return

        # IF OWNER OR MOD
        if self.help_channel_list[ctx.channel.id].owner == user_name or await bot_utils.is_mod(ctx):
            await self.help_channel_list[ctx.channel.id].close_channel()

    @tasks.loop(seconds=10)
    async def background_ActivityCheck(self):

        if DEBUG: print(f" -- RUNNING ACTIVITY CHECK -- ")

        # AWAIT BOT TO BE READY
        await self.bot.wait_until_ready()

        temp_chan = "\n     ".join( [ str(i) for i in self.config_data['help_channels'] ] )
        if DEBUG: print(f" -- Channels in list:\n     {temp_chan}")

        if DEBUG: print(" -- Now looping over channels:")

        # LOOP OVER ALL CHANNELS IN LIST
        for channel in self.help_channel_list.values():
            if DEBUG: print(f"     Channel: {channel}")
            
            # IF CHANNEL HAS A LAST MESSAGE
            if self.bot.get_channel(channel.channel_id).last_message == None:
                if DEBUG: print("     No last message: Next.")
                continue

            if DEBUG: print(f"     Last message: _____ ")

            # CONVERT EMBEDS DICTS 
            embeds_dict = [i.to_dict() for i in self.bot.get_channel(channel.channel_id).last_message.embeds]

            # CHECK IF LAST MESSAGE IS THE AVAILABLE DICT
            if self.available_embed.to_dict() in embeds_dict: 
                if DEBUG: print("     Embed is available embed")
                continue
            if DEBUG: print(f"     Embed check passed")

            # GET TIME SINCE LAST MESSAGE 
            seconds_since_last_message = (datetime.datetime.utcnow() - self.bot.get_channel(channel.channel_id).last_message.created_at).total_seconds()
            if DEBUG: print(f"     Seconds of inactivity: {seconds_since_last_message}")

            # CHECK IF TIMEOUT CONDITION HAS HAPPENED
            if seconds_since_last_message < self.config_data['timeout']:
                if DEBUG: print("     Timeout condition not occured.")
                continue
        
            # CLOSE CHANNEL
            if DEBUG: print(f"     CHANNEL CLOSING")
            await channel.close_channel()           

        if DEBUG: print("---------------------------------")

    def get_name(self, author):
        if author.nick == None: 
            name = author.name
        else: 
            name = author.nick

        return name

def setup(bot):
    bot.add_cog(Dynamic_Help(bot))
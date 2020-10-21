import discord
from discord.ext import tasks, commands
import json
import datetime
import bot_utils
import asyncio
import re

DEBUG = False

class Help_Channel:
    version = "v2.0"

    def __init__(self, bot, channel_number, config_data, channel_id):
        if DEBUG: print(f"Initilising Help_Channel {channel_number}")

        self.bot = bot
        self.config_data = config_data

        self.channel_id = channel_id

        self.channel_number = channel_number

        self.state = "AVAILABLE"
        # await self._to_avail()
        self.owner = None
        # self.title_update_at = None

        # CREATE EMBEDS
        self.available_embed = discord.Embed(title="Channel Available", description=self.config_data['available_message'], color=bot_utils.green)
        self.closed_embed = discord.Embed(title="Channel Closed", description=self.config_data['closed_message'], color=bot_utils.red)
        self.directMessage_embed = discord.Embed(title="Channel Allocated", description=self.config_data['direct_message'], color=bot_utils.green)

    def __str__(self):
        return f"Help Channel: {str(self.bot.get_channel(self.channel_id))}"

    async def _to_close(self):
        '''
        Closed status entry method.

        Sets the channel state to closed. No messages should can be sent. This state exists to work around the discord rate limitations on changing channel names.
        '''

        previous_state = self.state
        self.state = "CLOSED"

        channel_object = await self.get_channel()

        if self.config_data['pin_messages'] == "True":
            for p in await channel_object.pins(): 
                await p.unpin()
        
        if DEBUG: print("Checking time since update")

        time_since_updated = self.time_since_last_update()
        if time_since_updated > 600:
            await self._to_avail()
            return

        # CLOSE THE CHANNEL
        await channel_object.send(embed=self.closed_embed)
        await channel_object.set_permissions(channel_object.guild.default_role, send_messages=False)

        # CLEAN UP PINS 
        if self.config_data['pin_messages'] == "True":
            pinned_messages = await channel_object.pins()
            for pinned_message in pinned_messages: 
                await pinned_message.unpin()

    async def _check_close(self):
        '''
        Checks the closed state is still required.

        Channel should remain closed if <600 seconds has passed since the last name change. After 600 have passed _to_avail() should be called.
        '''

        if self.time_since_last_update() > 600:
            await self._to_avail()

    async def _to_new(self, member, message=None):
        '''
        Sets state to a new issue.
        '''
        self.state = "NEW"

        if len(message.mentions) != 0:
            sent_message = await message.channel.send(f"**Do you want to open this channel for {message.mentions[0]}?**\n\n```\nReact 👍 to open the channel for {message.mentions[0]}.\nReact 👎 to open it for yourself.\n```")
            await sent_message.add_reaction('👍')
            await sent_message.add_reaction('👎')

            def check(reaction, user):
                return user == message.author and (str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎') and sent_message.id == reaction.message.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=20, check=check)
                await sent_message.delete()
                if str(reaction.emoji) == '👍':
                    target_user = message.mentions[0]
                else:
                    target_user = message.author
            except asyncio.TimeoutError:
                # CLEAN UP
                await sent_message.delete()
                target_user = message.author
        else:   
            target_user = message.author

        self.owner = str(target_user.name)

        if message and self.config_data['pin_messages'] == "True":
            await message.pin()

        # await self.title_update(emoji="❗", status=self.owner)
        await self.title_update(emoji="❕", status=self.owner)

        # try:
        #     await target_user.send(embed=self.directMessage_embed)
        # except Exception:
        #     print("Failed to send DM in help channels")

        await self.message_quality_check(message)

    async def _check_new(self):
        await self.timeout_check()

    async def _to_avail(self):
        if DEBUG: print("_to_avail running")

        if DEBUG: print("Setting state:")
        self.state = "AVAILABLE"
        if DEBUG: print(self.state)

        await self.title_update(emoji="✅", status="available")
        self.owner = None

        channel_object = await self.get_channel()

        # SET PERMS
        await channel_object.set_permissions(channel_object.guild.default_role, send_messages=True)

        # SEND EMBED
        await channel_object.send(embed=self.available_embed)

    async def _check_avail(self):
        pass

    async def _to_active(self, member):
        self.state = "ACTIVE"

        if member.name == self.owner:
            return

        # await self.title_update(emoji="❕", status=self.owner)

    async def _check_active(self):
        await self.timeout_check()
    
    async def check(self):
        if DEBUG: print(f" - Running check {self.state} on {self.channel_id}")

        checks = {
            "AVAILABLE": self._check_avail,
            "CLOSED": self._check_close,
            "ACTIVE": self._check_active,
            "NEW": self._check_new
        }

        if DEBUG: print("Awaiting check")
        await checks[self.state]()
        if DEBUG: print("returned from check")

    async def get_time_since_last_message(self):
        channel_object = await self.get_channel()
        last_message = await channel_object.fetch_message(channel_object.last_message_id)
        seconds_since_last_message = (datetime.datetime.utcnow() - last_message.created_at).total_seconds()
        return seconds_since_last_message

    async def get_channel(self):
        return self.bot.get_channel(self.channel_id)

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

    async def timeout_check(self):
        if DEBUG: print("Timeout Check")
        channel_inactive_for = await self.get_time_since_last_message()
        if DEBUG: print(channel_inactive_for)
        if DEBUG: print("   -", channel_inactive_for)
        
        if channel_inactive_for > self.config_data['timeout']:
            if DEBUG: print("Running _to_close")
            await self._to_close()

    async def message_quality_check(self, message):

        length_check = len(message.content) < 200
        images_check = len(message.attachments)<1
            
        length_string = "**Your question looks a bit short!**\nConsider including some more information with it such as:\n- Printer make and model\n- Any Mods\n- Firmware\n- Filament material and temps\n- What slicer you are using\n- Any recent changes you have made\n- What have you tried so far"
        images_string = "**Images can really help with debugging a printer!**\nConsider adding some to your post of:\n- The print\n- The printer"

        result = length_check * length_string + "\n\n" + images_check * images_string

        if length_check or images_check:
            await message.channel.send(embed=discord.Embed(title="Could You Include More Info?", description=result))

    def time_since_last_update(self):
        result = (datetime.datetime.utcnow() - self.title_update_at).total_seconds()
        if DEBUG: print(result)
        return result

    async def message_faq_check(self, message):
        message_content = message.content.lower().split()


class HelpChannels(commands.Cog):
    version = "v1.0.0"

    def __init__(self, bot):
        self.bot = bot

        # GET CONFIG DATA
        self.config_data = []
        with open('modules/HelpChannels/config.json') as f:
            self.config_data = json.load(f)

        # CREATE CHANNELS DICT
        self.help_channel_list = {}
        for index, chan_id in enumerate(self.config_data['help_channels'], start=1):
            self.help_channel_list[chan_id] = Help_Channel(self.bot, index, self.config_data, chan_id)

        # CREATE EMBEDS
        # self.available_embed = discord.Embed(title="Channel Available", description=self.config_data['available_message'], color=bot_utils.green)
        # self.closed_embed = discord.Embed(title="Channel Closed", description=self.config_data['closed_message'], color=bot_utils.red)
        # self.directMessage_embed = discord.Embed(title="Channel Allocated", description=self.config_data['direct_message'], color=bot_utils.green)

        # START BACKGROUND TASKS
        if self.config_data['timeout'] != 0:
            self.background_ActivityCheck.start()

    @commands.Cog.listener()
    async def on_message(self, message):

        # CHECK IF USER IS THE BOT
        if message.author == self.bot.user:
            return

        # CHECK IF ITS IN A HELP CHANNEL
        if message.channel.id not in self.config_data['help_channels']:
            return

        # CHECK IF ITS A COMMAND
        if message.content[:1] == self.bot.config['prefix']:
            return

        if DEBUG: print("--- RUNNING ON_MESSAGE LISTENER IN DYANMIC HELP ---")

        help_channel =  self.help_channel_list[message.channel.id]
        channel_state = help_channel.state
        if DEBUG: print(help_channel, " ", channel_state)

        if channel_state == 'AVAILABLE':
            if any(message.author.name == x.owner for x in self.help_channel_list.values()):
                await message.delete()
                await message.author.send(self.config_data['multiple_message'])
                return
            if DEBUG: print("Available channel reveived a message.")
            await help_channel._to_new(message.author, message)
        elif channel_state == 'NEW':
            if DEBUG: print("New Channel received message.")
            await help_channel._to_active(message.author)
        else:
            if DEBUG: print("No action")
                 
    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def end_help(self, message):
        '''Ends Dynamic Help and resets the help names.'''
        
        while self.help_channel_list:
            key, value = self.help_channel_list.popitem()
            await value._to_avail()

        # for i, c in self.help_channel_list.copy().items():
        #     del self.help_channel_list[i]
        #     await c._to_avail()

        self.bot.unload_extension(f"modules.HelpChannels.HelpChannels")

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def setup_help(self, ctx):
        '''Makes all help channels available. (Admin-Only)'''

        for channel in self.help_channel_list.values():
            await channel._to_avail()

    @commands.command()
    async def solved(self, ctx):
        '''Command to close an open help channel that is no longer required.'''

        # CHECK IF IN HELP CHANNEL
        if ctx.channel.id not in self.config_data['help_channels']:
            return

        help_channel = self.help_channel_list[ctx.channel.id]

        if DEBUG: print("----------\n", help_channel.owner == ctx.author.name, '\n', ctx.author.name, help_channel.owner, '\n',  await bot_utils.is_mod(ctx), "\n----------")
        if help_channel.owner == ctx.author.name or await bot_utils.is_mod(ctx):
            await help_channel._to_close()
        else:
            await ctx.send("You dont have permission to do that!")
            return

    @tasks.loop(seconds=60)
    async def background_ActivityCheck(self):

        if DEBUG: print(f" -- RUNNING ACTIVITY CHECK -- ")

        # AWAIT BOT TO BE READY
        await self.bot.wait_until_ready()

        # LOOP OVER ALL CHANNELS IN LIST
        for channel in self.help_channel_list.values():
            if DEBUG: print(f"Channel: {channel}")
            if DEBUG: print(channel.channel_number, channel.owner, channel.state)

            await channel.check()

        if DEBUG: print("----------------------")

def setup(bot):
    bot.add_cog(HelpChannels(bot))
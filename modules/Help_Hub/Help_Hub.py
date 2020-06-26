import discord
from discord.ext import tasks, commands
import json
import bot_utils
import asyncio
import datetime

class Help_Hub(commands.Cog):
    version = "v0.1"    

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Help_Hub/config.json') as f:
            self.config_data = json.load(f)

        self.closed_embed = discord.Embed(title="Channel Closed", description=self.config_data['closed_message'], color=bot_utils.red)

        self.background_ActivityCheck.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Delete non 'ask' messages
        if message.author != self.bot.user:
            if message.channel.id == self.config_data["help_hub"]:
                if not (f"{self.bot.config['prefix']}ask ") in message.content[:8] :
                    await message.delete()

    @commands.command()
    async def topic(self, ctx, *, topic):
        """Use this command in the help hub to open a new help channel!"""

        if ctx.channel.id != self.config_data["help_hub"]:
            await ctx.send(self.config_data['wrong_channel_message'])
            return

        time_stamps = [0]*len(self.config_data["help_channels"])

        #FIND LEAST ACTIVE HELP CHANNEL
        for i in range(len(self.config_data["help_channels"])):
            time_stamps[i] = self.bot.get_channel(self.config_data["help_channels"][i]).last_message.created_at
        least_active_channel = self.bot.get_channel(self.config_data["help_channels"][time_stamps.index(min(time_stamps))])

        # OPEN CHANNEL
        await least_active_channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await least_active_channel.edit(name=await self.make_channel_name(emoji="❕", status="in-use", number=self.config_data['help_channels'].index(least_active_channel.id)+1))

        # SEND USER TO CORRECT CHANNEL
        embed = discord.Embed(title="Channel Open", description=f"This channel is now open for {ctx.author.mention} to talk about:\n\n{topic}\n\nIf you have a question you can get your own channel by posting in the help-hub.", color=bot_utils.green)
        await least_active_channel.send(embed=embed)

        # ANNOUNCE IN HELP HUB + CLEAN UP
        embed = discord.Embed(title="Help Request!", description=f"{ctx.author.mention} would like some help in {least_active_channel.mention} with:\n\n{topic}\n\nIf you have a question you can open a new help channel with the !topic [Your Topic] command.", color=bot_utils.purple)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def setup_help_hub(self, ctx):
        for channel_id in self.config_data['help_channels']:
            channel = self.bot.get_channel(channel_id)
            
            await self.close_channel(channel)

    @tasks.loop(seconds=5.0)
    async def background_ActivityCheck(self): # task runs every 60 seconds

        await self.bot.wait_until_ready()

        for channel_id in self.config_data['help_channels']:

            # GET CHANNEL
            channel = self.bot.get_channel(channel_id)

            # CHECK IF A MESSAGE EXISTS
            if channel.last_message == None:
                continue

            # CHECK IF LAST MESSAGE WAS FROM A BOT
            embeds_dict = [i.to_dict() for i in channel.last_message.embeds]
            if self.closed_embed.to_dict() in embeds_dict:
                continue

            #CALCUALTE TIME SINCE LAST MESSAGE
            seconds_since_last_message = (datetime.datetime.utcnow() - channel.last_message.created_at).total_seconds()

            # IF LONGER THAN TIMEOUT: CLOSE
            if seconds_since_last_message > self.config_data['timeout']:
                await self.close_channel(channel)

    async def close_channel(self, channel_object):

        await channel_object.send(embed=self.closed_embed)

        await channel_object.set_permissions(channel_object.guild.default_role, send_messages=False)
        
        await channel_object.edit(name=await self.make_channel_name(emoji="🔒", status="closed", number=self.config_data['help_channels'].index(channel_object.id)+1))

    async def make_channel_name(self, emoji=" ", number=" ", status=" "):

        output = self.config_data['channel_name']

        output = output.replace("<emoji>", emoji)

        output = output.replace("<number>", str(number))
       
        output = output.replace("<status>", status)

        return output

def setup(bot):
    bot.add_cog(Help_Hub(bot))
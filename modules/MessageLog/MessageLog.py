
import discord
from discord.ext import commands
import json
import bot_utils

class MessageLog(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await bot_utils.log(self.bot, title='Message Edited', color=bot_utils.yellow, From=f"{before.author.mention} [{before.author}]", Before=before.content[:1000], After=after.content[:1000], channel=500395384720588810, DM=False)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await bot_utils.log(self.bot, title='Message Deleted', color=bot_utils.yellow, From=f"{message.author.mention} [{message.author}]", Before=message.content[:1000], channel=500395384720588810, DM=False)

def setup(bot):
    bot.add_cog(MessageLog(bot))
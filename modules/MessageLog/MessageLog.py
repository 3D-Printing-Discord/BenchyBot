
import discord
from discord.ext import commands
import json
import difflib
import bot_utils

def diff(a, b ):

    sm = difflib.SequenceMatcher(None, a, b)
    
    output= []
    for opcode, a0, a1, b0, b1 in sm.get_opcodes():
        if opcode == 'equal':
            output.append(sm.a[a0:a1])
        elif opcode == 'insert':
            output.append("**" + sm.b[b0:b1] + "**")
        elif opcode == 'delete':
            pass
            # output.append("**" + sm.a[a0:a1] + "**")
        elif opcode == 'replace':
            output.append("**" + sm.b[b0:b1] + "**")
        else:
            raise RuntimeError
    return ''.join(output)

class MessageLog(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author == self.bot.user:
            return

        if before.content == after.content:
            return

        result = diff(before.content, after.content)
        await bot_utils.log(self.bot, title='Message Edited', color=bot_utils.yellow, From=f"{before.author.mention} [{before.author}]", Before=before.content, After=result, channel=500395384720588810, DM=False)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author == self.bot.user:
            return

        await bot_utils.log(self.bot, title='Message Deleted', color=bot_utils.red, From=f"{message.author.mention} [{message.author}]", Message=message.content[:1000], channel=500395384720588810, DM=False)

def setup(bot):
    bot.add_cog(MessageLog(bot))
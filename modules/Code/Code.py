
import discord
from discord.ext import commands
import json
import bot_utils
import re

class Code(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        # self.config_data = []
        # with open('modules/Code/config.json') as f:
        #     self.config_data = json.load(f)

    @commands.command(aliases=['g'])
    async def gcode(self, ctx):
        await self.send_gcode(ctx.message, command=f"{ctx.prefix}{ctx.invoked_with}")

    async def send_gcode(self, message, command=None):
        print(command)
        message_string = message.content.strip(f"{command} ")
        print(message_string)
        await message.channel.send(f"{message.author.mention} said:\n```gcode\n{message_string}\n```")
        # await message.channel.send("```\nAn Error Occured\n```")
        await message.delete()

def setup(bot):
    bot.add_cog(Code(bot))

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

    @commands.Cog.listener()
    async def on_message(self, message): 
        if message.author.id == self.bot.user.id:
            return

        if not message.channel.id == 339978089411117076:
            return

        print("Message received")
        if re.search('[G|M][0-9]', message.content) and not '```gcode' in message.content:
            gcode = []
            for l in message.content.split('\n'):
                if l.startswith(';') or re.search('^[G|M][0-9]', l):
                    gcode.append(l)

            if len(gcode) > 0:
                gcode_out = "\n".join(gcode)
                await message.channel.send(f"```gcode\n{gcode_out}\n```")

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
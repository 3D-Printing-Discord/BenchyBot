import discord
from discord.ext import commands
import json
import bot_utils
import datetime

class DM(commands.Cog):
    version = "v1.0"

    def __init__(self, bot):
        self.bot = bot

        # LOAD CONFIG DATA
        self.config_data = []
        with open('modules/DM/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if(message.guild == None) and (message.author != self.bot.user):
            # BUILD EMBED
            embed = discord.Embed(title="Direct Message Received", color=bot_utils.yellow)
            embed.add_field(name="Sender", value=message.author.mention, inline=False)
            embed.add_field(name="Message", value=message.content, inline=False)

            # SEND EMBED TO CHANNEL
            target_channel = self.bot.get_channel(self.config_data["bot_mail_channel"])
            await target_channel.send(embed=embed)

            # RESPOND TO USER
            await message.author.send(self.config_data["bot_response"])

def setup(bot):
    bot.add_cog(DM(bot))
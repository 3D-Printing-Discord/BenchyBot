import discord
from discord.ext import commands
import json
import bot_utils

class Report(commands.Cog):
    version = "v1.0"

    def __init__(self, bot):
        self.bot = bot

        # GET CONFIG DATA
        self.config_data = []
        with open('modules/Report/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if self.config_data['report_emoji'] in f"{reaction.emoji}":

            target_channel = self.bot.get_channel(self.config_data["report_channel"])

            embed = discord.Embed(title="Report Received", description=f"{reaction.message.jump_url}\n```        BY: {user.name}\n   OF USER: {reaction.message.author.name}\n       FOR: \"{reaction.message.content}\"\nCREATED AT: {reaction.message.created_at}\n        IN: #{reaction.message.channel.name}```", color=bot_utils.red)
            await target_channel.send('@here', embed=embed)

            await reaction.remove(user)
            
            await user.send(self.config_data["report_message"])

def setup(bot):
    bot.add_cog(Report(bot))

import discord
from discord.ext import commands
import json
import asyncio
from  datetime import datetime, timedelta

class Suggestions(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Suggestions/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if message.channel.id in self.config_data['suggestions_channel']:
            emojis = ['👍', '👎', '🤷‍♀️']
            for i in emojis:
                await message.add_reaction(i)

        if message.channel.id in self.config_data['timed_channels']:
            await message.delete()

            embed = discord.Embed(title=f"Poll By: {message.author.name}", description=message.content)
            end_date = datetime.now() + timedelta(days=3)
            embed.add_field(name="Expires at", value=end_date.strftime('%m/%d/%Y %H:%M UTC'), inline=False)

            sent_message = await message.channel.send("@everyone", embed=embed)

            emojis = ['👍', '👎', '🤷‍♀️']
            for i in emojis:
                await sent_message.add_reaction(i)

            await asyncio.sleep(259200) #86400 - 1 day, 259200 - 3 days, 432000 - 5 days 

            sent_message = await sent_message.channel.fetch_message(sent_message.id)
            
            r = {}
            for react in sent_message.reactions:
                r[react.emoji] = react.count

            yes_count   = r['👍'] - 1
            no_count    = r['👎'] - 1
            maybe_count = r['🤷‍♀️'] - 1
            total = sum([yes_count, no_count, maybe_count])
            
            if total != 0:
                embed.add_field(name="Results", value=f"```👍 = {yes_count} ({yes_count/total * 100:.1f}%)\n👎 = {no_count} ({no_count/total * 100:.1f}%)\n🤷‍♀️ = {maybe_count} ({maybe_count/total * 100:.1f}%)```", inline=False)
            else:
                embed.add_field(name="Results", value="```No Votes Received```")
            embed.title = f'Poll By: {message.author.name} CLOSED'
            await sent_message.edit(content=f"{message.author.mention}: Poll is complete.", embed=embed)

def setup(bot):
    bot.add_cog(Suggestions(bot))
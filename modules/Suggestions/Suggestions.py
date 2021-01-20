
import discord
from discord.ext import commands
import json
import asyncio
from  datetime import datetime, timedelta
import bot_utils

class Suggestions(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Suggestions/config.json') as f:
            self.config_data = json.load(f)

    async def suggestion_message(self, message):
        await message.delete()
        suggestion_message = await message.channel.send(
            embed=discord.Embed(
                title=f"Suggestion From: {message.author}",
                description=message.clean_content,
            )
        )

        emojis = ['👍', '👎', '🤷‍♀️']
        for i in emojis:
            await suggestion_message.add_reaction(i)

    async def count_reacts(self, message):
        r = {react.emoji: react.count for react in message.reactions}

        yes_count   = r['👍'] - 1
        no_count    = r['👎'] - 1
        maybe_count = r['🤷‍♀️'] - 1
        total = sum([yes_count, no_count, maybe_count])

        return yes_count, no_count, maybe_count, total

    async def timed_suggestion(self, message, days=3):
        end_date = datetime.now() + timedelta(days=days)

        embed = discord.Embed(title=f"Poll By: {message.author.name}", description=message.content)
        embed.add_field(name="Expires at", value=end_date.strftime('%m/%d/%Y %H:%M UTC'), inline=False)

        sent_message = await message.channel.send("@everyone", embed=embed)

        emojis = ['👍', '👎', '🤷‍♀️']
        for i in emojis:
            await sent_message.add_reaction(i)

        # WAIT
        await asyncio.sleep(days * 60 * 60 * 24) # days * 60 * 60 * 24
        sent_message = await sent_message.channel.fetch_message(sent_message.id)
        
        yes_count, no_count, maybe_count, total = await self.count_reacts(sent_message)

        if total != 0:
            embed.add_field(
                name="Results",
                value=f"```👍 = {yes_count} ({yes_count/total * 100:.1f}%)\n👎 = {no_count} ({no_count/total * 100:.1f}%)\n🤷‍♀️ = {maybe_count} ({maybe_count/total * 100:.1f}%)```",
                inline=False
            )
        else:
            embed.add_field(name="Results", value="```No Votes Received```")
        embed.title = f'Poll By: {message.author.name} CLOSED'
        await sent_message.edit(content=f"{message.author.mention}: Poll is complete.", embed=embed)

    async def reg_suggestion(self, message, user, days=3):
        end_date = datetime.now() + timedelta(days=days)

        embed = discord.Embed(title=f"Regs Vote for: {user.name}", description=f"Should {user.name} become a reg?")

        if self.bot.get_cog('User_Management'):
            embed = await self.bot.get_cog('User_Management').add_user_embed_fields(embed, user)
        else:
            embed.add_field(name="No User Data Available", value="`User Management` module not loaded.", inline=False)

        embed.add_field(name="Expires at", value=end_date.strftime('%m/%d/%Y %H:%M UTC'), inline=False)

        sent_message = await message.channel.send("@everyone", embed=embed)

        emojis = ['👍', '👎', '🤷‍♀️']
        for i in emojis:
            await sent_message.add_reaction(i)

        # WAIT
        await asyncio.sleep(days * 60 * 60 * 24) # days * 60 * 60 * 24
        sent_message = await sent_message.channel.fetch_message(sent_message.id)
        
        yes_count, no_count, maybe_count, total = await self.count_reacts(sent_message)

        if no_count == 0 and yes_count > 4 and yes_count > maybe_count:
            result_string = "Vote Passed!"
        else:
            result_string = "Vote Did not pass."
        
        if total != 0:
            embed.add_field(
                name="Results",
                value=f"```👍 = {yes_count} ({yes_count/total * 100:.1f}%)\n👎 = {no_count} ({no_count/total * 100:.1f}%)\n🤷‍♀️ = {maybe_count} ({maybe_count/total * 100:.1f}%)```\n**{result_string}**",
                inline=False
            )
        else:
            embed.add_field(name="Results", value="```No Votes Received```")
        embed.title = f'Regs Vote for: {user} CLOSED - {result_string}'
        await sent_message.edit(content=f"{message.author.mention}: Poll is complete.", embed=embed)

    async def add_feedback(self, message):
        await message.delete()

        message_target = await message.channel.fetch_message(message.reference.message_id)
        embed = message_target.embeds[0]

        embed.add_field(name=f"Response / Feedback from {message.author.name}", value=message.clean_content, inline=False)
        await message_target.edit(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.id == self.bot.user.id:
            return

        if message.channel.id in self.config_data['suggestions_channel']:
            if message.reference is not None and any(r.id in bot_utils.admin_roles for r in message.author.roles):
                await self.add_feedback(message)
            else: 
                await self.suggestion_message(message)
                

        if message.channel.id in self.config_data['timed_channels']:
            await message.delete()

            if len(message.mentions) == 0:
                await self.timed_suggestion(message)
            else:
                await self.reg_suggestion(message, message.mentions[0])


def setup(bot):
    bot.add_cog(Suggestions(bot))
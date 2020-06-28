
import discord
from discord.ext import commands
import json
import math
import bot_utils
import asyncio

class Poll(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.messages = {}

    @commands.command()
    async def poll(self, ctx, *, topic):

        result = self.build_result(0,0,0)
        sent_message = await ctx.send(f"**{topic}**\n{result}" )

        await sent_message.add_reaction('👍')
        await sent_message.add_reaction('👎')
        await sent_message.add_reaction('🤷‍♀️')

        self.messages[int(sent_message.id)] = topic

        await asyncio.sleep(24*60*60)

        del self.messages[sent_message.id]

        await sent_message.clear_reactions()
        await sent_message.edit(content=f"**{topic}**\n{result}`CLOSED`")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if reaction.message.id in self.messages:
            await self.update_message(reaction.message, self.messages[reaction.message.id])

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):

        if reaction.message.id in self.messages:
            await self.update_message(reaction.message, self.messages[reaction.message.id])

    def build_result(self, yes, no, maybe):
        total_answers = yes + no + maybe

        if total_answers == 0:
            return f"```\n👍| \n👎| \n🤷‍♀️| \nTotal Replies: 0```"

        yes_per = yes / total_answers
        no_per = no / total_answers
        maybe_per = maybe / total_answers

        len_factor = 30
        yes_bar = math.floor(yes_per * len_factor) * "█"
        no_bar = math.floor(no_per * len_factor) * "█"
        maybe_bar = math.floor(maybe_per * len_factor) * "█"

        percent_string_test = self.build_percent_string(0.08)

        result = f"```\n👍|{self.build_percent_string(yes_per)}%| {yes_bar}\n👎|{self.build_percent_string(no_per)}%| {no_bar}\n🤷‍♀️|{self.build_percent_string(maybe_per)}%| {maybe_bar}\nTotal Replies: {total_answers}```"

        return result

    async def update_message(self, message, topic):
        r = {}
        for react in message.reactions:
            r[react.emoji] = react.count

        yes_count   = r['👍'] - 1
        no_count    = r['👎'] - 1
        maybe_count = r['🤷‍♀️'] - 1

        result = self.build_result(yes_count, no_count, maybe_count)

        await message.edit(content=f"**TEST**\n{result}")

    def build_percent_string(self, percent):
        output = str(round(percent*100))

        output = " "*(3-len(output)) + output

        return(output)

def setup(bot):
    bot.add_cog(Poll(bot))
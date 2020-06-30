
import discord
from discord.ext import commands
import json
import math
import bot_utils
import asyncio

DEBUG = False

class Poll(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.messages = {}

        # self.reacts_list = ['👍', '👎', '🤷‍♀️']

    @commands.command()
    async def poll(self, ctx, *, topic):
        '''
        Creates an interactive poll.
        '''

        result = self.build_result(0,0,0)
        sent_message = await ctx.send(f"**{topic}**\n{result}" )

        await sent_message.add_reaction('👍')
        await sent_message.add_reaction('👎')
        await sent_message.add_reaction('🤷‍♀️')

        self.messages[int(sent_message.id)] = topic

        if DEBUG: print("Going to sleep")
        await asyncio.sleep(12*60*60)
        if DEBUG: print("Woken Up")
    
        del self.messages[sent_message.id]

        await sent_message.clear_reactions()
        await sent_message.edit(content=f"**{topic}**\n{result}`CLOSED`")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, RawReactionActionEvent):
        if DEBUG: print("on_raw_reaction_remove")
        if RawReactionActionEvent.message_id in self.messages:
            fetched_channel = self.bot.get_channel(RawReactionActionEvent.channel_id)
            fetched_message = await fetched_channel.fetch_message(RawReactionActionEvent.message_id)
            if DEBUG: print("-- Poll Message")
            await self.update_message(fetched_message, self.messages[RawReactionActionEvent.message_id])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, RawReactionActionEvent):
        if RawReactionActionEvent.user_id == self.bot.user.id:
            return

        if DEBUG: print("on_raw_reaction_add")
        if RawReactionActionEvent.message_id in self.messages:
            fetched_channel = self.bot.get_channel(RawReactionActionEvent.channel_id)
            fetched_message = await fetched_channel.fetch_message(RawReactionActionEvent.message_id)
            react_user = self.bot.get_user(RawReactionActionEvent.user_id)
            if DEBUG: print("-- Poll Message")

            reacts_to_remove = ['👍', '👎', '🤷‍♀️']
            reacts_to_remove.remove(str(RawReactionActionEvent.emoji))
            for r in reacts_to_remove:
                await fetched_message.remove_reaction(r, react_user)

            await self.update_message(fetched_message, self.messages[RawReactionActionEvent.message_id])

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
        if DEBUG: print("-- Update Message")
        r = {}
        for react in message.reactions:
            r[react.emoji] = [u.id for u in await react.users().flatten()]
            # r[react.emoji] = react.count

        yes_count   = len(set(r['👍']) - set(r['👎']) - set(r['🤷‍♀️']))
        no_count    = len(set(r['👎']) - set(r['🤷‍♀️']) - set(r['👍']))
        maybe_count = len(set(r['🤷‍♀️']) - set(r['👍']) - set(r['👎']))

        # yes_count   = r['👍'] - 1
        # no_count    = r['👎'] - 1
        # maybe_count = r['🤷‍♀️'] - 1

        result = self.build_result(yes_count, no_count, maybe_count)

        await message.edit(content=f"**TEST**\n{result}")

    def build_percent_string(self, percent):
        output = str(round(percent*100))

        output = " "*(3-len(output)) + output

        return(output)

def setup(bot):
    bot.add_cog(Poll(bot))
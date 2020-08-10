
import discord
from discord.ext import commands, flags
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
    @commands.has_any_role(*bot_utils.reg_roles)
    async def poll(self, ctx, *, topic="Poll"):
        '''
        Creates an interactive poll.
        '''

        topic = bot_utils.sanitize_input(topic)

        args, topic = bot_utils.simple_parse(topic, time='t')
        args['time'] = bot_utils.convert_to_number(args['time'])

        if args['time'] is None:
            args['time'] = 720

        result = self.build_result({'👍':0, '👎':0, '🤷‍♀️':0})
        sent_message = await ctx.send(f"**{topic}**\n{result}")

        await sent_message.add_reaction('👍')
        await sent_message.add_reaction('👎')
        await sent_message.add_reaction('🤷‍♀️')


        self.messages[int(sent_message.id)] = topic

        await sent_message.pin()

        if DEBUG: print("Going to sleep")
        await asyncio.sleep(args['time']*60)
        if DEBUG: print("Woken Up")
    
        del self.messages[sent_message.id]

        await sent_message.edit(content=f"**{topic}**\n{result}`CLOSED`")
        await sent_message.unpin()
        await sent_message.clear_reactions()

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
            try:
                reacts_to_remove.remove(str(RawReactionActionEvent.emoji))
            except ValueError:
                reacts_to_remove = reacts_to_remove
            for r in reacts_to_remove:
                await fetched_message.remove_reaction(r, react_user)

            await self.update_message(fetched_message, self.messages[RawReactionActionEvent.message_id])

    def build_result(self, options):
        total_answers = sum(options.values())

        if total_answers == 0:
            results_string = "\n".join([f"{k}|" for k in options.keys()])
            return f"```\n{results_string}\nTotal Replies: {total_answers}```"

        result_per = {}
        for k, v in options.items():
            result_per[k] = v / total_answers

        len_factor = 30
        result_bar = {}
        for k, v in result_per.items():
            result_bar[k] = math.floor(v * len_factor) * "█"

        results_string = "\n".join([f"{k}|{self.build_percent_string(result_per[k])}%|{v}" for k, v in result_bar.items()])
        result = f"```\n{results_string}\nTotal Replies: {total_answers}```"

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

        result = self.build_result({'👍':yes_count, '👎':no_count, '🤷‍♀️':maybe_count})

        await message.edit(content=f"**{topic}**\n{result}")

    def build_percent_string(self, percent):
        output = str(round(percent*100))
        output = " "*(3-len(output)) + output
        return(output)

def setup(bot):
    bot.add_cog(Poll(bot))
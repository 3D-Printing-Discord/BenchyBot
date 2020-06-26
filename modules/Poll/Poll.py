
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

    @commands.command()
    @commands.check(bot_utils.is_mod)
    async def poll(self, ctx, *, topic):
        result = self.build_result(0,0,0)
        sent_message = await ctx.send(f"**{topic}**\n{result}")

        await sent_message.add_reaction('👍')
        await sent_message.add_reaction('👎')
        await sent_message.add_reaction('🤷‍♀️')

        # DEF CHECK FOR RESPONSE
        def check(reaction, user):    
            return user != self.bot.user and reaction.message.id == sent_message.id

        yes = 0
        no = 0 
        maybe = 0

        voted = []
        cont = True
        while cont:
            # AWAIT AND HANDLE RESPONSE

            # try:
            #     done, pending = await asyncio.wait([
            #         self.bot.wait_for('reaction_remove', timeout=60, check=check),
            #         self.bot.wait_for('reaction_add', timeout=60, check=check)
            #     ], return_when=asyncio.FIRST_COMPLETED)
                
            #     print("Runnning Update")

            #     # refetch message
            #     sent_message = await sent_message.channel.fetch_message(sent_message.id)

            #     print(sent_message.reactions)

            #     yes_count = [f for f in sent_message.reactions if str(f.emoji) == "👍"]
            #     print(f"YESSES: {len(yes_count)}")
            #     no_count = [f for f in sent_message.reactions if str(f.emoji) == "👎"]
            #     maybe_count = [f for f in sent_message.reactions if str(f.emoji) == "🤷‍♀️"]

            #     result = self.build_result(len(yes_count)-1, len(no_count)-1, len(maybe_count)-1)

            #     await sent_message.edit(content=f"**{topic}**\n{result}")

    
            # except asyncio.TimeoutError:
            #     await sent_message.clear_reactions()
            #     await sent_message.edit(content=f"**{topic}**\n{result}`CLOSED`")
            #     cont = False 

            # for future in pending:
            #     future.cancel()  # we don't need these anymore
            

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=86400, check=check)

                if user in voted:
                    continue

                if str(reaction) == "👍":
                    yes = yes + 1 
                elif str(reaction) == "👎":
                    no = no + 1
                elif str(reaction) == "🤷‍♀️":
                    maybe = maybe + 1
                else:
                    continue

                voted.append(user)
                result = self.build_result(yes, no, maybe)

                await sent_message.edit(content=f"**{topic}**\n{result}")

            except asyncio.TimeoutError:
                await sent_message.clear_reactions()
                await sent_message.edit(content=f"**{topic}**\n{result}`CLOSED`")
                cont = False 

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

    def build_percent_string(self, percent):
        output = str(round(percent*100))

        output = " "*(3-len(output)) + output

        return(output)

def setup(bot):
    bot.add_cog(Poll(bot))
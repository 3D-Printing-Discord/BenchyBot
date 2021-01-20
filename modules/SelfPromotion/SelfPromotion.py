
import discord
from discord.ext import commands
import json
import datetime
import random
import bot_utils
import sqlite3
import math
import re
from urllib.parse import urlparse

whitelist = [
    "xkuyax.de:8090",
    "www.aliexpress.com",
    "www.thingiverse.com",
    "cdn.discordapp.com",
    "www.amazon.com"
]

class SelfPromotion(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/SelfPromotion/config.json') as f:
            self.config_data = json.load(f)

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_message(self, message):

        if self.bot.user.id == message.author.id:
            return

        if message.channel.id == self.config_data['promotion_channel']:

            promotion_per = self.calc_percentage(message.author)*100
            check_promotion = promotion_per > self.config_data['post_threshold']
            promotion_error_mod = f"Self promotion messages must be under {self.config_data['post_threshold']}%. Current: {promotion_per:.2f}%"
            promotion_error_pub = f"You are using this channel too much."

            days_on_server = (datetime.datetime.utcnow() - message.author.joined_at).days
            check_days = days_on_server < self.config_data['age_min']
            days_error_mod = f"Your account must be over {self.config_data['age_min']} days. Current: {days_on_server} days"
            days_error_pub = f"Your account is too new to the server."

            number_of_messages = self.message_count(message.author)
            check_messages = number_of_messages < self.config_data['min_messages'] 
            messages_error_mod = f"You must have over {self.config_data['min_messages']} messages on the server. Current: {number_of_messages}"
            messages_error_pub = f"You do not have enough messages on the server."

            formatted_reason_mod = (check_promotion * (promotion_error_mod + "\n")) + (check_days * (days_error_mod + "\n")) + (check_messages * (messages_error_mod + "\n"))
            formatted_reason_pub = (check_promotion * (promotion_error_pub + "\n")) + (check_days * (days_error_pub + "\n")) + (check_messages * (messages_error_pub + "\n"))


            if check_promotion or check_days or check_messages:

                await message.delete()

                try:
                    await message.author.send(self.config_data['delete_message'] + '\n\nReason for deletion:\n' + formatted_reason_pub)
                    dm_status = "DM Sent Successfully"
                except:
                    dm_status = "**DM Failed To Send**"

                await bot_utils.log(self.bot, title="Self Promotion Message Removed", color=bot_utils.red, From=f"{message.author.mention} [{message.author}]", Message=f"```{message.content[:1000]}```", DM=dm_status, Reason=formatted_reason_mod)
            
            else:
                self.log_message(message)
        else:
            self.log_message(message)

    def log_message(self, message):
        # print(f"MESSAGE LOGGED: {message.content}")
        self.bot.databasehandler.sqlquery(
            "INSERT INTO SelfPromotion(user_id, date, channel) VALUES (?, ?, ?)",
            message.author.id, message.created_at, message.channel.id,
            return_type='commit'
            )

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def selfpromotion(self, ctx, member: discord.Member=None):
        '''
        Provides percentage of posts that are self promotion.
        '''

        if member == None:
            member = ctx.author

        percentage = self.calc_percentage(member)

        await ctx.send(f"Percentage of messages that are self-promotion for {member}:```{percentage*100:.2f} %```")

    def message_count(self, member):
        search_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        non_promotion = self.bot.databasehandler.sqlquery(
            "SELECT * FROM SelfPromotion WHERE user_id=? AND NOT channel=? AND date>?",
            member.id, self.config_data['promotion_channel'], search_date,
            return_type='all'
        )
        return len(non_promotion)

    def calc_percentage(self, member):
        search_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        non_promotion = self.bot.databasehandler.sqlquery(
            "SELECT * FROM SelfPromotion WHERE user_id=? AND NOT channel=? AND date>?",
            member.id, self.config_data['promotion_channel'], search_date,
            return_type='all'
        )

        promotion = self.bot.databasehandler.sqlquery(
            "SELECT * FROM SelfPromotion WHERE user_id=? AND channel=? AND date>?",
            member.id, self.config_data['promotion_channel'], search_date,
            return_type='all'
        )

        try:
            promotion_ratio = len(promotion)/len(non_promotion)
        except ZeroDivisionError:
            promotion_ratio = 1
        
        return promotion_ratio

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def load_history(self, ctx):
        '''
        Loads historic message data into the database
        '''

        if not await bot_utils.await_confirm(ctx, "**Pull 30 day history?**\n\nThis will be slow! (~**3** hours)"):
            return

        self.bot.databasehandler.sqlquery(
            "DELETE FROM SelfPromotion",
            return_type='commit'
        )

        prog_count = 0
        sent_message = await ctx.send(f"Step {prog_count} of {len(ctx.guild.channels)}")

        search_limit = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        # print(search_limit)
        for c in ctx.guild.channels:
            prog_count += 1
            await sent_message.edit(content=self.gen_prog(prog_count, len(ctx.guild.channels)))

            count = 0
            if str(c.type) == 'text':
                async for m in c.history(after=search_limit, limit=150000, before=datetime.datetime.utcnow()):
                    self.bot.databasehandler.sqlquery(
                        "INSERT INTO SelfPromotion(user_id, date, channel) VALUES (?, ?, ?)",
                        m.author.id, m.created_at, m.channel.id,
                        return_type='commit'
                    )

        await ctx.send("Done!")
                
    def gen_prog(self, cur, end):
        per = cur/end
        scale_factor = 40 

        number_blocks = round(per * scale_factor)
        number_spaces = scale_factor - number_blocks

        blocks = '█' * number_blocks
        spaces = ' ' * number_spaces 

        output = f"Step {cur} of {end}\n```\n|{self.build_percent_string(per)}%|{blocks}{spaces}|\n```"
        return output

    def build_percent_string(self, percent):
        output = str(round(percent*100))

        output = " "*(3-len(output)) + output

        return output

def setup(bot):
    bot.add_cog(SelfPromotion(bot))
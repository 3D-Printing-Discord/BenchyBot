
import discord
from discord.ext import commands
import json
import datetime
import random
import bot_utils
import sqlite3
import math

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
        self.c.execute("INSERT INTO SelfPromotion(user_id, date, channel) VALUES (?, ?, ?)", (message.author.id, message.created_at, message.channel.id))
        self.conn.commit()

        if message.channel.id == self.config_data['promotion_channel']:
            promotion_per = self.calc_percentage(message.author)*100
            print(f"promotion message from: {message.author} with {promotion_per*100:.2f}% promotion")
            if promotion_per > self.config_data['post_threshold']:
                await message.delete()
                try:
                    await message.author.send(self.config_data['delete_message'])
                except:
                    print("Couldnt message!")
                await message.guild.get_channel(self.config_data['log_channel']).send(f"Message removed in self-promotion by {message.author}\n\n```{message.content}```")
            

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def selfpromotion(self, ctx, member: discord.Member=None):
        '''
        Provides percentage of posts that are self promotion.
        '''

        if member == None:
            member = ctx.author

        percentage = self.calc_percentage(member)

        await ctx.send(f"Percentage of messages that are self-promotion for {member}:```{percentage*100:.2f}%```")

    def calc_percentage(self, member):
        self.c.execute("SELECT * FROM SelfPromotion WHERE user_id=? AND NOT channel=?", (member.id, self.config_data['promotion_channel']))
        non_promotion = self.c.fetchall()
        
        self.c.execute("SELECT * FROM SelfPromotion WHERE user_id=? AND channel=?", (member.id, self.config_data['promotion_channel']))
        promotion = self.c.fetchall()

        try:
            promotion_ratio = len(promotion)/len(non_promotion)
        except ZeroDivisionError:
            promotion_ratio = 0
        
        return promotion_ratio

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def load_history(self, ctx):
        '''
        Loads historic message data into the database
        '''

        if not await bot_utils.await_confirm(ctx, "**Pull 30 day history?**\n\nThis will be slow! (~**3** hours)"):
            return

        self.c.execute("DELETE FROM SelfPromotion")
        self.conn.commit()

        prog_count = 0
        sent_message = await ctx.send(f"Step {prog_count} of {len(ctx.guild.channels)}")

        search_limit = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        print(search_limit)
        for c in ctx.guild.channels:
            prog_count += 1
            await sent_message.edit(content=self.gen_prog(prog_count, len(ctx.guild.channels)))

            count = 0
            if str(c.type) == 'text':
                async for m in c.history(after=search_limit, limit=150000, before=datetime.datetime.utcnow()):
                    self.c.execute("INSERT INTO SelfPromotion(user_id, date, channel) VALUES (?, ?, ?)", (m.author.id, m.created_at, m.channel.id))
                    self.conn.commit()
            print(f"{c} : {count}")

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

import discord
from discord.ext import commands
import json
import bot_utils
import datetime
import sqlite3

class Moderation(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Moderation/config.json') as f:
            self.config_data = json.load(f)

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def rule(self, ctx, rule_number, member: discord.Member =None):
        '''Shows a server rule.'''
        await ctx.message.delete()

        embed = discord.Embed(title=f"Rule {rule_number}", description=self.config_data['rules'][rule_number], color=bot_utils.red)
        embed.set_footer(text=f"Sent by: {ctx.author}")
        
        if member:
            embed.set_author(name=f"{member} please see the rule below:")

        warn_mesg = await ctx.send(member.mention, embed=embed)

        if member:
            self.c.execute("INSERT INTO Moderation_warnings(timestamp, user_id, reason, jump_link) VALUES (?, ?, ?, ?)", (datetime.datetime.utcnow(), member.id, rule_number, warn_mesg.jump_url))
            self.conn.commit()
            await ctx.guild.get_channel(self.bot.config['bot_log_channel']).send(f"Warning issued to {member}.\n{warn_mesg.jump_url}")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def show_infactions(self, ctx, member: discord.Member):
        self.c.execute("SELECT * FROM Moderation_warnings WHERE user_id=?", (member.id, ))
        results = self.c.fetchall()
        
        await ctx.send(f"{len(results)} warning(s) recorded for {member}")

def setup(bot):
    bot.add_cog(Moderation(bot))
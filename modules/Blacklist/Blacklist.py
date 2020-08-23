import discord
from discord.ext import commands
import json
import bot_utils
import sqlite3

class Blacklist(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Blacklist/config.json') as f:
            self.config_data = json.load(f)

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        try:
            if any(r.id in bot_utils.admin_roles for r in message.author.roles):
                return
        except:
            pass
            # print(f"ERROR USER: {message.author}")

        self.c.execute("SELECT * FROM Blacklist")
        banned_terms = self.c.fetchall()

        # Delete messages
        for s in banned_terms:
            if s[0] in message.content.lower():
                await message.delete()

                if self.config_data["blacklist_message"] != "":
                    try:
                        await message.author.send(self.config_data["blacklist_message"])
                        dm_status = "DM Sent"
                    except:
                        dm_status = "DM **FAILED** to send."

                embed=discord.Embed(title="Blacklist Message Removed", description=f"Message: '{message.content}'\n     By: {message.author.mention}\n     In: {message.channel.mention}", color=bot_utils.red)

                await bot_utils.log(self.bot, title="Blacklist Message Removed", color=bot_utils.red, From=f"{message.author.mention} [{message.author}]", Message=f"```{message.content[:1000]}```", DM=dm_status)
                await self.bot.get_channel(self.bot.config['bot_log_channel']).send(embed=embed)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def add_banned_term(self, ctx, term):
        """Adds blacklisted terms to the database"""
        term = term.lower()

        try:
            self.c.execute("INSERT INTO Blacklist(term) VALUES (?)", (term,))
            self.conn.commit()
            await ctx.send(f"'{term}' added to blacklist!")
        except:
            await ctx.send(f"'{term}' failed to add to blacklist!")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def remove_banned_term(self, ctx, term):
        """Removes blacklisted terms from the database"""
        # Load blacklist terms
        try:
            self.c.execute("DELETE FROM Blacklist WHERE term=?", (term,))
            self.conn.commit() 
            await ctx.send(f"'{term}' removed from blacklist!")
        except:
            await ctx.send(f"'{term}' failed to remove from blacklist!")

    @commands.command(hidden=True)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def view_banned_terms(self, ctx):
        '''Shows the currently blacklisted terms.'''
        self.c.execute(f"SELECT * FROM Blacklist")
        banned_terms = self.c.fetchall()

        terms = "\n".join(str(t[0]) for t in banned_terms)

        embed = discord.Embed(title="Banned Terms", description=terms, color=bot_utils.red)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Blacklist(bot))
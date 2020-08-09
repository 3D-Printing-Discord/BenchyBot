
import discord
from discord.ext import commands
import json
import bot_utils
import sqlite3

class MessageScanner(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/MessageScanner/config.json') as f:
            self.config_data = json.load(f)

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_message(self, message):
        self.c.execute("SELECT * FROM MessageScanner")
        banned_terms = self.c.fetchall()

        if message.author != self.bot.user:
            for s in banned_terms:
                if s[0] in message.content.lower().split(' '):
                    embed=discord.Embed(title="Message Containing Scan Term Found", color=bot_utils.red)
                    embed.add_field(name="Author", value=f"{message.author} : {message.author.mention}", inline=False)
                    embed.add_field(name="Channel", value=f"{message.channel.mention}", inline=False)
                    embed.add_field(name="Scan Word", value=s[0], inline=False)
                    embed.add_field(name="Message Content", value=f"```{message.content[:1000]}```", inline=False)
                    embed.add_field(name="Message Link", value=f"[Message Link]({message.jump_url})", inline=False)

                    await self.bot.get_channel(self.bot.config['bot_log_channel']).send(embed=embed)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def add_scan_term(self, ctx, term):
        """Adds scan terms to the database"""
        term = term.lower()

        try:
            self.c.execute("INSERT INTO MessageScanner(search_term) VALUES (?)", (term,))
            self.conn.commit()
            await ctx.send(f"'{term}' added to scanner!")
        except:
            await ctx.send(f"'{term}' failed to add to scanner!")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def remove_scan_term(self, ctx, term):
        """Removes scan terms from the database"""

        # Load blacklist terms
        try:
            self.c.execute("DELETE FROM MessageScanner WHERE search_term=?", (term,))
            self.conn.commit() 
            await ctx.send(f"'{term}' removed from scanner!")
        except:
            await ctx.send(f"'{term}' failed to remove from scanner!")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def view_scan_terms(self, ctx):
        '''Shows the currently scanned terms.'''
        self.c.execute(f"SELECT * FROM MessageScanner")
        banned_terms = self.c.fetchall()

        terms = "\n".join(str(t[0]) for t in banned_terms)

        embed = discord.Embed(title="Scanned Terms", description=terms, color=bot_utils.red)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def add_scan_term_bulk(self, ctx, *, term):
        """Adds scan terms to the database"""
        term = term.lower()

        terms = term.split(" ")
        print(terms)

        for i in terms:
            try:
                self.c.execute("INSERT INTO MessageScanner(search_term) VALUES (?)", (i,))
                self.conn.commit()
                await ctx.send(f"'{i}' added to scanner!")
            except:
                await ctx.send(f"'{i}' failed to add to scanner!")

def setup(bot):
    bot.add_cog(MessageScanner(bot))
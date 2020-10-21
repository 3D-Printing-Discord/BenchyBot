
import discord
from discord.ext import commands
import json

class Requests(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Requests/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # IGNORE BOT
        if payload.member == self.bot.user:
            return

        if '💵' in "":
            await handle_request(payload)

    async def handle_request(self, payload):
        pass 

    async def handle_delete(self, payload):
        pass 

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.command()
    async def test_ad(self, ctx):
        await ctx.message.delete()

        embed = discord.Embed(title="Service Request", description=ctx.message.content)

        sent_message = await ctx.send(embed=embed)
        await sent_message.add_reaction('💵')

        self.bot.databasehandler.sqlquery("INSERT INTO Requests(message_id, owner_id) VALUES (?, ?)", ctx.message.id, ctx.author.id return_type='commit')

def setup(bot):
    bot.add_cog(Requests(bot))

import discord
from discord.ext import tasks, commands
import json
import bot_utils
import math


MAX = 500
OWNER = 417018558908989451
PING = True

class Library(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.background_task.start()

        # self.config_data = []
        # with open('modules/Library/config.json') as f:
        #     self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == 419972029463265280:
            if not message.author.id == OWNER:
                meter = self.bot.databasehandler.sqlquery("SELECT * FROM Library", return_type='one')[0]
                meter += 25
                if meter > MAX:
                    meter = MAX
                self.bot.databasehandler.sqlquery("UPDATE Library SET value=?", meter, return_type='commit')

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def init_library(self, ctx):
        self.bot.databasehandler.sqlquery("DELETE FROM Library", return_type='commit')
        meter = MAX
        self.bot.databasehandler.sqlquery("INSERT INTO Library (value) VALUES (?)", meter, return_type='commit')
        meter = self.bot.databasehandler.sqlquery("SELECT * FROM Library", return_type='one')[0]
        await ctx.send(meter)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def library(self, ctx):
        meter = self.bot.databasehandler.sqlquery("SELECT * FROM Library", return_type='one')[0]
        await ctx.send(meter)

    @tasks.loop(seconds=600)
    async def background_task(self):
        await self.bot.wait_until_ready()

        meter = self.bot.databasehandler.sqlquery("SELECT * FROM Library", return_type='one')[0]

        if meter < 5:
            if PING:
                PING = True
                await self.bot.get_channel(419972029463265280).send(f"Hey <@{OWNER}>! Looking awful quiet around here!")
        else:
            PING = False

        adj_meter = math.floor(meter/(MAX/20))
        percentage = meter / (MAX/100)
        desc = f"BOOK METER: \n|{'█'*adj_meter}{'░'*(20-adj_meter)}| {percentage:>3.0f}% |"
        await self.bot.get_channel(419972029463265280).edit(topic=desc)

        meter -= 1
        if meter < 0:
            meter = 0
        self.bot.databasehandler.sqlquery("UPDATE Library SET value=?", meter, return_type='commit')

    async def cog_unload():
        self.background_task.stop()


def setup(bot):
    bot.add_cog(Library(bot))
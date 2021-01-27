
import discord
from discord.ext import commands, tasks
import json
import sqlite3
import bot_utils
import datetime
import asyncio

DEBUG = False

class Scheduler(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Scheduler/config.json') as f:
            self.config_data = json.load(f)

        self.closed_embed = discord.Embed(title="Channel Closed", description=self.config_data['closed_message'], color=bot_utils.red)
        self.open_embed   = discord.Embed(title="Channel Open", description=self.config_data['open_message'], color=bot_utils.green)

        self.channel_schedule.start()

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def add_schedule(self, ctx, channel_id, *, days):
        '''
        Adds a schedule.
        '''

        try:
            self.bot.databasehandler.sqlquery(
                "INSERT INTO Scheduler(channel_id, days) VALUES (?, ?)",
                channel_id, days,
                return_type='commit'
            )
            await ctx.send("Done!")

        except:
            await ctx.send("Failed to add schedule")

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def remove_schedule(self, ctx, channel_id):
        '''
        Deletes a schedule.
        '''

        try:
            self.bot.databasehandler.sqlquery(
                "DELETE FROM Scheduler WHERE channel_id=?",
                channel_id,
                return_type='commit'
            )
            await ctx.send("Done!")
        except:
            await ctx.send("Failed to remove schedule")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def show_schedule(self, ctx):
        '''
        Shows the currently implemented schedules.
        '''

        # GET Schedules COMMANDS
        result = self.bot.databasehandler.sqlquery(
            "SELECT * FROM Scheduler",
            return_type='all'
        )

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- SCHEDULES ({len(result)}) ---\nCHANNEL NAME                        | DAYS ACTIVE')

        # ADD COMMANDS TO PAGINATOR
        for s in result:
            chan_name = self.bot.get_channel(s[0]).name
            white_space = " "*(35 - len(chan_name))
            paginator.add_line(f"#{chan_name}{white_space}| {self.days_code_2_human(s[1])}")

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page, delete_after=60)

    @tasks.loop(hours=1)
    async def channel_schedule(self):
        
        # AWAIT BOT TO BE READY
        await self.bot.wait_until_ready()

        schedules = self.bot.databasehandler.sqlquery(
            "SELECT * FROM Scheduler",
            return_type='all'
        )

        for s in schedules:
            if DEBUG: print(s)

            channel_object = self.bot.get_channel(s[0])

            if str(datetime.datetime.now().weekday()) in s[1]:
                if DEBUG: print("ON DAY")
                if s[2] != 'O':
                    if DEBUG: print("UPDATING STATE TO ON")
                    await channel_object.send(embed=self.open_embed)
                    await channel_object.set_permissions(channel_object.guild.default_role, read_messages=False, send_messages=True)
                    self.bot.databasehandler.sqlquery(
                        "UPDATE Scheduler SET state = 'O' WHERE channel_id=?;",
                        s[0],
                        return_type='commit'
                    )
                else:
                    if DEBUG: print("NO UPDATE")
            else:
                if DEBUG: print("OFF DAY")
                if s[2] != 'C':
                    if DEBUG: print("UPDATING STATE TO OFF")
                    await channel_object.send("Channel will close in 5 mins!")

                    await asyncio.sleep(270)

                    await channel_object.send("Channel closing in 30 seconds!")

                    await asyncio.sleep(30)

                    await channel_object.send(embed=self.closed_embed)
                    await channel_object.set_permissions(channel_object.guild.default_role, read_messages=False, send_messages=False)
                    self.bot.databasehandler.sqlquery(
                        "UPDATE Scheduler SET state = 'C' WHERE channel_id=?;",
                        s[0],
                        return_type='commit'
                    )
                else:
                    if DEBUG: print("NO UPDATE")

    def days_code_2_human(self, input_str):
        lookup_dict = {
            '0': 'Mon ',
            '1': 'Tue ',
            '2': 'Wed ',
            '3': 'Thu ',
            '4': 'Fri ',
            '5': 'Sat ',
            '6': 'Sun '
        }

        output = input_str
        for k, v in lookup_dict.items():
            output = output.replace(k, v)

        return output

    def cog_unload():
        self.channel_schedule.stop()

def setup(bot):
    bot.add_cog(Scheduler(bot))
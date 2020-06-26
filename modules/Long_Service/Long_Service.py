
import discord
from discord.ext import commands, tasks
import json
import datetime
import sqlite3
import bot_utils

class Long_Service(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Long_Service/config.json') as f:
            self.config_data = json.load(f)

        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()

        self.apply_long_service_roles.start()

    # @tasks.loop(seconds=5)
    @tasks.loop(hours=12)
    async def apply_long_service_roles(self):

        # AWAIT BOT TO BE READY
        await self.bot.wait_until_ready()

        print("[!] Updating Long Service Roles")

        for server in self.config_data['servers'].values():

            guild = self.bot.get_guild(server['server_id'])

            for member in guild.members:

                time_delta = datetime.datetime.utcnow()-member.joined_at

                for role in server['roles'].values():

                    if time_delta > datetime.timedelta(role['days']):

                        role_obj = guild.get_role(role['role_id'])

                        if not role_obj.id in [a.id for a in member.roles]:

                            await member.add_roles(role_obj)

                            if role['message'] != "":
                                await member.send(role['message'])

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def output_dates(self, ctx, days=0):
        output_string = f"```\nUSERS OVER {days} DAYS MEMBERSHIP:        Days:"


        for member in ctx.guild.members:

            # CREATE TIME DELTA
            time_delta = datetime.datetime.utcnow()-member.joined_at
            time_delta_string = f"{time_delta}".split(" ")[0]
            
            if time_delta > datetime.timedelta(days):
                # CREATE WHITE SPACE
                space = " "*(40-len(f"{member}"))

                # APPEND USER TO STRING
                output_string = output_string + (f"\n{member}{space}{time_delta_string}")
        
        # CLOSE CODE BLOCK
        output_string = output_string + "```"

        if len(output_string) > 1900:
            await ctx.send("Output too long.")
        else:
            await ctx.send(output_string)

def setup(bot):
    bot.add_cog(Long_Service(bot))
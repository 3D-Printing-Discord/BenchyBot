
import discord
from discord.ext import tasks, commands
import json
import asyncio
import bot_utils
import datetime

class Mute(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Mute/config.json') as f:
            self.config_data = json.load(f)

        self.bg_unmute.start()

    @commands.command(aliases=['self_mute'])
    async def mute_self(self, ctx, time):
        '''
        Applies a mute to yourself for a set number of mins.
        '''

        try:
            time=float(time)
        except:
            await ctx.send("I didnt recognise that time!\nUsage: `?mute_mute [time to mute in mins]`")
            return

        if not await bot_utils.await_confirm(ctx, f"Confirm that you ({ctx.author}) want muting for {time} mins?"):
            return

        timestamp_end = datetime.datetime.utcnow() + datetime.timedelta(minutes=time)

        await self.mute_apply(ctx.author, timestamp_end)
        await ctx.send(
            embed=discord.Embed(
                title="Mute",
                description=f"{ctx.author} has been muted for {time} mins.\nExpires `{timestamp_end.strftime('%Y-%m-%d %H:%M')}`",
                color=bot_utils.green
            )
        )
            
    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def mute(self, ctx, member: discord.Member, time):
        '''Apply a mute to a member for a set number of mins.'''

        try:
            time = float(time)
        except:
            await ctx.send("```\nError\n- Please enter a valid time in mins.\n```")
            return
            
        timestamp_end = datetime.datetime.utcnow() + datetime.timedelta(minutes=time)

        await self.mute_apply(member, timestamp_end)
        await ctx.send(
            embed=discord.Embed(
                title="Mute",
                description=f"{member} has been muted for {time} mins.\nExpires `{timestamp_end.strftime('%Y-%m-%d %H:%M:%S')}`",
                color=bot_utils.green,
            )
        )

    async def mute_apply(self, member, timestamp_end):
        role_obj = member.guild.get_role(self.config_data['mute_role'])
        await member.add_roles(role_obj)

        self.bot.databasehandler.sqlquery(
            "INSERT INTO Mute_current_mutes(userid, expires_at) VALUES (?, ?)",
            member.id, timestamp_end,
            return_type='commit'
        )

    async def mute_remove(self, member):
        role_obj = member.guild.get_role(self.config_data['mute_role'])
        await member.add_roles(role_obj)
        await member.remove_roles(role_obj)

        self.bot.databasehandler.sqlquery(
            "DELETE FROM Mute_current_mutes WHERE userid=?",
            member.id,
            return_type='commit'
        )

    @tasks.loop(seconds=60)
    async def bg_unmute(self):
        expired_mutes = self.bot.databasehandler.sqlquery(
            "SELECT * FROM Mute_current_mutes WHERE expires_at>?",
            datetime.datetime.utcnow(),
            return_type='all',
        )

        for i in expired_mutes:
            guild = self.bot.get_guild(167661427862142976)
            member = guild.get_member(i[0])

            await self.mute_remove(member)

    @bg_unmute.after_loop
    async def post_bg_unmute(self):
        if self.bg_unmute.failed():
            import traceback
            error = self.background_demand_log.get_task().exception()
            traceback.print_exception(type(error), error, error.__traceback__)

    async def cog_unload():
        self.bg_unmute.stop()

def setup(bot):
    bot.add_cog(Mute(bot))
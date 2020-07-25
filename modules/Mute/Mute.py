
import discord
from discord.ext import commands
import json
import asyncio
import bot_utils

class Mute(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Mute/config.json') as f:
            self.config_data = json.load(f)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def mute(self, ctx, member: discord.Member, time=None):
        '''Apply a mute to a member for a set number of mins.'''

        try:
            time = float(time)
        except:
            ctx.send

        role_obj = ctx.guild.get_role(self.config_data['mute_role'])
        await member.add_roles(role_obj)
        embed = discord.Embed(title="Mute", description=f"{member} has been muted for {time} mins.", color=bot_utils.green)
        await ctx.send(embed=embed)

        if time is None:
            return
            
        await asyncio.sleep(time * 60)

        await member.add_roles(role_obj)
        await member.remove_roles(role_obj)
        embed = discord.Embed(title="Mute", description=f"{member} has been unmuted.", color=bot_utils.green)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Mute(bot))
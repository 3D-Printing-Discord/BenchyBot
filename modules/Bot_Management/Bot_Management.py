
import discord
from discord.ext import commands
import json
import bot_utils
import datetime

class Bot_Management(commands.Cog):
    version = "v1.0"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['info'])
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def bot_info(self, ctx):
        '''
        Provides info on the bot status.
        '''

        # CREATE EMBED
        embed = discord.Embed(title=f"Bot Info", description="", color=bot_utils.green)

        # DECLARE BOT VERSION 
        embed.add_field(name="Discord.py Version", value=self.bot.version, inline=False)

        # DECLARE MODULES
        embed.add_field(name=f"Loaded Modules ({len(self.bot.cogs)})", value="\n".join([f"{v.version} - {m}" for m, v in self.bot.cogs.items()]), inline=False)

        # UPTIME
        embed.add_field(name="Uptime", value=(datetime.datetime.utcnow()-self.bot.start_time), inline=False)


        await ctx.send('```To load modules use:   load_module [module name]\nTo unload modules use: unload_module [module name]\nTo reload modules use: reload_module [module name]\n```', embed=embed)

    @commands.command(aliases=['ulm'])
    @commands.has_any_role(*bot_utils.admin_roles)
    async def module_unload(self, ctx, module):
        """Unloads modules from the bot."""
        if module == "Bot_Management":
            await ctx.send("```\nERROR:\nCannot unload Bot_Management at runtime!\n```")
            return
        
        try:
            self.bot.unload_extension(f"modules.{module}.{module}")
            print(f"[!] {module} was unloaded")
            await ctx.send(f"```\nCommand Received:\n{module} unloaded successfully.\n```")
        except:
            await ctx.send(f"```\nERROR:\nCannot unload {module}!\n```")

    @commands.command(aliases=['lm'])
    @commands.has_any_role(*bot_utils.admin_roles)
    async def module_load(self, ctx, module):
        """Loads modules to the bot."""
        if module == "Bot_Management":
            await ctx.send("```\nERROR:\nCannot load Bot_Management at runtime!\n```")
            return

        try:
            self.bot.load_extension(f"modules.{module}.{module}")
            print(f"[!] {module} was loaded")
            await ctx.send(f"```\nCommand Received:\n{module} loaded successfully.\n```")
        except:
            await ctx.send(f"```\nERROR:\nCannot load {module}!\n```")

    @commands.command(aliases=['rlm'])
    @commands.has_any_role(*bot_utils.admin_roles)
    async def module_reload(self, ctx, module):
        """Reloads bot modules."""
        if module == "Bot_Management":
            await ctx.send("```\nERROR:\nCannot reload Bot_Management at runtime!\n```")
        else:
            try:
                self.bot.unload_extension(f"modules.{module}.{module}")
                self.bot.load_extension(f"modules.{module}.{module}")
                print(f"[!] {module} was reloaded")
                await ctx.send(f"```\nCommand Received:\n{module} reloaded successfully.\n```")
            except:
                await ctx.send(f"```\nERROR:\nCannot load {module}!\n```")
            
    @commands.command(aliases=['dlm'])
    @commands.has_any_role(*bot_utils.admin_roles)
    async def module_debug(self, ctx, module):
        """Loads modules with full console debug"""
        print("~~ Loading with debug ~~")
        print(f"Input: {module}")
        if module == "Bot_Management":
            await ctx.send("```\nERROR:\nCannot load Bot_Management at runtime!\n```")
        else:
            print("Attempting to load")
            self.bot.load_extension(f"modules.{module}.{module}")
            print(f"[!] {module} was loaded")
            await ctx.send(f"```\nCommand Received:\n{module} loaded successfully.\n```")

def setup(bot):
    bot.add_cog(Bot_Management(bot))
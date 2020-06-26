
import discord
from discord.ext import commands
import json
import bot_utils
import datetime

class Bot_Management(commands.Cog):
    version = "v1.0"

    def __init__(self, bot):
        self.bot = bot

        # GET CONFIG DATA
        # self.config_data = []
        # with open('modules/Bot_Management/config.json') as f:
            # self.config_data = json.load(f)

    @commands.command(hidden=True)
    @commands.check(bot_utils.is_admin)
    async def info(self, ctx):

        # CREATE EMBED
        embed = discord.Embed(title=f"Bot Info", description="", color=bot_utils.green)

        # DECLARE BOT VERSION 
        embed.add_field(name="Bot Version", value=self.bot.version, inline=False)

        # DECLARE MODULES
        embed.add_field(name=f"Loaded Modules ({len(self.bot.cogs)})", value="\n".join([f"{m} - {v.version}" for m, v in self.bot.cogs.items()]), inline=False)

        # UPTIME
        embed.add_field(name="Uptime", value=(datetime.datetime.utcnow()-self.bot.start_time), inline=False)


        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.check(bot_utils.is_admin)
    async def unload_module(self, ctx, module):
        """Unloads modules from the bot."""
        if module == "Bot_Management":
            await ctx.send("Cannot unload Bot_Management at runtime!")
        else:
            try:
                self.bot.unload_extension(f"modules.{module}.{module}")
                print(f"[!] {module} was unloaded")
                await ctx.send(f"Command Received: {module} unloaded successfully.")
            except:
                await ctx.send(f"ERROR: Cannot unload {module}!")

    @commands.command(hidden=True)
    @commands.check(bot_utils.is_admin)
    async def load_module(self, ctx, module):
        """Loads modules to the bot."""
        if module == "Bot_Management":
            await ctx.send("Cannot load Bot_Management at runtime!")
        else:
            try:
                self.bot.load_extension(f"modules.{module}.{module}")
                print(f"[!] {module} was loaded")
                await ctx.send(f"Command Received: {module} loaded successfully.")
            except:
                await ctx.send(f"ERROR: Cannot load {module}!")

    @commands.command(hidden=True)
    @commands.check(bot_utils.is_admin)
    async def reload_module(self, ctx, module):
        """Reloads bot modules."""
        if module == "Bot_Management":
            await ctx.send("Cannot reload Bot_Management at runtime!")
        else:
            try:
                self.bot.unload_extension(f"modules.{module}.{module}")
                self.bot.load_extension(f"modules.{module}.{module}")
                print(f"[!] {module} was reloaded")
                await ctx.send(f"Command Received: {module} reloaded successfully.")
            except:
                await ctx.send(f"ERROR: Cannot load {module}!")
            
    @commands.command(hidden=True)
    @commands.check(bot_utils.is_admin)
    async def debug_load_module(self, ctx, module):
        """Loads modules with full console debug"""
        print("Loading with debug")
        print(f"Input: {module}")
        if module == "Bot_Management":
            await ctx.send("Cannot load Bot_Management at runtime!")
        else:
            print("Attempting to load")
            self.bot.load_extension(f"modules.{module}.{module}")
            print(f"[!] {module} was loaded")
            await ctx.send(f"Command Received: {module} loaded successfully.")

def setup(bot):
    bot.add_cog(Bot_Management(bot))
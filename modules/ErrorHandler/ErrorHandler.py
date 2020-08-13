
import discord
from discord.ext import commands
import json
import sys
import traceback

class ErrorHandler(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/ErrorHandler/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        # IGNORE HANDLED ERRORS 
        if hasattr(ctx, "handled_in_local"):
            return

        # IGNORE SPECIFIC ERROR TYPES
        if isinstance(error, commands.CommandNotFound):
            return

        print("~~ Global Error Handler ~~~")
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
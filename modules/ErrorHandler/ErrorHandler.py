
import discord
from discord.ext import commands
import json
import sys
import traceback
import bot_utils

class ErrorHandler(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot
        
        self.report = True

        # self.config_data = []
        # with open('modules/ErrorHandler/config.json') as f:
        #     self.config_data = json.load(f)

    # @commands.Cog.listener()
    # async def on_command_error(self, error):
    #     print(error)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        # IGNORE HANDLED ERRORS 
        if hasattr(ctx, "handled_in_local"):
            return

        # HANDLE SPECIFIC ERROR TYPES
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"{ctx.author.mention} either you dont have permission to use `{ctx.prefix}{ctx.command}` or you\'re in the wrong channel!\nUse `?help` for a list of commands for which you have permission to use.")
            return

        print("~~ Global Error Handler ~~~")
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        if self.report:

            traceback_formatted="".join(traceback.format_exception(type(error), error, error.__traceback__))
            error_message = f"```\n'Ignoring exception in command {ctx.command}\n{traceback_formatted}\n```"

            if len(error_message) < 2000:
                embed=discord.Embed(title=f"An Error Occured", description=error_message, color=bot_utils.red)
            else:
                embed=discord.Embed(title=f"An Error Occured", description=f"```An error occured.\nThe traceback is too long for discord. See the logfile for info.\n```", color=bot_utils.red)

            embed.set_author(name="Jumplink to Error", url=ctx.message.jump_url)
            await self.bot.get_channel(self.bot.config['bot_log_channel']).send(embed=embed)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def error(self, ctx):
        '''Causes an error. (for debug use only)'''
        sldgkh

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def toggle_errors(self, ctx):
        '''
        Enable or disable logging of bot errors to the audit log.
        '''
        if self.report:
            self.report = False
            await ctx.send('Error Reporting Disabled.')
        else:
            self.report = True 
            await ctx.send('Error Reporting Enabled.')


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
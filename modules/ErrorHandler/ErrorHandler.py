import discord
from discord.ext import commands
import sys
import traceback
import bot_utils


class ErrorHandler(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot
        self.report = True

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

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("A required argument was missing!\nView Command help with `?help <command name>")
            return

        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("A command argument was invalid. Usually this means a member couldnt be found!\nView Command help with `?help <command name>")
            return

        # FETCH ED
        await ctx.send(
            "**Uh-oh!**\nSomething went wrong!\nDont worry! <@212995985901617154> will fix it!"
        )

        print(
            '~~ Global Error Handler ~~~',
            f'Ignoring exception in command {ctx.command}:',
            file=sys.stderr
        )
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        if self.report:
            traceback_formatted = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            error_message = f"```\n'Ignoring exception in command {ctx.command}\n{traceback_formatted}\n```"

            if len(error_message) < 2000:
                embed = discord.Embed(
                    title="An Error Occured",
                    description=error_message,
                    color=bot_utils.red
                )
            else:
                embed = discord.Embed(
                    title="An Error Occured",
                    description="```An error occured.\nThe traceback is too long for discord. See the logfile for info.\n```",
                    color=bot_utils.red
                )
                
            embed.set_author(
                name="Jumplink to Error",
                url=ctx.message.jump_url
            )
            await self.bot.get_channel(self.bot.config['bot_log_channel']).send(embed=embed)

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def error(self, ctx):
        '''Causes an error. (for debug use only)'''
        sldgkh

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def errors_toggle(self, ctx):
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

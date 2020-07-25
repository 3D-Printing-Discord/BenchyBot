
import discord
from discord.ext import commands
import json
from pyfiglet import Figlet
import bot_utils

class Ascii(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        # self.config_data = []
        # with open('modules/Ascii/config.json') as f:
        #     self.config_data = json.load(f)

    @commands.has_any_role(*bot_utils.reg_roles)
    @commands.command()
    async def ascii(self, ctx, *, input_string):
        '''Displays ascii art.'''
        await ctx.message.delete()

        args, input_string = bot_utils.simple_parse(input_string, font='f')

        if args['font'] == None:
            args['font'] = 'standard'

        try:
            custom_fig = Figlet(font=args['font'])
            await ctx.send(f"```\n{custom_fig.renderText(input_string)}\n[Requested by: {ctx.author}]\n```")
        except FontNotFound:
            await ctx.send(f"I couldnt find font '{args['font']}'!\n\nFont list: https://github.com/pwaller/pyfiglet/tree/master/pyfiglet/fonts")

def setup(bot):
    bot.add_cog(Ascii(bot))
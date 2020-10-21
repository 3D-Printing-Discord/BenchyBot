
import discord
from discord.ext import commands
import json
import bot_utils
import os

class PCPart(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/PCPart/config.json') as f:
            self.config_data = json.load(f)

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def pcpart(self, ctx, *, table_info=None):
        '''Displays PCPartPicker build tables.'''

        if len(ctx.message.attachments) > 0:
            filename = 'runtimefiles/pcpart.csv'

            if os.path.isfile(filename):
                os.remove(filename)
            await ctx.message.attachments[0].save(filename)

            f = open(filename, "r")
            table_info = f.readlines()
            f.close()

        else:
            table_info = table_info.split('\n')

        embed = discord.Embed(title=f"Build Info", description=table_info[0], color=bot_utils.green)
        embed.set_footer(text=f"Command sent by: {ctx.author}")
        embed.set_author(name="PCPartPicker", icon_url="https://cdn.discordapp.com/attachments/339978089411117076/732579258752434246/Unknown.png")

        for i in table_info[4:-3]:
            line=i.strip().split("|")
            line[0] = line[0].replace("**","")

            embed.add_field(name=line[0], value=f"{line[1]} : {line[2]}", inline=False)

        total_price = table_info[-2].split("|")
        total_price[2] = total_price[2].replace("**","")
        embed.add_field(name="Total Price", value=total_price[2], inline=False)

        
        await ctx.send(embed=embed)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(PCPart(bot))
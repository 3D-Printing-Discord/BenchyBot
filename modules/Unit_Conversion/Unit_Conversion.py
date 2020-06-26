
import discord
from discord.ext import commands
import json
from quantulum3 import parser
import time
import bot_utils

class Unit_Conversion(commands.Cog):
    '''
    Converts units in messages into metric. Not the other way. Metric only.
    '''

    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.measures = (
            ("inch", "mm", 25.4, 0),
            ("foot", "m", 0.3048, 0),
            ("yard", "m", 0.9144, 0),
            ("pound", "kg", 0.453592, 0),
            ("ounce", "g", 28.3495, 0),
            ("stone", "kg", 6.35029, 0),
            ("gallon", "l", 4.54609, 0),
            ("mile", "km", 1.60934, 0),
            ("degree fahrenheit", "C", 5/9, -32),
            ("degree celsius", "F", 9/5, 32)
        )

        # self.config_data = []
        # with open('modules/Unit_Conversion/config.json') as f:
        #     self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        version = "v1.0"

        if message.author == self.bot.user:
            return

        quants = parser.parse(message.content)
        channel = message.channel

        # embed=discord.Embed(title="Unit Conversions")
        embed=discord.Embed(title=" ")

        for q in quants:
            for conversion in self.measures:

                if str(q.unit) == conversion[0]:

                    if str(q.unit) == "degree fahrenheit":
                        result = (q.value + conversion[3]) * conversion[2]
                    elif str(q.unit) == "degree celsius":
                        result = (q.value * conversion[2]) + conversion[3]
                    else:
                        result = q.value * conversion[2]

                    output_unit = conversion[1]

                    ouput_string = f"{q.value} {q.unit} = {result:.2f} {output_unit}"
                    embed.add_field(name="Conversion:", value=ouput_string, inline=False)

        if len(embed.fields) > 0 and await bot_utils.await_react_confirm(message, self.bot, emoji='📝'):
            await message.channel.send(embed=embed)

    @commands.command()
    async def convert(self, ctx, string):
        quants = parser.parse(ctx.message.content)

        embed=discord.Embed(title="Unit Conversions")

        for q in quants:
            for conversion in self.measures:

                if str(q.unit) == conversion[0]:

                    result = q.value * conversion[2]
                    output_unit = conversion[1]

                    ouput_string = f"{q.value} {q.unit} = {result:.2f} {output_unit}"
                    embed.add_field(name="Conversion:", value=ouput_string, inline=False)
        
        if len(embed.fields) > 0:
            await ctx.send(embed=embed)


    async def generate_output(self, string, channel):
        embed=discord.Embed(title=string)
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Unit_Conversion(bot))
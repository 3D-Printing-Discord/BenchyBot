
import discord
from discord.ext import commands
import json
from quantulum3 import parser
import time
import bot_utils
from currency_converter import CurrencyConverter

class Unit_Conversion(commands.Cog):
    '''
    Converts units in messages into metric. Not the other way. Metric only.
    '''

    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.measures = {
            "inch":   ["mm", 25.4, 0],
            "foot":   ["m", 0.3048, 0],
            "yard":   ["m", 0.9144, 0],
            "pound":  ["kg", 0.453592, 0],
            "ounce":  ["g", 28.3495, 0],
            "stone":  ["kg", 6.35029, 0],
            "gallon": ["l", 4.54609, 0],
            "mile":   ["km", 1.60934, 0],
            "degree fahrenheit": ["C", 5/9, -32],
            "degree celsius":    ["F", 9/5, 32]
        }

        self.currencies = {
            'pound sterling': 'GBP',
            'united states dollar': 'USD',
            'canadian dollar': 'CAD',
            'australian dollar': 'AUD',
            'euro': 'EUR',
            'day kelvin kelvins': 'DKK'
        }

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

        embed=discord.Embed(title=" ")

        for q in quants:
            # print(q.unit)
            if str(q.unit) in self.measures.keys():
                conversion_units = self.measures[str(q.unit)]
                result = result = q.value * conversion_units[1] + conversion_units[2]
                output_unit = conversion_units[0]

                ouput_string = f"{q.value} {q.unit} = {result:.2f} {output_unit}"

                embed.add_field(name="Unit Conversion:", value=ouput_string, inline=False)

            elif str(q.unit) in self.currencies.keys():
                c = CurrencyConverter()

                output_strings = []
                convert_to = self.currencies.copy()
                convert_to.pop(str(q.unit))
                for currency in convert_to.values():
                    result = c.convert(q.value, self.currencies[str(q.unit)], currency)

                    output_strings.append(f"{q.value} {self.currencies[str(q.unit)]} = {result:.2f} {currency}")

                conversions_string = "\n".join(output_strings)
                embed.add_field(name="Currency Conversion:", value=conversions_string, inline=False)

            # SPECIAL CASES
            elif str(q.unit) == "attowatt gausses":
                n = q.value
                result = 0.127 * pow(92, ((36-n)/39))
                print(result)

                ouput_string = f"{q.value} AWG = {result:.4f} Ømm"

                embed.add_field(name="Unit Conversion:", value=ouput_string, inline=False)

        if len(embed.fields) > 0:
            send_embed, user = await bot_utils.await_react_confirm(message, self.bot, emoji='📝', confirm_time=300)
            if send_embed:
                embed.set_footer(text=f"Conversion Requested By: {user}")
                await message.channel.send(embed=embed)

    async def generate_output_embed(self, quants):
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

        return embed

def setup(bot):
    bot.add_cog(Unit_Conversion(bot))
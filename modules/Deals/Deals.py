
import discord
from discord.ext import commands
import json
from bs4 import BeautifulSoup
import aiohttp
import bot_utils

DEBUG = False 

class Deals(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.cur_symbol = ['£', '$', '€']

        self.config_data = []
        with open('modules/Deals/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if not message.channel.id == 728544079406825522:
            return

        await message.delete()

        # Send Loading Message
        temp_embed = discord.Embed(title="Deal", description="Embed content loading.", color=bot_utils.yellow)
        temp_embed.set_footer(text=f"Posted By: {message.author.name}")
        sent_message = await message.channel.send(embed=temp_embed)

        # Split up string
        input_string = message.content
        input_string = input_string.replace('\n', ' ')
        split_string = input_string.split(" ")
        split_string = [i for i in split_string if i != ""]

        # Grab fields
        prices = [i for i in split_string if i[0] in self.cur_symbol]
        links =  [i for i in split_string if i.startswith('http')]

        # Convert links
        markdown_links = [f"[link]({i})" if i.startswith('http') else i for i in split_string]
                
        # Create Embed
        description_content = " ".join(markdown_links)
        output_embed = discord.Embed(title="Deal", description=description_content, color=bot_utils.green)
        output_embed.set_footer(text=f"Posted By: {message.author.name}")

        if prices == []: prices = ['N/a']
        joined_prices = " / ".join(prices)
        output_embed.add_field(name="Price", value=joined_prices, inline=False)

        # HANDLE LINKS
        if links != []:
            for i in links:
                if DEBUG: print("Getting Title")
                title = await self.get_page_title(i)

                if DEBUG: print("Adding Field")
                output_embed.add_field(name="Link", value=f"[{title}]({i})", inline=False)

        await sent_message.edit(embed=output_embed)

        if await bot_utils.await_react_confirm(sent_message, self.bot, confirm_time=15, emoji='❌'):
            await sent_message.delete()

    async def get_page_title(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.read()
                soup = BeautifulSoup(text.decode('utf-8'), 'html.parser')

                f = open("log.txt", "w")
                f.write(soup.prettify())
                f.close()

                return soup.title.string
        
def setup(bot):
    bot.add_cog(Deals(bot))

import discord
from discord.ext import commands
import json
import bot_utils
import re
from urllib.parse import urlparse


class Amazon(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        # self.config_data = []
        # with open('modules/Amazon/config.json') as f:
        #     self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message): 

        if self.bot.user.id == message.author.id:
            return

        # FIND LINKS      
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)

        links = []
        replace = False
        force = False
        for s in urls:
            if ('amazon' in s) or ('amzn' in s):
                try:
                    if any([i in s for i in ['.co.uk', '.com', '.de']]):
                        short_link = ('https://smile.' + re.search('ama*zo*n.*?\/', s)[0] + re.search('(dp|gp)\/.*?(\/|\?)', s)[0])
                    else:
                        short_link = ('https://www.' + re.search('ama*zo*n.*?\/', s)[0] + re.search('(dp|gp)\/.*?(\/|\?)', s)[0])
                    new_content = message.content.replace(s, short_link)

                    replace = True
                    if 'tag=' in s:
                        force = True
                except:
                    print(f"ERROR IN AMAZON {s}")

            if ('aliexpress' in s) and ('?' in s):
                endex = s.index('?')
                short_link = s[:endex] #.replace('item/', 'item//')
                new_content = message.content.replace(s, short_link)

                replace = True

            if ('ebay' in s):
                # \/itm\/.*?\?
                # ebay.*?\/
                short_link = ('https://www.' + re.search('ebay.*?\/', s)[0] + 'itm/' + re.search('\/itm\/.*?\?', s)[0].split('/')[-1][:-1])
                new_content = message.content.replace(s, short_link)
                replace = True
            
        if replace:
            if force:
                await self.replace_message(message, new_content)
            else:
                if await bot_utils.await_react_confirm(message, self.bot, emoji='🤏', confirm_time=20, delete_after=True):
                    await self.replace_message(message, bot_utils.sanitize_input(new_content))

    async def replace_message(self, message, new_message):
        await message.delete()
        await message.channel.send(f"**{message.author.mention} said:**\n{new_message}\n`LINKS SHORTENED`")


def setup(bot):
    bot.add_cog(Amazon(bot))

import discord
from discord.ext import commands
import json
import bot_utils
import random
import asyncio

class Showcase(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.reacts = ['👍', '❤️', '🆒', '😍', '📸', '🎉', '🎊']

        self.config_data = []
        with open('modules/Showcase/config.json') as f:
            self.config_data = json.load(f)

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def showcase_whitelist(self, ctx):
        '''View the whitelist of sites for the showcase module.'''
        sites = self.bot.databasehandler.sqlquery('SELECT * FROM showcase_whitelist', return_type='all')

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- WHITELIST SITES ({len(sites)}) ---\nIf a message contains any of the following terms it will be allowed.\n---------------------------')

        # ADD COMMANDS TO PAGINATOR
        for s in sites:
            paginator.add_line(f"{s[0]}")

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page, delete_after=60)

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def showcase_whitelist_add(self, ctx, term):
        '''Adds an entry to the showcase whitelist.'''
        if await bot_utils.await_confirm(ctx, f"Add '`{term}`' to the whitelist?", delete_after=False, confirm_time=60):
            self.bot.databasehandler.sqlquery('INSERT INTO showcase_whitelist(site) VALUES (?)', term, return_type='commit')

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def showcase_whitelist_remove(self, ctx, term):
        '''Removes an entry from the showcase whitelist.'''
        if await bot_utils.await_confirm(ctx, f"Remove '`{term}`' from the whitelist?", delete_after=False, confirm_time=60):
            self.bot.databasehandler.sqlquery('DELETE FROM showcase_whitelist WHERE site=?', term, return_type='commit')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.config_data['showcase_channels']:

            if any(role.id in bot_utils.admin_roles for role in message.author.roles):
                return

            whitelist_items = self.bot.databasehandler.sqlquery('SELECT * FROM showcase_whitelist', return_type='all')

            # print(whitelist_items)

            check = [True for i in whitelist_items if i[0] in message.content]
            # print(check)

            if message.attachments or any(check):
                await asyncio.sleep(30)
                await message.add_reaction(random.choice(self.reacts))
            else:
                try:
                    await message.author.send(self.config_data['showcase_message'])
                    await message.author.send(f"```\n{message.content}\n```")
                    dm_status = "Sent Successfully"
                except discord.errors.Forbidden:
                    dm_status = "**Failed To Send**"

                await message.delete()
                await bot_utils.log(self.bot, title="Showcase Message Removed", color=bot_utils.red, From=f"{message.author.mention} [{message.author}]", Message=f"```{message.content[:1000]}```", DM=dm_status)
                # await message.guild.get_channel(self.bot.config['bot_log_channel']).send(f"Showcase message from {message.author} removed.```{message.content}```")

def setup(bot):
    bot.add_cog(Showcase(bot))
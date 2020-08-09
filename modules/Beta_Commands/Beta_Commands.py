
import discord
from discord.ext import commands
import json
import asyncio
import random 
import bot_utils
import py7zr
import shutil
import requests
import re

DEBUG = False

COMBO = '''
   _____                _           _ 
  / ____|              | |         | |
 | |     ___  _ __ ___ | |__   ___ | |
 | |    / _ \| '_ ` _ \| '_ \ / _ \| |
 | |___| (_) | | | | | | |_) | (_) |_|
  \_____\___/|_| |_| |_|_.__/ \___/(_)
  '''

class Beta_Commands(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot
        self.yeets = 0

        # self.config_data = []
        # with open('modules/Beta_Commands/config.json') as f:
        #     self.config_data = json.load(f)

    # @commands.Cog.listener()
    # async def on_message(self, message):
        
    #     if message.content.startswith("^nrolelist"):
    #         await message.channel.send("Hello,\n\nBecause there is a limit on the max number of roles, we are unable to continue adding each new printer that releases. We will be restructuring printer roles in the future so stay tuned!")

    #     if message.channel.id == 339978089411117076:
    #         if len(message.content) > 280:
    #             await message.delete()

    #             API_KEY = 'AxTd4eNGF4vhXT8MUoJD-BkOVUMsJN-r'
    #             import requests 

    #             url = 'https://pastebin.com/api/api_post.php'
    #             data = {
    #                 'api_dev_key':'AxTd4eNGF4vhXT8MUoJD-BkOVUMsJN-r',
    #                 'api_option':'paste',
    #                 'api_paste_code':message.content
    #                 }

    #             r = requests.post(url, data=data)
    #             print(r.content)
                
    #             embed = discord.Embed(title=f"{message.author} (Shortened Message)", description=f"{message.content[:280]}...\n\n[Read Full Message]({r.content.decode('utf-8')})")
    #             await message.channel.send(embed=embed)


    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     x = re.findall('(Y|y)(e|E){2,}(T|t)', message.content)
    #     if x and message.author.id != self.bot.user.id:
    #         await message.add_reaction(":yeet:730210956793086034")
    #         self.yeets = self.yeets + len(x)
    #         if len(x) > 1:
    #             await message.channel.send(f"```{COMBO}```")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def dmstaff(self, ctx, *, message=None):
        role = ctx.guild.get_role(690993018357940244)

        temp_staff_string = "\n".join([str(i) for i in role.members])

        if not await bot_utils.await_confirm(ctx, f"Send DM?\n\nDM ({len(role.members)}):\n{message}\n\nTo:```{temp_staff_string}```", confirm_time=60):
            return

        for n, i in enumerate(role.members):
            user_message = await ctx.send(f"Sending message to: {i}...")
            try:
                await i.send(message)
                await user_message.edit(content=f"Sending message to: {i}... Done!")
            except:
                await user_message.edit(content=f"Sending message to: {i}... **Failed to send!**")

        await ctx.send("Complete.")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def ban_log(self, ctx):

        if not ctx.channel.id == 339978089411117076:
            return

        bans = await ctx.guild.bans()

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- BANS ({len(bans)}) ---')

        # ADD COMMANDS TO PAGINATOR
        for i in bans:
            reason = str(i.reason).strip('\n')
            newline = '\n'
            paginator.add_line(f"{i.user.name} : {reason}{newline}")

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page, delete_after=300)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def backup(self, ctx):
        pass
        print("Copying files")
        new_path = shutil.copy('database_prod.db', 'runtimefiles/backup')
        print("New Path = ", new_path)
        print("Done Copying")


        # , password='secret'
        print("Zipping")
        with py7zr.SevenZipFile('runtimefiles/backup.7z', 'w') as archive:
            archive.writeall('runtimefiles/backup', 'base')
        print("Done Zipping")

    @commands.command()
    async def add_printer(self, ctx, *, printer):
        '''Beta Command: Adds a printer to your name.'''
        nick_string = f"{ctx.author.name} | {printer}"
        if len(nick_string) > 32:
            await ctx.send("Name string too long.")
        else:
            await ctx.author.edit(nick=nick_string)
            await ctx.send("Done.")

    @add_printer.error
    async def add_printer_handler(self, ctx, error):
        """Local Error Handler For add_printer."""

        # Check if our required argument inp is missing.
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to provide a printer name. Use the command like this (no [ ] needed):\n`?add_printer [Printer Name]`")

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def set_status(self, ctx, *, status):
        # activity = discord.CustomActivity("Test")¶
        # self.bot.change_presence()

        activity=discord.Activity(type=discord.ActivityType.listening, name=status)
        # activity = discord.Game(status)
        await self.bot.change_presence(activity=activity)

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if 'anet' in message.content.lower():
    #         await message.add_reaction('🔥')

    # @commands.command()
    # @commands.cooldown(1, 3*60*60, commands.BucketType.user)
    # async def add_emoji(self, ctx):
    #     if DEBUG: print("add_emoji")

    #     hours_to_wait = random.uniform(3, 5)
    #     if DEBUG: print(hours_to_wait)

    #     embed = discord.Embed(title="Adding Custom Emoji", description=f"Hi {ctx.author.name}. You are currently {random.randint(5463,10956)} in the line. Estimated wait time: {hours_to_wait:.1f} Hours", color=bot_utils.red)
    #     await ctx.send(embed=embed)

    #     if DEBUG: print("sleeping")
    #     await asyncio.sleep(hours_to_wait*60*60)
    #     if DEBUG: print("Woken Up")

    #     embed = discord.Embed(title="Adding Custom Emoji", description=f"Hi {ctx.author.name}. Your number is up! Please come forward.", color=bot_utils.green)
    #     sent_message = await ctx.send(embed=embed)
        
    #     if DEBUG: print("resolve")
    #     if await bot_utils.await_confirm(ctx, "Step forwards?", confirm_time=120):
    #         await ctx.send("It appears you dont have the correct paperwork. Please check your paperwork and rejoin the line.")
    #         embed = discord.Embed(title="Adding Custom Emoji", description=f"{ctx.author.name} didnt have the right paperwork!", color=bot_utils.red)
    #         await sent_message.edit(embed=embed)
    #     else:
    #         await ctx.send(f"Hello? {ctx.author.mention}? Are you there? No? Ok! Next customer please!")
    #         embed = discord.Embed(title="Adding Custom Emoji", description=f"{ctx.author.name} missed their number.", color=bot_utils.red)
    #         await sent_message.edit(embed=embed)

def setup(bot):
    bot.add_cog(Beta_Commands(bot))
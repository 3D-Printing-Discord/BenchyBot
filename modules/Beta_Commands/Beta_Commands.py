
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
import datetime
from pytz import timezone
import pytz
import secrets
import pyqrcode
import feedparser
import html2markdown
import datetime
import asyncio
import matplotlib
import textstat
import os
# import cexprtk
# import speedtest


from PIL import Image
import pytesseract

DEBUG = False

timezone_lookup = {}

for tz in pytz.all_timezones:
    try:
        key = tz.split("/")[1].upper()
    except:
        key = tz.upper()

    timezone_lookup[key] = timezone(tz)

# timezones = {
#     "UTC": pytz.utc,
#     "EASTERN": timezone('US/Eastern'),
#     "PACIFIC": timezone("US/Pacific"),
#     "UK": timezone('Europe/London'),
#     "AUS": timezone('Europe/London')
# }

buttons = {
    '⚪':0xffffff,
    '🟢':0x00cc00,
    '🔵':0x0c71e0,
    '🟣':0xb200ff,
    '🟠':0xffa500,
    '🟡':0xffd700
    }

sent_items =[]

class Beta_Commands(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot
        self.yeets = 0
        self.live = True
        self.voted = []
 
        # self.config_data = []
        # with open('modules/Beta_Commands/config.json') as f:
        #     self.config_data = json.load(f)

    # @commands.command()
    # @commands.has_any_role(*bot_utils.admin_roles)
    # async def math(self, ctx, input_string):
    #     solution = cexprtk.evaluate_expression(input_string, {})
    #     await ctx.send(f"```\n{solution}\n```")

    # @commands.command()
    # @commands.has_any_role(*bot_utils.admin_roles)
    # async def RSS(self, ctx):

    #     print("Parsing Feeds")

    #     feed_list = [
    #         'http://allabout3dprinting.com/feed/',
    #         'http://3dprintingindustry.com/feed',
    #         'http://3dprinting.com/news/feed',
    #         'http://3dprint.com/feed',
    #         "https://www.youtube.com/feeds/videos.xml?channel_id=UCb8Rde3uRL1ohROUVg46h1A"
    #     ]

    #     feeds = [feedparser.parse(i) for i in feed_list]

    #     for f in feeds:
    #         for n in f.entries[:3]: 
    #             if n.link not in sent_items:
    #                 await ctx.send(n.link)
    #                 sent_items.append(n.link)
    #                 await asyncio.sleep(30)

    #     # for f in feeds:
    #     #     # print(f)
    #     #     for i in f.entries[:5]:
    #     #         print("  - ", i.title, end=" ")
    #     #         if not i.link in sent_items:
    #     #             # embed=discord.Embed(title=i.title, description=html2markdown.convert(i.summary), author=i.author)
    #     #             await ctx.send(i.link)

    #     #             sent_items.append(i.link)
    #     #             await asyncio.sleep(30)


    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def exec(self, ctx, *, cmd):
        if ctx.message.author.id != 212995985901617154:
            await ctx.send("`NOT AUTHORISED`")
            return
        print(f"Executing: {cmd}")
        os.system(f'{cmd} > runtimefiles/exec.log')

        with open('runtimefiles/exec.log') as f:
            logs = f.readlines()

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```py\n', suffix='\n```')

        for i in logs:
            paginator.add_line(discord.utils.escape_markdown(i).strip())

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def logs(self, ctx):
        os.system('tail -n 50 logfile.log > runtimefiles/temp_log.log')

        with open('runtimefiles/temp_log.log') as f:
            logs = f.readlines()

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```py\n', suffix='\n```')

        for i in logs:
            paginator.add_line(discord.utils.escape_markdown(i).strip())

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page)


    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def status(self, ctx):
        os.system('systemctl status bb > runtimefiles/status_log.log')

        with open('runtimefiles/status_log.log') as f:
            status_info = f.read()

        await ctx.send(f"```ruby\n{status_info}```")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def read(self, ctx, message="Test"):
        await ctx.send(f"{Pessage}\n\n{textstat.flesch_reading_ease(message)}")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def ch_act(self, ctx, days=7):
        '''Shows channel activity.'''
        await ctx.send("Im doing it but this will take a few moments.")

        result = []
        data = []

        timestamp = datetime.datetime.utcnow() - datetime.timedelta(days = int(days))

        # CREATE PAGINATOR
        print("Creating Paginator")
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- Channels ({len(ctx.guild.channels)}) ---')

        # ADD CHANNELS TO PAGINATOR
        print("Getting histories")
        for i, c in enumerate(ctx.guild.channels):

            print(f"Now loading channel: {i:<3} of {len(ctx.guild.channels)}")

            if isinstance(c, discord.TextChannel):
                count = 0

                async for message in c.history(after=timestamp, limit=None):
                    count += 1
                    print(f"  - Messages Loaded from channel {i}: {count}\r", end="")

                print(count)
                paginator.add_line(f"{c.name}, {count}")

                data.append([c.name, count])

        print("Sending Paginator")
        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page)
        await ctx.send(ctx.author.mention)
        # for c in ctx.guild.channels:
        #     result.append(f"{c.name:>35}: 0")
        # await ctx.send("\n".join(result))

    @commands.command()
    async def ping(self, ctx):
        '''Latency Check.'''
        now = datetime.datetime.utcnow()
        _in = ctx.message.created_at

        msg = await ctx.send(f"__**Pong!**__")

        out = msg.created_at

        in_time = now - _in
        out_time = msg.created_at - now
        loop_time = out - _in 

        await msg.edit(content=f"__**Pong!**__```\n  IN: {in_time}\n OUT: {out_time}\nLOOP: {loop_time}```")


    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def hist(self, ctx, member: discord.Member):
        async for i in member.history(limit=10):
            try:
                await ctx.send(f"```\nMSG: {i.content[:1000]}\n\n\nFrom: {i.author}\nEmbeds: {len(i.embeds)}\nAttachments: {len(i.attachments)}\n```", files=[await n.to_file() for n in i.attachments], embed=self.list_get(i.embeds, 0))
            except:
                await ctx.send("Empty Message")

    def list_get(self, lst, index, default=None):
        try:
            return lst[index]
        except IndexError:
            return default

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def say(self, ctx, *, message):

        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def code(self, ctx, *, url_string="No Content"):
        '''Generates a QR Code with the info provided. Can be used for websites etc.'''

        await ctx.message.delete()

        try:
            url = pyqrcode.create(url_string)
        except Exception:
            await ctx.send("Sorry, I couldnt make that Code.")
            return

        url.png('runtimefiles/code.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xff])

        loaded_file = discord.File("runtimefiles/code.png", filename="code.png")
        await ctx.send(file=loaded_file)

    # @commands.command()
    # @commands.has_any_role(*bot_utils.admin_roles)
    # async def test_ad(self, ctx):
    #     '''Test'''
    #     await ctx.message.delete()

    #     embed = discord.Embed(title="Service Request", description=ctx.message.content[9:])

    #     sent_message = await ctx.send(embed=embed)
    #     await sent_message.add_reaction('💵')


    #     def check_wait(reaction, user):
    #         # print("CHECK")
    #         # print(str(reaction.emoji) == '💵')
    #         # print(user != self.bot.user)
    #         # print(sent_message.id == reaction.message.id)
    #         return str(reaction.emoji) == '💵' and user != self.bot.user and sent_message.id == reaction.message.id

    #     print("Going to wait!")
    #     reaction, user = await self.bot.wait_for('reaction_add', timeout=10000, check=check_wait)
    #     print("Done Waiting")

    #     print(f"Sending DM to {user}")
    #     embed = discord.Embed(title="Service Request", description=f"**Thanks for responsing to this request.**\n\nAlthough connected by the 3DPrinting server any deals you make are to happen outside of the server and are completed at your own risk.\n\nYou may now contact the user via DM to further discuss this request: {ctx.message.author.mention}\n\nCopy of the origional request:\n{ctx.message.content[9:]}\n\n`This is sample text and should be changed to be more descriptive`")
    #     await user.send(embed=embed)
    #     await reaction.remove(user)
            

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def key(self, ctx):
        '''Generates a secure cryptographic key... then sends it making it insecure!'''
        await ctx.send(secrets.token_urlsafe())

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def read_image(self, ctx):
        if len(ctx.message.attachments) == 0:
            await ctx.send("Please send an image!")

        await ctx.message.attachments[0].save("runtimefiles/ocrimage.png")
        await ctx.send(pytesseract.image_to_string(Image.open("runtimefiles/ocrimage.png")))

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def toggle_button(self, ctx):
        if not ctx.author.id == 212995985901617154:
            return

        if self.live:
            self.live = False
            await ctx.send("Button is now off")
        else:
            self.live = True 
            await ctx.send("Button is now on")


    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def embed(self, ctx, *, message):
        await ctx.message.delete()
        embed=discord.Embed(description=message)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def test_embed(self, ctx):
        embed=discord.Embed(title=" TEST EMBED", description=f"This embed tests embedding an image")

        embed.set_image(url="https://knowpathology.com.au/app/uploads/2018/07/Happy-Test-Screen-01-825x510.png")

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def the_button(self, ctx):
        '''
        ALL PRAISE THE BUTTON
        '''

        if not ctx.author.id == 212995985901617154:
            return

        embed=discord.Embed(title="THE BUTTON", description=f"loading...\n")
        message = await ctx.send(embed=embed)

        leader_board = []

        await asyncio.sleep(3)

        await message.add_reaction('⚪')

        while self.live:
            leader_board = sorted(leader_board, key=lambda x: x[2], reverse=True)
            leader_board.append(await self.the_button_manager(ctx,message,leader_board))

        embed=discord.Embed(title="THE BUTTON", description=f"GAME OVER")
        await message.edit(embed=embed)
        await message.clear_reactions()
        self.voted = []

    def numbers_to_trophies(self, number):

        number += 1

        if number == 1:
            return '🥇'
        elif number == 2:
            return '🥈'
        elif number == 3:
            return '🥉'
        else:
            return number

    def rounds_from_colour(self, colour):

        my_list = {
            '⚪':15,
            '🟢':31,
            '🔵':81,
            '🟣':273,
            '🟠':1282,
            '🟡':9177
        }

        return rounds[colour]

    async def the_button_manager(self, ctx, message, leader_board):
        if DEBUG: print("the_button_manager")
        timeout_time = 30

        # GENERATE LEADER BOARD
        if DEBUG: print("generating board")

        if len(leader_board) == 0:
            no_players = "~ No High Scores ~"
            joined_leader_board = f"```{no_players:^30}```"
        else:
            strings_leader_board = [f"{self.numbers_to_trophies(n)} {i[0]} {str(i[1]):<30} {str(i[2])} pts" for n, i in enumerate(leader_board)]
            joined_leader_board = "```\n" + "\n".join(strings_leader_board) + "\n```"
        print(joined_leader_board)

        if DEBUG: print("resetting score")
        score = 0

        for k, v in buttons.items():
            if DEBUG: print("Colour Update")
            # await message.clear_reactions()
            # await message.add_reaction(k)
            for i in range(self.rounds_from_colour(k)):
                if DEBUG: print("Score Update")
                score += 10

                if DEBUG: print("   - Updating Message")
                embed=discord.Embed(title=f"{k} THE BUTTON {k}", description=f"Click the button...\nScore: `{score}` points!\n\nLeaderboard:\n{joined_leader_board}", color=v)
                await message.edit(embed=embed)

                if DEBUG: print("   - Setting check")
                # DEF CHECK OF RESPONSE
                def check(reaction, user):
                    return str(reaction.emoji) in buttons and message.id == reaction.message.id and not (user in self.voted)


                if DEBUG: print("   - Awaiting Check")
                try:
                    reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout_time, check=check)
                    if DEBUG: print("   - Press detected!")
                    embed=discord.Embed(title=f"{k} THE BUTTON {k}", description=f"**WE HAVE A WINNER!**\n\n{user}\nScore: `{score}`\n\nLeaderboard:\n{joined_leader_board}", color=v)
                    await message.edit(embed=embed)
                    await asyncio.sleep(10)
                    self.voted.append(user)
                    return [k, user, score]

                except asyncio.TimeoutError:
                    if DEBUG: print("   - No press detected!")
                    pass

        if DEBUG: print("   - Setting check")
        # DEF CHECK OF RESPONSE
        def check(reaction, user):
            return str(reaction.emoji) in buttons and message.id == reaction.message.id and not (user in self.voted)

        reaction, user = await ctx.bot.wait_for('reaction_add', check=check)
        if DEBUG: print("   - Press detected!")
        embed=discord.Embed(title=f"{k} THE BUTTON {k}", description=f"**WE HAVE A WINNER!**\n\n{user}\nScore: {score}\n\nLeaderboard:\n{joined_leader_board}", color=v)
        await message.edit(embed=embed)
        await asyncio.sleep(10)
        self.voted.append(user)
        return [k, user, score]


    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def after_dark(self, ctx):
        await ctx.message.delete()

        await ctx.author.send("This is a test message which should contain an invitation! As soon as Acid lets me know what text he wants here I shall make it so!")

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    async def time_zones(self, ctx):
        '''View the timezones that can be used.'''

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- TIMEZONES ({len(timezone_lookup.keys())}) ---')

        def split_list(input_list, no_lists=3):
            input_list = sorted(input_list)

            lis_a = input_list[0::3]
            lis_b = input_list[1::3]
            lis_c = input_list[2::3]
            return zip(lis_a, lis_b, lis_c)

        # ADD COMMANDS TO PAGINATOR
        for a, b, c in split_list(timezone_lookup.keys()):
            paginator.add_line(f"{a:<15}{b:<15}{c}")

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page)

    @commands.command()
    async def time(self, ctx, time_zone=None):
        '''Used to get the current time in a timezone.'''

        if not time_zone:
            await ctx.send("You must supply a timezone to lookup: `?time [time_zone]`")
            return 

        time_zone = time_zone.upper()

        UTC_TIME = datetime.datetime.now(tz=datetime.timezone.utc)
        try:
            LOCAL_TIME = UTC_TIME.astimezone(timezone_lookup[time_zone])
        except:
            await ctx.send("Sorry, I dont know that timezone. try `?time_zones` for a list of available timeszones.")
            return

        await ctx.send(f"The current time in `{timezone_lookup[time_zone]}` is: `{LOCAL_TIME.strftime('%I:%M %p')}`")

    @commands.Cog.listener()
    async def on_message(self, message):
        prefixes = ['!', '^']

        for p in prefixes:
            if message.content.startswith(p):
                try:
                    if not (message.content[1] == p or message.content[1] == ' '):
                        embed=discord.Embed(description=f"The `{p}` prefix is now obsolete and may be removed. Consider switching to the new `?` prefix for commands.")
                        await message.channel.send(embed=embed)
                except Exception:
                    pass


        if message.content.startswith(('^help', '!help')):
            embed=discord.Embed(description="Try `?help`")
            await message.channel.send(embed=embed)

        if message.content.startswith("^rolelist") or message.content.startswith("^addrole"):
            await message.channel.send("Hello,\n\nBecause there is a limit on the max number of roles, we are unable to continue adding each new printer that releases. We will be restructuring printer roles in the future so stay tuned!")

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
    async def request_text(self, ctx):

        bot = self.bot
        channel = ctx.channel
        member = ctx.author
        message = "Please respond with your text"
        timeout=5

        request_message = await channel.send(message)
        await request_message.add_reaction('❌')

        def message_check(m):
            return m.author == member and m.channel == channel

        def reaction_check(reaction, user):
            return str(reaction.emoji) == '❌' and user != bot.user and request_message.id == reaction.message.id 
            
        done, pending = await asyncio.wait([
                        bot.wait_for('message', check=message_check, timeout=timeout),
                        bot.wait_for('reaction_add', check=reaction_check, timeout=timeout)
                    ], return_when=asyncio.FIRST_COMPLETED)

        try:
            return_object = done.pop().result()
        except:
            exception = done.pop().exception()
            return_object = False

        for future in pending:
            future.cancel()

        await request_message.delete()

        if type(return_object) == discord.message.Message:
            await return_object.delete()
            return return_object.content
        else:
            return False

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def speed(self, ctx):
        servers = []
        

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def ban_log(self, ctx):
        '''Shows all server bans.'''

        if not ctx.channel.id == 339978089411117076:
            return

        bans = await ctx.guild.bans()

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- BANS ({len(bans)}) ---')

        # ADD COMMANDS TO PAGINATOR
        for i in bans:
            reason = str(i.reason).strip('\n')
            paginator.add_line(f"{i.user.name} : {reason}")

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page, delete_after=300)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def backup(self, ctx):
        pass
        print("Copying files")
        new_path = shutil.copy('logfile.log', 'runtimefiles/backup')
        print("New Path = ", new_path)
        print("Done Copying")


        # , password='secret'
        print("Zipping")
        with py7zr.SevenZipFile('runtimefiles/backup.7z', 'w') as archive:
            archive.writeall('runtimefiles/backup', 'base')
        print("Done Zipping")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def lmgtfy(self, ctx, *, term):
        '''Delivers Sass.'''
        await ctx.message.delete()
        await ctx.send(f"<https://lmgtfy.com/?q={term.replace(' ', '+')}>")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def ntest(self, ctx, *, content="Test"):
        pass

    async def bot_log(self, title="Log", author=None, description=None, color=bot_utils.blue, **kwargs):
        embed=discord.Embed(title=title, description=description, color=bot_utils.blue)

        for k, v in kwargs.items():
            embed.add_field(name=k, value=v, inline=False)

        await self.bot.get_channel(self.bot.config['bot_log_channel']).send(embed=embed)

    @commands.command()
    async def add_printer(self, ctx, *, printer):
        '''Beta Command: Adds a printer to your name.'''
        nick_string = f"{ctx.author.name} | {printer}"
        if len(nick_string) > 32:
            embed=discord.Embed(title="Name String Too Long", description=f"The printer name you submitted was too long! Try a shorter name or an abbreviation.")
            await ctx.send(embed=embed)
        else:
            await ctx.author.edit(nick=nick_string)
            embed=discord.Embed(title="Name Changed", description=f"{ctx.author.mention} your name has been changed successfully.")
            await ctx.send(embed=embed)

    @add_printer.error
    async def add_printer_handler(self, ctx, error):
        """Local Error Handler For add_printer."""

        # Check if our required argument inp is missing.
        if isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(title="You need to provide a printer name.", description="Use the command like this:\n`?add_printer [Printer Name]`\n\nExample\n`?add_printer Prusa i3`")
            await ctx.send(embed=embed)
            ctx.handled_in_local = True

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def set_status(self, ctx, *, status):
        activity=discord.Activity(type=discord.ActivityType.listening, name=status)
        await self.bot.change_presence(activity=activity)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def check_bg(self, ctx):
        await ctx.send(f"```BG TASK ACTIVE: {self.bot.get_cog('HelpChannels').background_ActivityCheck.is_running()}```")


    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def restart_bg(self, ctx):
        try:
            self.bot.get_cog('HelpChannels').background_ActivityCheck.start()
            print("```BG TASK RESTARTED SUCCESSFULLY```")
        except Exception as e:
            print(e)

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if 'anet' in message.content.lower().split():
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
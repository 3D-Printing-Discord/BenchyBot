
import discord
from discord.ext import commands
import json
import asyncio
import random 
import bot_utils
import py7zr
import shutil

DEBUG = False

class Beta_Commands(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        # self.config_data = []
        # with open('modules/Beta_Commands/config.json') as f:
        #     self.config_data = json.load(f)

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
        print("Edit Name")
        nick_string = f"{ctx.author.name} | {printer}"
        if len(nick_string) > 32:
            await ctx.send("Name string too long.")
        else:
            await ctx.author.edit(nick=nick_string)
            await ctx.send("Done.")

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
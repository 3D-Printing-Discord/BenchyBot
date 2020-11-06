
import discord
from discord.ext import commands
import json
import bot_utils
import asyncio

DEBUG = False

class Entry(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.temp_list = []

        # self.config_data = []
        # with open('modules/Entry/config.json') as f:
        #     self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # APPLY NEW MEMBER ROLE
        await member.add_roles(member.guild.get_role(746659973970264114))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # IGNORE BOT
        if payload.member == self.bot.user:
            return

        messages = [i[0] for i in self.bot.databasehandler.sqlquery("SELECT * FROM Entry", return_type='all')]
        if DEBUG: print(messages)

        if payload.message_id in messages:
            # GET GUILD
            guild = self.bot.get_guild(payload.guild_id)

            # GET ROLE
            role_obj = guild.get_role(746659973970264114)

            # GET MESSAGE
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            # GET REACTOR
            member = payload.member

            # REMOVE ROLE
            await member.remove_roles(role_obj)

            # SEND WELCOME DM
            embed = discord.Embed(title="Welcome!", description='''**Access to the server has now been unlocked for your account. Please note that you will be unable to send messages for the first 10 minutes after joining.**

Why dont you **introduce yourself** in <#168046101860057088>, or **dive straight into 3D Printing chat** in <#167661427862142976>?

**If you need assistance with your printer:**
Check out the <#758751108419551242> channel for more info.

**Tell us about your latest project:**
Share works in progress in <#417157493244952587>
Share completed prints in <#684578465139392556>
Chat about projects in <#690193739460640856>

**Discuss printer parts and designs in the technical channels:**
<#224661367326638081>
<#339862027789008898>
<#224661007593635851>
<#639158967645241364>

**Chat with various reps from:**
<#458449165886947328>
<#458972392132313088>
<#549886242041626625>
<#505104121045450755>
<#502967857445994509>
<#459343408662708248>

**Chat about 3d modelling in our dedicated modelling channels:**
<#510307234396241920>
<#258761552520282112>
<#510307351614455828>
<#741990939626831932>
''')
            await member.send(embed=embed)

            # LOG
            embed = discord.Embed(title="Member Accepted Rules", description=f"{member.mention} [{member}]")
            await self.bot.get_channel(357705890046017536).send(embed=embed)

            # WAIT
            await asyncio.sleep(10)

            # REMOVE REACTION
            await message.remove_reaction('✅', member)


    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def create_entry_widget(self, ctx):
        '''Create a reaction widget to allow entry to the server.'''
        
        embed = discord.Embed(title="Agree to the Rules.", description="To indicate that you have read and agree to the server rules please click / tap the green tick.")
        message = await ctx.send(embed=embed)
        await message.add_reaction('✅')

        # self.temp_list.append(message.id)
        self.bot.databasehandler.sqlquery("INSERT INTO Entry(message_id) VALUES (?)", message.id, return_type='commit')

        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Entry(bot))
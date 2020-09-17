
import discord
from discord.ext import commands
import json
import bot_utils

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
            member = guild.get_member(payload.user_id)

            # REMOVE ROLE
            await guild.get_member(payload.user_id).remove_roles(role_obj)

            # REMOVE REACTION
            await message.remove_reaction('✅', member)

            # LOG
            embed=discord.Embed(title="Member Accepted Rules", description=f"{member.mention} [{member}]")
            await self.bot.get_channel(357705890046017536).send(embed=embed)


    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def create_entry_widget(self, ctx):
        embed = discord.Embed(title="Agree to the Rules.", description="To indicate that you have read and agree to the server rules please react to this message with a green tick.")
        message = await ctx.send(embed=embed)
        await message.add_reaction('✅')

        # self.temp_list.append(message.id)
        self.bot.databasehandler.sqlquery("INSERT INTO Entry(message_id) VALUES (?)", message.id, return_type='commit')

        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Entry(bot))
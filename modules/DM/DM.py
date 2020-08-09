import discord
from discord.ext import commands
import json
import bot_utils
import datetime

class DM(commands.Cog):
    version = "v1.0"

    def __init__(self, bot):
        self.bot = bot

        # LOAD CONFIG DATA
        self.config_data = []
        with open('modules/DM/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if(message.guild == None) and (message.author != self.bot.user) and not (message.content.startswith("?")):
            # BUILD EMBED
            embed = discord.Embed(title="Direct Message Received", color=bot_utils.yellow)
            embed.add_field(name="Sender", value=message.author.mention, inline=False)
            embed.add_field(name="Message", value=message.content, inline=False)

            # SEND EMBED TO CHANNEL
            target_channel = self.bot.get_channel(self.config_data["bot_mail_channel"])
            await target_channel.send(embed=embed)

            # RESPOND TO USER
            await message.author.send(self.config_data["bot_response"])

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def reply(self, ctx, member: discord.Member, *, message):
        '''Used to reply to DMs through the bot.'''
        await ctx.message.delete()
        await member.send(f"Message from the mods:\n{message}")
        embed = discord.Embed(title="Direct Message Response Sent", color=bot_utils.yellow)
        embed.add_field(name="To", value=member, inline=False)
        embed.add_field(name="Content", value=message, inline=False)
        embed.set_footer(text=f"Sent by: {ctx.author}")
        await ctx.guild.get_channel(self.config_data["bot_mail_channel"]).send(embed=embed)

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def page(self, ctx, *, message):
        '''Used to alert the mods. Please use in a regs channel.'''
        embed = discord.Embed(title=f"{ctx.author} is requesting assistance!", color=bot_utils.red)
        embed.add_field(name="Message", value=message, inline=False)
        await ctx.guild.get_channel(self.config_data["bot_mail_channel"]).send("@here", embed=embed)

def setup(bot):
    bot.add_cog(DM(bot))
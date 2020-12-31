
import discord
from discord.ext import commands
import json
import bot_utils
import datetime
import sqlite3

class Moderation(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Moderation/config.json') as f:
            self.config_data = json.load(f)

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await bot_utils.log(self.bot, title="Member Banned", Member=user, color=bot_utils.red)

    @commands.command(aliases=['warn'])
    @commands.has_any_role(*bot_utils.admin_roles)
    async def rule(self, ctx, rule_number, member: discord.Member=None):
        '''Shows a server rule or issues a warning.'''

        await ctx.message.delete()

        embed = discord.Embed(title=f"Rule {rule_number}", description=self.config_data['rules'][rule_number], color=bot_utils.red)
        embed.set_footer(text=f"Sent by: {ctx.author}")
        
        if member:
            embed.set_author(name=f"{member} please see the rule below:")

            warn_mesg = await ctx.send(member.mention, embed=embed)

            self.bot.databasehandler.sqlquery(
                "INSERT INTO Moderation_warnings(timestamp, user_id, reason, jump_link) VALUES (?, ?, ?, ?)",
                datetime.datetime.utcnow(), member.id, rule_number, warn_mesg.jump_url,
                return_type='commit'
            )

            log_embed = discord.Embed(title="Warning Issued", color=bot_utils.red)
            log_embed.set_footer(text=f"Issued by: {ctx.author}")
            log_embed.add_field(name="Issued to", value=f"{member} [{member.mention}]", inline=False)
            log_embed.add_field(name="Reason", value=f"Rule {rule_number}", inline=False)
            log_embed.add_field(name="Link", value=f"[Jump link]({warn_mesg.jump_url})", inline=False)

            await ctx.guild.get_channel(self.bot.config['bot_log_channel']).send(embed=log_embed)

        else:
            await ctx.send(embed=embed)

    @rule.error
    async def rule_error(self, ctx, error):
        await ctx.message.delete()

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send("Warning was not issued: Missing a required argument.")
            ctx.handled_in_local = True

        if isinstance(error, commands.MemberNotFound):
            await ctx.author.send("Warning was not issued: Could not find the user.")
            ctx.handled_in_local = True

    @commands.command(aliases=['warns'])
    @commands.has_any_role(*bot_utils.admin_roles)
    async def show_infractions(self, ctx, *, member):
        '''Shows the number and type of infractions a user has collected.'''

        try:
            member = await commands.MemberConverter().convert(ctx, member)
            banned_string = False
        except:            
            try:
                ban_entry = [i for i in await ctx.guild.bans() if i.user.name == member][0]
                member = ban_entry.user
                banned_string = str(ban_entry.reason)
            except: 
                await ctx.send("Member Not Found!")
                return
        
        results = self.bot.databasehandler.sqlquery(
            "SELECT * FROM Moderation_warnings WHERE user_id=?",
            member.id,
            return_type='all'
        )
        
        warnings = {'1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0}
        for i in results:
            warnings[i[2]] += 1

        out_string = "\n".join([f"Rule {k}: {v}" for k, v in warnings.items() if v != 0])
        out_list_string = '\n'.join([f"[Rule: {i[2]}]({i[3]})" for i in results])

        embed = discord.Embed(title=f"Infractions for {member.name}", color=bot_utils.red)
        if banned_string:
            embed.add_field(name="User is Banned:", value=f"Reason: {banned_string}", inline=False)
        if out_string:
            embed.add_field(name="Infractions Total", value=out_string, inline=False)
        if out_list_string:
            embed.add_field(name="Infractions List", value=out_list_string, inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, RawReactionActionEvent):
        if not any(role.id in bot_utils.admin_roles for role in RawReactionActionEvent.member.roles):
            return

        if 'delete' in str(RawReactionActionEvent.emoji):
            message = await self.bot.get_guild(RawReactionActionEvent.guild_id).get_channel(RawReactionActionEvent.channel_id).fetch_message(RawReactionActionEvent.message_id)

            embed = discord.Embed(title="Message Removed", color=bot_utils.red)
            embed.set_footer(text=f"Deleted by: {RawReactionActionEvent.member}")

            embed.add_field(name="Author", value=f"{message.author} [{message.author.mention}]", inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
            embed.add_field(name="Sent at", value=message.created_at, inline=False)
            if message.clean_content != "":
                embed.add_field(name="Content", value=message.clean_content, inline=False)
            embed.add_field(name="Attachments", value=len(message.attachments), inline=False)

            await self.bot.get_guild(RawReactionActionEvent.guild_id).get_channel(self.bot.config['bot_log_channel']).send(embed=embed, files=[await i.to_file() for i in message.attachments])
            await message.delete()  

def setup(bot):
    bot.add_cog(Moderation(bot))
import discord
from discord.ext import commands, flags
import json
import sqlite3
import bot_utils

class ReactRoles(commands.Cog):
    version = "v1.0"

    def __init__(self, bot):
        self.bot = bot

        # GET CONFIG DATA
        # self.config_data = []
        # with open('modules/ReactRoles/config.json') as f:
        #     self.config_data = json.load(f)

        # BUILD DATABASE CONNECTION
        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, RawReactionActionEvent):

        # IGNORE BOT
        if RawReactionActionEvent.member == self.bot.user:
            return
        
        # GET USER BANNED LIST
        self.c.execute("SELECT * FROM ReactRoles_Banned_Users WHERE user_id=?", (str(RawReactionActionEvent.member),))
        banned_users = self.c.fetchall()

        # EXIT IF THE USER IS BLOCKED
        if banned_users != []:
            return

        # GET MESSAGE FROM DATABASE
        self.c.execute("SELECT * FROM ReactRoles WHERE owning_message=? AND reaction=?", (RawReactionActionEvent.message_id, str(RawReactionActionEvent.emoji)))

        # FETCH ALL RESULTS
        role = self.c.fetchone()

        # SEND COMMAND RESPONSE
        if role == None:
            return

        # GET GUILD
        guild = self.bot.get_guild(RawReactionActionEvent.guild_id)

        # GET ROLE
        role_obj = guild.get_role(role[1])

        # APPLY ROLE
        await RawReactionActionEvent.member.add_roles(role_obj)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, RawReactionActionEvent):

        # IGNORE THE BOT
        if RawReactionActionEvent.member == self.bot.user:
            return

        # GET GUILD
        guild = self.bot.get_guild(RawReactionActionEvent.guild_id)  

        # GET MEMBER
        target_member = guild.get_member(RawReactionActionEvent.user_id)

        # GET USER BANNED LIST
        self.c.execute("SELECT * FROM ReactRoles_Banned_Users WHERE user_id=?", (str(target_member),))
        banned_users = self.c.fetchall()

        # EXIT IF THE USER IS BLOCKED
        if banned_users != []:
            return

        # GET MESSAGE FROM DATABASE
        self.c.execute("SELECT * FROM ReactRoles WHERE owning_message=? AND reaction=?", (RawReactionActionEvent.message_id, str(RawReactionActionEvent.emoji)))
        role = self.c.fetchone()

        # SEND COMMAND RESPONSE
        if role == None:
            return

        # GET ROLE
        role = guild.get_role(role[1])                      

        # REMOVE ROLE
        await target_member.remove_roles(role)

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def block_roles(self, ctx, username):
        '''
        Blocks a user from editing their roles through reaction roles.
        '''

        # GET MEMBER
        member = discord.utils.find(lambda m: username.lower() in m.name.lower(), ctx.guild.members)

        if member is None:
            await ctx.send("Member Not Found.")
            return

        member = str(member)

        self.c.execute("INSERT INTO ReactRoles_Banned_Users(user_id) VALUES (?)", (member,))
        self.conn.commit()

        await ctx.send(f"User '{member}' can no longer edit their roles.")

    @commands.command()
    @commands.check(bot_utils.is_admin)
    async def unblock_roles(self, ctx, username):
        '''
        Allows a previously blocked user to edit their roles through reaction roles again.
        '''

        # GET MEMBER
        member = discord.utils.find(lambda m: username.lower() in m.name.lower(), ctx.guild.members)

        if member is None:
            await ctx.send("Member Not Found.")
            return

        member = str(member)

        self.c.execute("DELETE FROM ReactRoles_Banned_Users WHERE user_id=?", (member,))
        self.conn.commit()

        await ctx.send(f"User '{member}' can now edit their roles again.")

    @flags.add_flag("--title", default="Pick Your Roles!")
    @flags.add_flag("--text", default="Pick your roles by reacting with the following emoji.")
    @flags.add_flag("--roles", default=None)
    @flags.add_flag("--reacts", default="🔴 🟡 🟢 🔵 🟣 🟤 🟠 🟥 🟧 🟨 🟩 🟦 🟪 🔶 🔷")
    @commands.has_any_role(*bot_utils.admin_roles)
    @flags.command()
    async def create_reaction_roles_widget(self, ctx, **flags):
        '''
        Creates a ReactionRoles Widget to assign roles.

        The ReactionRoles widget lets users select roles using reactions. You must supply a number of roles through flags to create the widget. Roles should be entered as a string of their IDs seperated by spaces.
        '''

        # SUBSTITUTE NUMBERS IF REQUESTED
        if flags['reacts'] == "numbers":
            flags['reacts'] = "1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟"

        # CONVERT ROLES INTO INTO LIST
        roles = flags['roles'].split(" ")
        roles = [int(i) for i in roles]

        if any(r.id in bot_utils.reg_roles for r in roles):
            list_of_roles = [ctx.guild.get_role(r).name for r in roles]
            string_of_roles = "\n".join(list_of_roles)
            if not await bot_utils.await_confirm(ctx, f"**----- ‼️ WARNING ‼️ -----**\nThe reaction roles widget that you are trying to create will allow any user with access to this channel to apply roles with elevated permissions!\n\nThe roles in this widget are:```\n{string_of_roles}\n```\nAre you sure you want to continue?", confirm_time=60):
                return

        # CONVERT EMOJIS INTO LIST
        reacts = flags['reacts'].split(" ")

        # MAKE SURE ROLES WERE DEFINED
        if flags['roles'] is None:
            await ctx.send("You need to define some roles.")
            return

        # CHECK THERE ARE ENOUGH EMOJI
        if len(roles) > len(reacts):
            await ctx.send("Not enough emoji!")
            return

        # REMOVE COMMAND MESSAGE
        await ctx.message.delete()

        # BUILD INITIAL EMBED
        embed = discord.Embed(title="{title}".format(**flags), description="{text}".format(**flags), color=bot_utils.green)

        # ADD FIELDS FOR EACH SPECIFIED ROLE
        for i, role in enumerate(roles):
            temp_role = ctx.guild.get_role(role)
            embed.add_field(name=temp_role, value=reacts[i], inline=True)

        # SEND EMBED
        message = await ctx.send(embed=embed)

        # ADD INITIAL REACTS
        for i in range(len(roles)):
            await message.add_reaction(reacts[i])

        # ADD MESSAGE TO DATABASE
        for i, role in enumerate(roles):
            self.c.execute("INSERT INTO ReactRoles(owning_message, role_id, reaction) VALUES (?, ?, ?)", (message.id, role, reacts[i]))
            self.conn.commit()

def setup(bot):
    bot.add_cog(ReactRoles(bot))
import discord
from discord.ext import commands, tasks
import json
import bot_utils
import datetime
from matplotlib import pyplot as plt
import sqlite3
from scipy.signal import savgol_filter
import os

class User_Management(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/User_Management/config.json') as f:
            self.config_data = json.load(f)

        # START BACKGROUND TASKS
        if self.config_data['activity_check'] != 0:
            self.user_activity_check.start()

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_member_join(self, member):

        time_delta = datetime.datetime.utcnow() - member.created_at

        channel_object = self.bot.get_channel(self.config_data['membership_channel'])

        if time_delta.days < 1:
            embed=discord.Embed(title="New Member", description=f"{member.mention} [New Discord User: {time_delta.seconds / 60} mins]", color=bot_utils.green)
        else:
            embed=discord.Embed(title="New Member", description=member.mention, color=bot_utils.green)

        await channel_object.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel_object = self.bot.get_channel(self.config_data['membership_channel'])
        
        embed=discord.Embed(title="Member Left", description=f"{member} : {member.mention}", color=bot_utils.red)
        await channel_object.send(embed=embed)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def membership_info(self, ctx):
        '''
        Gets info on the server membership.
        '''

        async with ctx.typing():

            # GET MEMEBRS LIST
            members = ctx.guild.members

            # CREATE EMBED
            embed = discord.Embed(title=f"Membership Info", description=f"Membership info for {ctx.guild}", color=bot_utils.green)

            embed.add_field(name="Total Members:", value=len(members), inline=True)

            embed.add_field(name="Online:", value=len([member for member in members if member.status == discord.Status.online]), inline=True)

            embed.add_field(name="Roles:", value=len(ctx.guild.roles), inline=True)

            embed.add_field(name="Channels:", value=len(ctx.guild.channels), inline=True)

            ### --- USER GROWTH --- ###

            # ORDER MEMEBERS
            ordered_members = sorted(members, key=lambda r: r.joined_at)

            # GENERATE USER GRAPH DATA 
            i = 0
            x_data = []
            y_data = []

            for member in ordered_members:
                i = i + 1
                x_data.append(member.joined_at)
                y_data.append(i)

            # PLOT AND SET TITLES 
            plt.plot(x_data,y_data, color="black")
            plt.xlabel('Date')
            plt.ylabel('Users')
            plt.title('User Growth')

            # SAVE IMAGE
            if os.path.isfile('runtimefiles/user_graph.png'):
                os.remove('runtimefiles/user_graph.png')
            plt.savefig('runtimefiles/user_graph.png')
            plt.clf() 

            ### --- USER ACTIVITY --- ###

            # GET ACTIVITY NUMBERS
            self.c.execute("SELECT * FROM User_Activity")
            user_activity = self.c.fetchall()

            trimmed_data = user_activity[-672:]

            # print(len(trimmed_data))
            # print(trimmed_data[0])
            # print(trimmed_data[-1])

            x_data = [datetime.datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S.%f') for d in trimmed_data]
            y_data = [int(d[1]) for d in trimmed_data]

            # PLOT AND SET TITLES 
            plt.plot(x_data,y_data, color="black")
            plt.xlabel('Date')
            plt.ylabel('Active Users')
            plt.title('7-Day User Activity')

            # SAVE IMAGE
            if os.path.isfile('runtimefiles/user_activity.png'):
                os.remove('runtimefiles/user_activity.png')
            plt.savefig('runtimefiles/user_activity.png')
            plt.clf() 


            ### --- USER CHANGE --- ###

            # GET ACTIVITY NUMBERS
            self.c.execute("SELECT * FROM User_Activity")
            user_activity = self.c.fetchall()

            # trimmed_data = user_activity[:1344]
            trimmed_data = user_activity[-672:]

            x_data = [datetime.datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S.%f') for d in trimmed_data]
            y_data = [d[2] for d in trimmed_data]

            # PLOT AND SET TITLES 
            plt.plot(x_data,y_data, color="black")
            plt.xlabel('Date')
            plt.ylabel('Users')
            plt.title('7-Day User Numbers')

            # SAVE IMAGE
            if os.path.isfile('runtimefiles/7-day-users.png'):
                os.remove('runtimefiles/7-day-users.png')
            plt.savefig('runtimefiles/7-day-users.png')
            plt.clf() 

            y_diff = savgol_filter(y_data, window_length=41, polyorder=2, deriv=1)
            # y_diff = [0] + [y - x for x, y in zip(y_data[:-1], y_data[1:])]

            # PLOT AND SET TITLES 
            plt.plot(x_data,y_diff, color="black")
            plt.xlabel('Date')
            plt.ylabel('Users')
            plt.title('7-Day User Change')

            # SAVE IMAGE
            if os.path.isfile('runtimefiles/7-user-change.png'):
                os.remove('runtimefiles/7-user-change.png')
            plt.savefig('runtimefiles/7-user-change.png')
            plt.clf() 

            ### --- SEND OBJECTS --- ###

            # SEND EMBED
            await ctx.send(embed=embed)

            # LOAD DISCORD FILE
            loaded_file_1 = discord.File("runtimefiles/user_graph.png", filename="image1.png")
            loaded_file_2 = discord.File("runtimefiles/user_activity.png", filename="image2.png")
            loaded_file_3 = discord.File("runtimefiles/7-day-users.png", filename="image3.png")
            loaded_file_4 = discord.File("runtimefiles/7-user-change.png", filename="image4.png")

            # SEND GRAPH
            await ctx.send(file=loaded_file_1)
            await ctx.send(file=loaded_file_3)
            await ctx.send(file=loaded_file_4)
            await ctx.send(file=loaded_file_2)

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def user_info(self, ctx, member: discord.Member):
        '''
        Gets info on a user
        '''

        # EMBED
        embed = discord.Embed(title=f"User Info For {member}", color=bot_utils.green)

        # DISPLAY NAME
        embed.add_field(name="Display Name", value=member.display_name, inline=False)

        # JOIN DATE
        days = str(datetime.datetime.utcnow() - member.created_at).split(" ")[0]
        created_string = f"{member.created_at.strftime('%Y-%m-%d')} ({days} days)"
        embed.add_field(name="Joined Discord on:", value=created_string, inline=False)

        # JOINED DISCORD
        days = str(datetime.datetime.utcnow() - member.joined_at).split(" ")[0]
        joined_string = f"{member.joined_at.strftime('%Y-%m-%d')} ({days} days)"
        embed.add_field(name="Joined Server on:", value=joined_string, inline=False)

        # NITRO SINCE
        if not member.premium_since is None:
            nitro_days = str(datetime.datetime.utcnow() - member.premium_since).split(" ")[0]
            nitro_string = f"{member.premium_since.strftime('%Y-%m-%d')} ({nitro_days} days)"
        else:
            nitro_string = "Not Boosting"
        embed.add_field(name="Nitro Since:", value=nitro_string, inline=False)

        # CURRENT STATUS
        embed.add_field(name="Current Status:", value=member.status, inline=False)

        # CONNECTION STATUS
        is_mobile = member.is_on_mobile()
        embed.add_field(name="On Mobile?", value=is_mobile, inline=False)

        # SELF PROMOTION
        if self.bot.get_cog('SelfPromotion'):
            percentage = self.bot.get_cog('SelfPromotion').calc_percentage(member)

            search_date = datetime.datetime.utcnow() - datetime.timedelta(days=120)
            self.c.execute("SELECT * FROM SelfPromotion WHERE user_id=? AND date > ?", (member.id, search_date))
            messages = self.c.fetchall()

            embed.add_field(name="Self Promotion", value=f"Self Promotion Percentage: `{percentage*100:.2f}`\nMessage Count Last 30 Days: `{len(messages)}`", inline=False)

        # WIKI
        if self.bot.get_cog('Wiki'):
            username = self.bot.get_cog('Wiki').get_username(member)
            if username:
                embed.add_field(name="Wiki", value=f"Wiki Username: `{username[0][1]}`", inline=False)

        # CommandsDB
        if self.bot.get_cog('CommandsDB'):
            commands = self.bot.get_cog('CommandsDB').get_user_commands(member)
            embed.add_field(name="CommandsDB", value=f"Created `{len(commands)}` commands.", inline=False)

        # ROLES
        embed.add_field(name="Roles:", value=", ".join([i.name for i in member.roles]), inline=True)

        await ctx.send(embed=embed)

    @user_info.error
    async def user_info_handler(self, ctx, error):
        """Local Error Handler for user_info."""

        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
            ctx.handled_in_local = True

        if isinstance(error, commands.BadArgument):
            await ctx.send("Member not found.")
            ctx.handled_in_local = True

    @tasks.loop(minutes=15)
    # @tasks.loop(seconds=5)
    async def user_activity_check(self):

        # AWAIT BOT TO BE READY
        await self.bot.wait_until_ready()

        members = self.bot.get_guild(self.config_data['guild_id']).members 

        online_members = len([member for member in members if member.status == discord.Status.online])

        self.c.execute("INSERT INTO User_Activity(time_stamp, online, total_users) VALUES (?, ?, ?)", (datetime.datetime.utcnow(), online_members, len(members)))
        self.conn.commit()

def setup(bot):
    bot.add_cog(User_Management(bot))
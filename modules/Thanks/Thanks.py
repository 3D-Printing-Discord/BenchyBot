
import discord
from discord.ext import commands
import json
import sqlite3
import bot_utils

class Thanks(commands.Cog):
    version = "v0.2.0"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Thanks/config.json') as f:
            self.config_data = json.load(f)
        
        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content[:1] == self.bot.config['prefix']:
            return

        if not message.author == self.bot.user:
            if "thanks" in message.content.lower():
                if self.config_data['thanks_detected'] != "":
                    await message.channel.send(self.config_data['thanks_detected'])

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if ":thanks:" in f"{reaction.emoji}": # Check if reaction is a thanks
            if (reaction.message.author.id == user.id): # Check if thanking themselves
                await reaction.remove(user)
            else: 
                # Collect info from database 
                self.c.execute("SELECT * FROM Thanks WHERE user_ID =?", (reaction.message.author.id,))
                user_thanks = self.c.fetchone()
                self.c.close()
                self.c = self.conn.cursor()
                if user_thanks == None: # if no info create new entry
                    self.c.execute(f"INSERT INTO Thanks VALUES ({reaction.message.author.id}, 1)")
                else: # else + 1
                    self.c.execute(f"UPDATE Thanks SET thanks = ? WHERE user_ID = ?", ((user_thanks[1] + 1), reaction.message.author.id))
                self.conn.commit()

    @commands.command()
    async def thanks(self, ctx):
        '''Shows the amount of thanks you have received'''
        self.c.execute("SELECT * FROM Thanks WHERE user_ID =?", (ctx.message.author.id,))
        user_thanks = self.c.fetchone()
        self.c.close()
        self.c = self.conn.cursor()
        if user_thanks == None:
            await ctx.send(f"{ctx.author.mention} has received 0 thanks!\n{self.config_data['check_message_none']}")
        else:
            await ctx.send(f"{ctx.author.mention} has received {user_thanks[1]} thanks!\n{self.config_data['check_message']}")

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def check_thanks(self, ctx):
        self.c.execute("SELECT * FROM Thanks")
        user_thanks = self.c.fetchall()

        user_list = "\n".join([f"{ctx.guild.get_member(int(m[0])).name} : {m[1]}" for m in user_thanks])

        output_string = f"```\nUSERS THANKS\n------------\n{user_list}\n```"
        await ctx.send(output_string)



def setup(bot):
    bot.add_cog(Thanks(bot))

import discord
from discord.ext import commands
import json
import praw
import bot_utils

class Reddit(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.reddit = praw.Reddit(client_id="8RRC7LMDekxHqw",
                     client_secret="Wtqi7tq2Zn9Z9x2wYFS_C_0oxMo",
                     user_agent="Benchybot")

        # self.config_data = []
        # with open('modules/Reddit/config.json') as f:
        #     self.config_data = json.load(f)

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def reddit(self, ctx, subreddit='3dprinting'):
        '''Links and previews a subreddit.'''

        await ctx.message.delete()
        
        subreddit = subreddit.lower()
        subreddit = subreddit.strip("r/")

        submissions = self.reddit.subreddit(subreddit).hot(limit=5)

        try:
            links = [f"• [{s.title}]({s.shortlink})" for s in submissions]
        except:
            await ctx.send("Didn't find that subreddit!")
            return

        output_text = "\n".join(links)

        embed = discord.Embed(title=f"r/{subreddit}", description=f"**Recent Posts:**\n{output_text}", color=bot_utils.red)
        embed.set_footer(text=f"Command sent by: {ctx.author}")
        embed.set_author(name="Reddit", icon_url="https://cdn.discordapp.com/attachments/339978089411117076/733720238469808248/rq36kl1xjxr01.png", url=f"https://www.reddit.com/r/{subreddit}")

        await ctx.send(embed=embed)
        
        
def setup(bot):
    bot.add_cog(Reddit(bot))
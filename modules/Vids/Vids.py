
import discord
from discord.ext import commands
import json
import ffmpeg

class Vids(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 339978089411117076:
            return

        if len(message.attachments) < 1:
            return
        
        img = message.attachments[0]

        try:
            h = img.height
        except: 
            return

        filename = f"runtimefiles/temp_{img.filename}"
        await img.save(filename)

        vid = ffmpeg.probe(filename)
        try:
            location = vid["format"]["tags"]["com.apple.quicktime.location.ISO6709"]
            await message.delete()

            embed=discord.Embed(title='MESSAGE DELETION', description='**YOUR RECENT MESSAGE HAS BEEN DELETED FOR YOUR OWN PRIVACY.**\n\nYour recent video message contained potentially sensitive GPS location meta-data and so has been automatically removed for your privacy. If you belive this action was taken in error please respond to this message to contact the mods.', color=bot_utils.red)
            await message.author.send(embed=embed)
            
        except:
            pass

def setup(bot):
    bot.add_cog(Vids(bot))
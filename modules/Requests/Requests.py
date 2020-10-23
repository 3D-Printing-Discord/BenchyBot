
import discord
from discord.ext import commands
import json
import bot_utils

class Requests(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Requests/config.json') as f:
            self.config_data = json.load(f)

    async def can_offer(self, member):
        return True

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != 768585449639641088:
            return

        # IGNORE BOT
        if payload.member == self.bot.user:
            return

        if await self.can_offer(payload.member):
            pass

        if '💵' == str(payload.emoji):
            db_entry = self.bot.databasehandler.sqlquery(
                "SELECT * FROM Requests WHERE message_id=?",
                payload.message_id,
                return_type='one'
            )

            if db_entry:
                channel = self.bot.get_channel(payload.channel_id)
                msg = await channel.fetch_message(payload.message_id)

                await msg.remove_reaction('💵', payload.member)

                embed = discord.Embed(
                    title="Request", 
                    description=f'''
                        Thanks for responding to this service request.\n
                        [Disclaimer here]\n
                        You may now contact the requester to discuss this opportunity over DM. The requester is: <@{db_entry[1]}>\n
                        A copy of the request is included below:\n"{msg.embeds[0].description[:750]}"
                        '''
                )
                await payload.member.send(embed=embed)
                

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if message.channel.id == 768585449639641088:
            await message.delete()

            embed = discord.Embed(title="Service Request", description=message.content)

            sent_message = await message.channel.send(embed=embed)
            await sent_message.add_reaction('💵')

            self.bot.databasehandler.sqlquery(
                "INSERT INTO Requests(message_id, owner_id) VALUES (?, ?)",
                sent_message.id, message.author.id,
                return_type='commit'
            )


def setup(bot):
    bot.add_cog(Requests(bot))
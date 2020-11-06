
import discord
from discord.ext import commands
import json
import bot_utils
import datetime


class Requests(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/Requests/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != self.config_data["channel"]:
            return

        if payload.member == self.bot.user:
            return

        if '❌' == str(payload.emoji):
            await self.manage_deletion(payload)
            return

        if '💵' == str(payload.emoji):
            await self.manage_response(payload)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if message.channel.id != self.config_data['channel']:
            return

        await message.delete()

        if not await self.check_user(message.author):
            try:
                embed = discord.Embed(
                    title="Service Request",
                    description=self.config_data['reject_post_message']
                )
                await self.member.send(embed=embed)
                DM=False
            except:
                DM=True

            await bot_utils.log(
                self.bot,
                title="Request Rejected",
                color=bot_utils.red,
                From=f"@{message.author.mention} [{message.author.name}]",
                DM=DM,
                Message=message.content
            )
            return

        await self.manage_input(message)

    async def check_user(self, member):
        return await self.check_time(member) and await self.check_messages(member)

    async def check_offer(self, member):
        return (await self.check_time(member) and await self.check_messages(member)) or bot_utils.has_any_role(member, bot_utils.admin_roles)

    async def check_time(self, member):
        days = str(datetime.datetime.utcnow() - member.created_at).split(" ")[0]
        if float(days) > 7:
            return True
        else:
            return False

    async def check_messages(self, member):
        if self.bot.get_cog('SelfPromotion'):
            messages = self.bot.get_cog('SelfPromotion').message_count(member)
            if messages > 50:
                return True
        return False

    async def manage_input(self, message):
        embed = discord.Embed(
            title="Service Request",
            description=bot_utils.sanitize_input(message.content)
        )
        sent_message = await message.channel.send(embed=embed)

        await sent_message.add_reaction('💵')
        await sent_message.add_reaction('❌')

        self.bot.databasehandler.sqlquery(
            "INSERT INTO Requests(message_id, owner_id) VALUES (?, ?)",
            sent_message.id, message.author.id,
            return_type='commit'
        )

        embed = discord.Embed(
            title="✅ Service Request",
            description=f"{self.config_data['accept_post_message']}\n\n{self.config_data['disclaimer']}"
        )
        await message.author.send(embed=embed)

    async def manage_response(self, payload):
        if not await self.check_offer(payload.member):
            try:
                embed = discord.Embed(
                title="Service Request",
                description=self.config_data['reject_post_message']
                )
                await self.member.send(embed=embed)
                DM = True
            except:
                DM = False

            await bot_utils.log(self.bot, title="Request Reponse Rejected", color=bot_utils.red, From=f"@{payload.user_id}", DM=DM)
            return

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
                    {self.config_data["disclaimer"]}\n
                    You may now contact the requester to discuss this opportunity over DM. The requester is: <@{db_entry[1]}>\n
                    A copy of the request is included below:\n"{msg.embeds[0].description[:750]}"
                    '''
            )
            await payload.member.send(embed=embed)

    async def manage_deletion(self, payload):
        db_entry = self.bot.databasehandler.sqlquery(
            "SELECT * FROM Requests WHERE message_id=?",
            payload.message_id,
            return_type='one'
        )

        if db_entry:
            channel = self.bot.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)

            if db_entry[1] == payload.user_id:
                await msg.clear_reactions()
                self.bot.databasehandler.sqlquery(
                    "DELETE FROM Requests WHERE message_id=?;",
                    payload.message_id,
                    return_type='commit'
                )
            else:
                await msg.remove_reaction('❌', payload.member)


def setup(bot):
    bot.add_cog(Requests(bot))

import discord
from discord.ext import commands
import json
import bot_utils
import datetime
import asyncio
import re

class DM(commands.Cog):
    version = "v1.0"

    def __init__(self, bot):
        self.bot = bot

        self.open_conversations = {}

        # LOAD CONFIG DATA
        self.config_data = []
        with open('modules/DM/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, RawReactionActionEvent):
        if RawReactionActionEvent.user_id == self.bot.user.id:
            return

        if RawReactionActionEvent.message_id in self.open_conversations.keys():
            
            fetched_channel = self.bot.get_channel(RawReactionActionEvent.channel_id)
            fetched_message = await fetched_channel.fetch_message(RawReactionActionEvent.message_id)

            if str(RawReactionActionEvent.emoji) == '📩':

                target_user = self.bot.get_guild(RawReactionActionEvent.guild_id).get_member(self.open_conversations[RawReactionActionEvent.message_id])
                sending_user = self.bot.get_guild(RawReactionActionEvent.guild_id).get_member(RawReactionActionEvent.user_id)

                response = await bot_utils.request_text(self.bot, fetched_channel, sending_user, f"{sending_user.mention} please type your message to `{target_user}`:")

                if response:
                    await self._add_embed_field(fetched_message, name=f"Response (sent by {sending_user}) [{datetime.datetime.now().strftime('%m/%d %H:%M')}]", value=response)
                    await target_user.send(f"`Message from the mods:`\n{response}")

                await fetched_message.remove_reaction('📩', sending_user)

            elif str(RawReactionActionEvent.emoji) == '❌':

                await self._close_thread(self.open_conversations[RawReactionActionEvent.message_id])

        else:
            if RawReactionActionEvent.channel_id == self.config_data["bot_mail_channel"]:
                if str(RawReactionActionEvent.emoji) == '📩':
                    fetched_channel = self.bot.get_channel(RawReactionActionEvent.channel_id)
                    fetched_message = await fetched_channel.fetch_message(RawReactionActionEvent.message_id)
                    
                    embed = fetched_message.embeds[0]

                    x = re.findall('<@(!?)([0-9]*)>', str(embed.to_dict()))

                    member = fetched_channel.guild.get_member(int(x[0][1]))

                    if not member.id in self.open_conversations.values():
                        await self.create_thread(member)

                    sending_user = self.bot.get_guild(RawReactionActionEvent.guild_id).get_member(RawReactionActionEvent.user_id)
                    await fetched_message.remove_reaction('📩', sending_user)

    @commands.Cog.listener()
    async def on_message(self, message):
        if(message.guild == None) and (message.author != self.bot.user) and not (message.content.startswith("?")):

            if message.author.id in self.open_conversations.values():
                mail_channel = self.bot.get_channel(self.config_data["bot_mail_channel"])

                flipped_dict = {value:key for key, value in self.open_conversations.items()}
                thread_message = await mail_channel.fetch_message(flipped_dict[message.author.id])

                await self._add_embed_field(thread_message, f"Message [{datetime.datetime.now().strftime('%m/%d %H:%M')}]", f"> {message.content}")

            else:
                thread_message = await self.create_thread(message.author)
                await self._add_embed_field(thread_message, f"Message [{datetime.datetime.now().strftime('%m/%d %H:%M')}]", f"> {message.content[:950]}\nAttachments: {len(message.attachments)}")

            # RESPOND TO USER
            await message.author.send(self.config_data["bot_response"])

    async def _add_embed_field(self, message, name, value):
        fetched_message = await message.channel.fetch_message(message.id)
        
        embed = fetched_message.embeds[0]
        embed.add_field(name=name, value=value, inline=False)

        await fetched_message.edit(embed=embed)

    async def create_thread(self, member):
        embed = discord.Embed(title="Direct Message Thread", description=f"With: {member.mention} [{member}]", color=bot_utils.yellow)
        sent_message = await self.bot.get_channel(self.config_data["bot_mail_channel"]).send(embed=embed)

        self.open_conversations[sent_message.id] = member.id

        await sent_message.add_reaction('📩')
        await sent_message.add_reaction('❌')

        return sent_message

    async def _close_thread(self, user_id):
        mail_channel = self.bot.get_channel(self.config_data["bot_mail_channel"])

        thread_message = await mail_channel.fetch_message(self._get_message_id_from_user_id(user_id))

        embed = thread_message.embeds[0]
        embed.title = 'Direct Message Thread - CLOSED'

        await thread_message.edit(embed=embed)

        await thread_message.clear_reactions()

        del self.open_conversations[thread_message.id]

    def _get_message_id_from_user_id(self, user_id):
        flipped_dict = {value:key for key, value in self.open_conversations.items()}
        return flipped_dict[user_id]

    async def _dm_user(self, user, message):
        pass

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def dm(self, ctx, member: discord.Member, *, message):
        '''Use to send DMs through the bot.'''
        await ctx.message.delete()

        if not await bot_utils.await_confirm(ctx, f"**Send the following message to {member.mention}:**\n```\n{message}```", confirm_time=90):
            return

        thread_message = await self.create_thread(member)
        await self._add_embed_field(thread_message, f"Response (sent by {ctx.author}) [{datetime.datetime.now().strftime('%m/%d %H:%M')}]", message)

        await member.send(f"`Message from the mods:`\n{message}")

    @commands.command()
    @commands.has_any_role(*bot_utils.reg_roles)
    async def page(self, ctx, *, message=None):
        '''Used to alert the mods. Please use in a regs channel.'''

        if not message:
            message = "None"
            
        embed = discord.Embed(title=f"{ctx.author} is requesting assistance!", color=bot_utils.red)
        embed.add_field(name="Message", value=message, inline=False)
        await ctx.guild.get_channel(self.config_data["bot_mail_channel"]).send("@here", embed=embed)

def setup(bot):
    bot.add_cog(DM(bot))

import discord
from discord.ext import commands
import json
import bot_utils
import asyncio

channels_to_ignore = bot_utils.bot_channels + [730178093444104272]


class Template(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot
        self.message_history = [[None, None, None] for i in range(50)]

    @commands.Cog.listener()
    async def on_message(self, message):
        # if message.channel.id != 339978089411117076:
        #     return 

        if not await self.is_valid_message(message):
            return

        # await self.check_rapid_fire(message)
        await self.check_repeated_message(message)

        self.add_message_to_history(message)

    async def check_rapid_fire(self, message):
        rapid_fire_msg_lst = [
            i[0] == message.author.id
            for i in [
                k
                for k in self.message_history
                if message.channel.id == k[2]
            ]
        ]

        try:
            rapid_fire_msg = list(reversed(rapid_fire_msg_lst)).index(False) #rapid_fire_msg_lst.index(False)
        except ValueError:
            rapid_fire_msg = sum(rapid_fire_msg_lst)

        if rapid_fire_msg >= 7:
            await self.log_spam_event(message, "User Muted for 30s (Quick fire messages)")

            # role_obj = message.guild.get_role(340256097749303297)

            # await message.author.add_roles(role_obj)
            # await asyncio.sleep(10)
            # await message.author.remove_roles(role_obj)

    async def check_repeated_message(self, message):
        relevents_content_match = [
            i
            for i in self.message_history[-15:]
            if self.cleaned_content(message) == i[1]
        ]

        if len(relevents_content_match) == 3:
            # await message.channel.send("Please avoid spamming the channels with repeated messages.")
            await self.log_spam_event(message, "User Warned (repreated message)")
            
        elif len(relevents_content_match) >= 4:
            # await message.delete()
            await self.log_spam_event(message, "Message Removed (repeated messages)")

        elif len(relevents_content_match) >= 5:
            # await message.delete()
            # role_obj = message.guild.get_role(340256097749303297)
            # await message.author.add_roles(role_obj)
            await self.log_spam_event(message, "User Muted (repeated messages)")

    async def is_valid_message(self, message):
        if self.bot.user.id == message.author.id:
            return False

        if message.channel.id in channels_to_ignore:
            return False

        if len(message.attachments) > 0:
            return False

        if message.is_system():
            return False

        if message.content.startswith(self.bot.command_prefix):
            return False

        if len(message.content) <= 3:
            return False

        return True

    async def log_spam_event(self, message, action="None taken"):
        chan = message.guild.get_channel(339978089411117076)
        await chan.send(f"Spam Event:\nReason: {action}\n{message.jump_url}")

        # await bot_utils.log(
        #     self.bot,
        #     title="Potential Spam Event Detected",
        #     color=bot_utils.red,
        #     From=f"{message.author.mention} [{message.author}]",
        #     Channel=message.channel.mention,
        #     Message=message.content[:1000],
        #     Action=action,
        #     Link=f"[Jump Link]({message.jump_url})",
        # )

    def cleaned_content(self, message):
        return message.clean_content.lower().strip()

    def add_message_to_history(self, message):
        self.message_history.pop(0)

        self.message_history.append([
            message.author.id,
            self.cleaned_content(message),
            message.channel.id
        ])

def setup(bot):
    bot.add_cog(Template(bot))

import discord
from discord.ext import commands
import json
import difflib
import bot_utils

def diff(a, b ):
    sm = difflib.SequenceMatcher(None, a, b)
    
    output= []
    for opcode, a0, a1, b0, b1 in sm.get_opcodes():
        if opcode == 'equal':
            output.append(sm.a[a0:a1])
        elif opcode == 'insert':
            output.append("**" + sm.b[b0:b1] + "**")
        elif opcode == 'delete':
            pass
            # output.append("**" + sm.a[a0:a1] + "**")
        elif opcode == 'replace':
            output.append("**" + sm.b[b0:b1] + "**")
        else:
            raise RuntimeError
    return ''.join(output)

class MessageLog(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        target_channel = self.bot.databasehandler.sqlquery(
            '''SELECT * FROM MessageLog''',
            return_type='one'
        )

        try:
            self.target_channel = target_channel[0]
        except TypeError:
            self.bot.databasehandler.sqlquery(
                '''INSERT INTO MessageLog(channel_id) VALUES(NULL)''',
                return_type='commit'
            )


    def get_channel(self):
        return self.bot.databasehandler.sqlquery(
            '''SELECT * FROM MessageLog''',
            return_type='one'
        )[0]

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def message_log_channel_view(self, ctx):
        '''View the current message log channel ID'''
        await ctx.send(self.get_channel())

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def message_log_channel_update(self, ctx, channel_id):
        '''Changes the channel ID for message log.'''
        if await bot_utils.await_confirm(ctx, f"Confirm change of message log to channel: `{channel_id}`", delete_after=False, confirm_time=60):
            self.bot.databasehandler.sqlquery(
                'UPDATE MessageLog SET channel_id=?',
                channel_id,
                return_type='commit'
            )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author == self.bot.user or before.content == after.content:
            return

        result = diff(before.content, after.content)
        await bot_utils.log(
            self.bot,
            title='Message Edited',
            color=bot_utils.yellow,
            Channel=before.channel.mention,
            From=f"{before.author.mention} [{before.author}]",
            Before=f"> {before.content}",
            After=f"> {result}",
            channel=self.get_channel(),
            DM=False
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author == self.bot.user:
            return

        await bot_utils.log(
            self.bot,
            title='Message Deleted',
            color=bot_utils.red,
            Channel=message.channel.mention,
            From=f"{message.author.mention} [{message.author}]",
            Message=f"> {message.content[:1000]}",
            channel=self.get_channel(),
            DM=False
        )

def setup(bot):
    bot.add_cog(MessageLog(bot))
import discord
from discord.ext import commands
import json
import csv
import datetime

import bot_utils

DEBUG = False


class CommandsDB(commands.Cog):
    version = "v1.1"

    def __init__(self, bot):
        self.bot = bot
        self.config_data = []
        with open('modules/CommandsDB/config.json') as f:
            self.config_data = json.load(f)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        '''
        Handles custom commands!
        '''

        # IF NOT COMMAND NOT FOUND ERROR
        if not isinstance(error, commands.CommandNotFound):
            return

        # EXTRACT COMMAND
        input_command = ctx.message.content.split(" ")[0][1:]

        # COLLECT COMMAND FROM DATABASE
        command = self.bot.databasehandler.sqlquery(
            "SELECT * FROM Commands WHERE command=?",
            input_command,
            return_type='one'
        )

        # CHECK COMMAND IS FOUND AND OFFER CORRECTION IF NOT
        if command is None:
            if new_command := await self.did_you_mean(ctx, input_command):
                command = self.bot.databasehandler.sqlquery(
                    "SELECT * FROM Commands WHERE command=?",
                    new_command,
                    return_type='one'
                )
            else:
                return

        # HANDLE ALIASES
        if command[2] == 'alias':
            command = self.bot.databasehandler.sqlquery(
                "SELECT * FROM Commands WHERE command=?",
                command[1],
                return_type='one'
            )
            if command is None:
                await ctx.send("`ERROR: Invalid Alias`")
                return

        # SEND COMMAND
        await self.send_command(ctx, command[1], command=command)

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.reg_roles)
    async def hc(self, ctx, command=None, *, response=None):
        '''
        Used to create / delete help commands.

        Pass no arguments to view commands, pass a name to delete, and pass both to create a command.

        Prefix commands with `<>` to turn it into an embed supporitng markdown.
        Place an image link within the <> to embed the image.
        '''
        if command is None:
            await self.show_commands(ctx, 'help')

        elif response is None:
            await self.remove_command(ctx, 'help', command)

        else:
            await self.add_command(ctx, 'help', command, response)

    @commands.command()
    @commands.check(bot_utils.is_secret_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def cc(self, ctx, command=None, *, response=None):
        '''
        Used to create / delete custom commands.
        See ?hc help for more info.
        '''
        if command is None:
            await self.show_commands(ctx, 'fun')

        elif response is None:
            await self.remove_command(ctx, 'fun', command)

        else:
            await self.add_command(ctx, 'fun', command, response)

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.reg_roles)
    async def alias(self, ctx, alias=None, command=None):
        '''
        Used to manage command aliasing.
        '''

        if alias is None:  # SHOW COMMANDS
            # GET ALIAS
            result = self.bot.databasehandler.sqlquery(
                "SELECT * FROM Commands WHERE command_type='alias'",
                return_type='all'
            )

            # CREATE PAGINATOR
            paginator = commands.Paginator(prefix='```\n', suffix='\n```')
            paginator.add_line(f'--- ALIAS COMMANDS ({len(result)}) ---')

            # ADD COMMANDS TO PAGINATOR
            result.sort(key=lambda x: x[1])
            for command in result:
                paginator.add_line(f"{command[1]} <-- {command[0]}")

            # SEND PAGINATOR
            for page in paginator.pages:
                await ctx.send(page)

        elif command is None:  # DELETE ALIAS
            # CONFIRM
            if not await bot_utils.await_confirm(ctx, F"Delete {alias}?"):
                await ctx.send("Alias wasn't deleted.")
                return

            # DELETE COMMAND FROM DATABASE
            self.bot.databasehandler.sqlquery(
                "DELETE FROM Commands WHERE command=? AND command_type=?",
                alias, 'alias',
                return_type='commit'
            )

            await ctx.send(f"Alias: '{alias}' deleted!")

        else:  # ADD ALIAS
            self.bot.databasehandler.sqlquery(
                "INSERT INTO Commands(command, response, command_type) VALUES (?, ?, ?)",
                alias.strip('```'), command, 'alias',
                return_type='commit',
            )

            await ctx.send(f"New alias: '{alias}' --> '{command}'")

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    async def help_db(self, ctx):
        '''
        Shows all databse commands.
        '''
        await self.show_commands(ctx, 'help')

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def db_csv(self, ctx):
        '''
        Exports a CSV of the commands database.
        '''

        result = self.bot.databasehandler.sqlquery(
            "SELECT * FROM Commands",
            return_type='all'
        )

        with open('runtimefiles/Database-CSV.csv', 'w') as csvfile:
            ouput_writer = csv.writer(csvfile, delimiter=',', quotechar='"')

            ouput_writer.writerow(['command', 'response', 'command_type', 'owner', 'timestamp'])

            for command in result:
                ouput_writer.writerow(command)

            loaded_file = discord.File("runtimefiles/Database-CSV.csv", filename="Database-CSV.csv")
            await ctx.send("CSV File of the commands Database.", file=loaded_file)

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.reg_roles)
    async def get_command(self, ctx, command):
        '''
        Gets the plain text version of a command from the database.
        '''

        if any(role.id in bot_utils.admin_roles for role in ctx.message.author.roles):
            command = self.bot.databasehandler.sqlquery("SELECT * FROM Commands WHERE command=?", command, return_type='one')
        else:
            command = self.bot.databasehandler.sqlquery("SELECT * FROM Commands WHERE command=? AND command_type=?", command, "help", return_type='one')

        if command is None:
            await ctx.send("Sorry, didnt find that one!")
        else:
            await ctx.send(f"```\n{command[1]}\n```")

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def legacy_import(self, ctx):
        '''
        Imports legacy database data. Will overwrite all database entries.
        '''

        filename = 'runtimefiles/csv-import.csv'

        await ctx.message.attachments[0].save(filename)

        with open('runtimefiles/csv-import.csv', newline='\n') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            list_of_rows = list(csv_reader)

        i = 0
        for line in list_of_rows:
            # ADD COMMAND TO THE DATABASE
            self.bot.databasehandler.sqlquery(
                "INSERT INTO Commands(command, response, command_type) VALUES (?, ?, ?)",
                line[1], line[2], line[0],
                return_type='commit'
            )
            i += 1

        await ctx.send(f"Added {i} commands to the databse!")

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def commands_by(self, ctx, member: discord.Member):
        '''Shows commands by a certain user.'''

        # GET DATABASE COMMANDS
        result = sorted(self.get_user_commands(member))

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- DATABASE COMMANDS BY {member} ({len(result)}) ---')

        # ADD COMMANDS TO PAGINATOR
        for command in result:
            paginator.add_line(command[0])

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page)

    @commands_by.error
    async def commands_by_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="You need to provide a users name.",
                description="Use the command like this:\n`?commands_by [User Name]`\n\nExample\n`?commands_by Ed`\n\nYou can find users with either their ID, name or mention."
            )
            await ctx.send(embed=embed)
            ctx.handled_in_local = True

        if isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(
                title="Member Not Found",
                description="Sorry, I didnt find that user.\nYou can find users with either their ID, name or mention. if their name includes a space you will have to use either the mention or ID."
            )
            await ctx.send(embed=embed)
            ctx.handled_in_local = True

    # -- HELPER FUNCTIONS --

    def embed_type(self, input_string):
        if not input_string.startswith('<'):
            return 'PLAIN'

        closing_index = input_string.index('>')

        if closing_index == 1:
            return 'EMBED'
        else:
            return input_string[1:closing_index]

    def get_user_commands(self, member):
        return self.bot.databasehandler.sqlquery(
            "SELECT * FROM Commands WHERE owner=?",
            member.id,
            return_type='all'
        )

    async def send_command(self, ctx, response, command="?", delete=True):
        # HANDLE TARGET (FOR REPLIES)
        try:
            reply_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            target = reply_message.reply
        except AttributeError:
            target = ctx.send

        # DIFFERENT COMMAND TYPES
        command_type = self.embed_type(response)

        if command_type == 'PLAIN':
            await target(bot_utils.sanitize_input(response))
            delete = False

        elif command_type == 'EMBED':
            embed = discord.Embed(description=bot_utils.sanitize_input(response)[2:])
            embed.set_footer(text=f"?{command[0]} requested by: {ctx.author}")
            await target(embed=embed)

        else:  # IMAGE EMBED
            response = response.replace(f'<{command_type}>', '')

            embed = discord.Embed(description=bot_utils.sanitize_input(response))
            embed.set_footer(text=f"?{command[0]} requested by: {ctx.author}")
            embed.set_image(url=command_type)

            await target(embed=embed)

        # HANDLE DELETIONS
        if delete:
            await ctx.message.delete()

    async def add_command(self, ctx, command_type, command, response):
        """
        Adds a command to the database.
        """

        await self.send_command(ctx, response, command="?PREVIEW", delete=False)

        if not await bot_utils.await_confirm(ctx, F"Create `?{command}`?\nPlease ensure that the command is inline with the command creation guidlines. View guidlines with `?command_creation`", confirm_time=60):
            await ctx.send("Command wasn't created.")
            return

        if self.config_data['require_approval'] == "True":
            approval_message = await ctx.send("Thanks for your new command. It has been submitted for approval and should be live soon!")
            if not await bot_utils.await_mod_confirm(ctx, f"**A command creation requires approval:**\nCommand: `?{command}`\nLink: {ctx.message.jump_url}", delete_after=False, confirm_time=21000):
                await approval_message.edit(content=f"{ctx.author.mention} The command was not approved.")
                return
            else:
                await approval_message.delete()

        # ADD COMMAND TO THE DATABASE
        self.bot.databasehandler.sqlquery(
            "DELETE FROM Commands WHERE command=? AND command_type=?",
            command, command_type,
            return_type='commit'
        )

        self.bot.databasehandler.sqlquery(
            "INSERT INTO Commands(command, response, command_type, owner, timestamp) VALUES (?, ?, ?, ?, ?)",
            command.strip('```'), response, command_type, ctx.author.id, datetime.datetime.utcnow(),
            return_type='commit'
        )

        await ctx.send(f"{ctx.author.mention} New {command_type} command: '{command}'")

    async def remove_command(self, ctx, command_type, command):
        '''
        Removes a command from the database
        '''

        # WAIT FOR CONFIRM
        if not await bot_utils.await_confirm(ctx, F"Delete {command}?"):
            await ctx.send("Command wasn't deleted.")
            return

        # DELETE COMMAND FROM DATABASE
        self.bot.databasehandler.sqlquery(
            "DELETE FROM Commands WHERE command=? AND command_type=?",
            command, command_type,
            return_type='commit'
        )

        # DELETE ALIASES
        self.bot.databasehandler.sqlquery(
            "DELETE FROM Commands WHERE response=? AND command_type=?",
            command, 'alias',
            return_type='commit'
        )

        await ctx.send(f"Command: '{command}' deleted!")

    async def show_commands(self, ctx, command_type):
        """
        Shows all databse commands
        """

        # GET DATABASE COMMANDS
        result = sorted(self.bot.databasehandler.sqlquery(
            "SELECT * FROM Commands WHERE command_type=?",
            command_type,
            return_type='all'
        ))

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- DATABASE COMMANDS (Aliases) ({len(result)}) ---')

        # ADD COMMANDS TO PAGINATOR
        for command in result:
            aliases = self.bot.databasehandler.sqlquery(
                "SELECT * FROM Commands WHERE command_type=? AND response=?",
                "alias", command[0],
                return_type='all'
            )
            alias_string = ", ".join([i[0] for i in aliases])
            paginator.add_line(f"{command[0]} ({alias_string})")

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page)

    async def did_you_mean(self, ctx, input_str):
        # GET ALL COMMANDS
        commands = self.bot.databasehandler.sqlquery(
            "SELECT * FROM Commands WHERE command_type='help'",
            return_type='all'
        )

        # FIND POSSIBLE MATCHES
        possible_command = bot_utils.close_match(input_str, [i[0] for i in commands])

        if not possible_command:
            return False

        if await bot_utils.await_confirm(ctx, f"Did you mean:\n```\n{self.bot.config['prefix']}{possible_command}\n```"):
            return possible_command
        else:
            return None


def setup(bot):
    bot.add_cog(CommandsDB(bot))

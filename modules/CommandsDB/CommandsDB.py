import discord
from discord.ext import commands
import json
import sqlite3
import math
import sys
import traceback
import difflib 
import time
import asyncio
import csv
import datetime

import bot_utils

DEBUG = False

class CommandsDB(commands.Cog):
    version = "v1.0"

    def __init__(self, bot):
        self.bot = bot

        # LOAD CONFIG DATA
        #self.config_data = []
        #with open('modules/CommandsDB/config.json') as f:
        #    self.config_data = json.load(f)

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    # --- COMMANDS ---  

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if DEBUG: print("on_command_error")
        
        # IF NOT COMMAND NOT FOUND ERROR
        if not isinstance(error, commands.CommandNotFound):
            return

        # EXTRACT COMMAND
        input_args = ctx.message.content.split(" ")
        input_command = input_args[0][1:]
        if DEBUG: print("Command = ", input_command)

        # COLLECT COMMAND FROM DATABASE
        self.c.execute("SELECT * FROM Commands WHERE command=?", (input_command,))
        command = self.c.fetchone()
        self.c.close()
        self.c = self.conn.cursor()
        if DEBUG: print("Found = ", command)

        # CHECK COMMAND IS FOUND AND OFFER CORRECTION IF NOT
        if command == None:
            if DEBUG: print("Command Not Found")
            new_command = await self.did_you_mean(ctx, input_command)

            if new_command:
                # COLLECT COMMAND FROM DATABASE
                self.c.execute("SELECT * FROM Commands WHERE command=?", (new_command,))
                command = self.c.fetchone()
                self.c.close()
                self.c = self.conn.cursor()
            else:
                return

        # HANDLE ALIASES
        if command[2] == 'alias':
            if DEBUG: print("Triggereing Alias")
            # COLLECT COMMAND FROM DATABASE
            self.c.execute("SELECT * FROM Commands WHERE command=?", (command[1],))
            command = self.c.fetchone()
            self.c.close()
            self.c = self.conn.cursor()
            if DEBUG: print("replacement command = ", command)

            if command == None:
                await ctx.send("ERROR: Invalid Alias")
                return
                   
        # GET RESPONSE
        response = command[1]
        if DEBUG: print("Response = ", response)

        await self.send_command(ctx, response)

        if DEBUG: print("Done!")

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.reg_roles)
    async def hc(self, ctx, command=None, *, response=None):
        '''
        Used to create / delete help commands.

        Pass no arguments to view commands, pass a name to delete, and pass a name + response to crata command.

        Prefix commands with `<>` to turn it into an embed supporitng markdown.
        '''

        if command == None:
            await self.show_commands(ctx, 'help')
            return

        if response == None:
            await self.remove_command(ctx, 'help', command)
            return

        await self.add_command(ctx, 'help', command, response)
    
    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def cc(self, ctx, command=None, *, response=None):
        '''
        Used to create / delete custom commands. 
        
        Pass no arguments to view commands, pass a name to delete, and pass a name + response to crata command.

        Prefix commands with `<>` to turn it into an embed supporitng markdown.
        '''

        if command == None:
            await self.show_commands(ctx, 'fun')
            return

        if response == None:
            await self.remove_command(ctx, 'fun', command)
            return

        await self.add_command(ctx, 'fun', command, response)

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.reg_roles)
    async def alias(self, ctx, alias=None, command=None):
        '''
        Used to manage command aliasing.
        '''

        if alias == None: # SHOW COMMANDS
            
            # GET ALIAS
            self.c.execute("SELECT * FROM Commands WHERE command_type='alias'")
            result = self.c.fetchall()
            
            result.sort(key=lambda x: x[0])

            # CREATE PAGINATOR
            paginator = commands.Paginator(prefix='```\n', suffix='\n```')
            paginator.add_line(f'--- ALIAS COMMANDS ({len(result)}) ---')

            # ADD COMMANDS TO PAGINATOR
            for command in result:
                paginator.add_line(f"{command[1]} <-- {command[0]}")

            # SEND PAGINATOR
            for page in paginator.pages:
                await ctx.send(page, delete_after=60)

        elif command == None: # DELETE ALIAS

            # CONFIRM
            if not await bot_utils.await_confirm(ctx, F"Delete {alias}?"):
                await ctx.send("Alias wasn't deleted.")
                return

            try:
                # DELETE COMMAND FROM DATABASE
                self.c.execute("DELETE FROM Commands WHERE command=? AND command_type=?", (alias, 'alias'))
                self.conn.commit()
                await ctx.send(f"Alias: '{alias}' deleted!")

            except:
                # REPORT ERROR
                await ctx.send(f"Failed to delete '{alias}' from database!")

        else: # ADD ALIAS
            try:
                # ADD COMMAND TO THE DATABASE
                self.c.execute("INSERT INTO Commands(command, response, command_type) VALUES (?, ?, ?)", (alias.strip('```'), command, 'alias'))
                self.conn.commit()
                await ctx.send(f"New alias: '{alias}' --> '{command}'")

            except:
                # REPORT ERROR
                await ctx.send(f"Failed to add '{command}' to databse!")

    @commands.command()
    async def help_db(self, ctx):
        '''
        Shows all databse commands.
        '''

        await self.show_commands(ctx, 'help')

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def db_csv(self,ctx):
        '''
        Exports a CSV of the commands database.
        '''

        self.c.execute("SELECT * FROM Commands")
        result = self.c.fetchall()

        with open('runtimefiles/Database-CSV.csv', 'w') as csvfile:
            ouput_writer = csv.writer(csvfile, delimiter=',', quotechar='"')

            ouput_writer.writerow(['command', 'response', 'command_type'])

            for command in result:
                ouput_writer.writerow(command)

            loaded_file = discord.File("runtimefiles/Database-CSV.csv", filename="Database-CSV.csv")
            await ctx.send("CSV File of the commands Database.", file=loaded_file)

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def legacy_import(self, ctx):
        '''
        Imports legacy database data.
        '''

        filename = 'runtimefiles/csv-import.csv'

        await ctx.message.attachments[0].save(filename)

        with open('runtimefiles/csv-import.csv', newline='\n') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            list_of_rows = list(csv_reader)

        i = 0

        for line in list_of_rows:
            try:
                # ADD COMMAND TO THE DATABASE
                self.c.execute("INSERT INTO Commands(command, response, command_type) VALUES (?, ?, ?)", (line[1], line[2], line[0]))
                self.conn.commit()
                i = i + 1

            except:
                # REPORT ERROR
                await ctx.send(f"Failed to add '{line[1]}' to databse!")

        await ctx.send(f"Added {i} commands to the databse!")

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.admin_roles)
    async def commands_by(self, ctx, member: discord.Member):
        '''Shows commands by a certain user.'''

        # GET DATABASE COMMANDS
        self.c.execute("SELECT * FROM Commands WHERE owner=?", (member.id, ))
        result = sorted(self.c.fetchall())

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- DATABASE COMMANDS BY {member} ({len(result)}) ---')

        # ADD COMMANDS TO PAGINATOR
        for command in result:
            paginator.add_line(command[0])

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page)

    # -- HELPER FUNCTIONS --

    def get_user_commands(self, member):
        self.c.execute("SELECT * FROM Commands WHERE owner=?", (member.id, ))
        result = self.c.fetchall()
        return result

    async def send_command(self, ctx, response, delete=True):
        if response.startswith("<>"):
            embed=discord.Embed(description=bot_utils.sanitize_input(response[2:]))
            embed.set_footer(text=f"Sent by: {ctx.author}")
            await ctx.send(embed=embed)
            if delete:
                await ctx.message.delete()
        else:
            await ctx.send(bot_utils.sanitize_input(response))

    async def add_command(self, ctx, command_type, command, response):
        """
        Adds a command to the database.
        """

        if not await bot_utils.await_confirm(ctx, F"Create `?{command}`?\nPlease ensure that the command is inline with the command creation guidlines. View guidlines with `?command_creation`"):
            await ctx.send("Command wasn't created.")
            return

        approval_message = await ctx.send("Thanks for your new command. It has been submitted for approval and should be live soon!")
        if not await bot_utils.await_mod_confirm(ctx, f"**A command creation requires approval:**\nCommand: `?{command}`\nLink: {ctx.message.jump_url}", delete_after=False, confirm_time=21000):
            await approval_message.edit(content=f"{ctx.author.mention} The command was not approved.")
            return
        else:
            await approval_message.delete()

        try:
            # ADD COMMAND TO THE DATABASE
            self.c.execute("DELETE FROM Commands WHERE command=? AND command_type=?", (command, command_type))
            self.c.execute("INSERT INTO Commands(command, response, command_type, owner, timestamp) VALUES (?, ?, ?, ?, ?)", (command.strip('```'), response, command_type, ctx.author.id, datetime.datetime.utcnow()))
            self.conn.commit()
            await ctx.send(f"{ctx.author.mention} New {command_type} command: '{command}'")
            await self.send_command(ctx, response, delete=False)

        except:
            # REPORT ERROR
            await ctx.send(f"Failed to add '{command}' to databse!")

    async def remove_command(self, ctx, command_type, command):
        '''
        Removes a command from the database
        '''

        if not await bot_utils.await_confirm(ctx, F"Delete {command}?"):
            await ctx.send("Command wasn't deleted.")
            return

        try:
            # DELETE COMMAND FROM DATABASE
            self.c.execute("DELETE FROM Commands WHERE command=? AND command_type=?", (command, command_type))
            self.c.execute("DELETE FROM Commands WHERE response=? AND command_type=?", (command, 'alias'))
            self.conn.commit()
            await ctx.send(f"Command: '{command}' deleted!")

        except:
            # REPORT ERROR
            await ctx.send(f"Failed to delete '{command}' from database!")

    async def show_commands(self, ctx, command_type):
        """
        Shows all databse commands
        """

        # GET DATABASE COMMANDS
        self.c.execute("SELECT * FROM Commands WHERE command_type=?", (command_type, ))
        result = sorted(self.c.fetchall())

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- DATABASE COMMANDS ({len(result)}) ---')

        # ADD COMMANDS TO PAGINATOR
        for command in result:
            paginator.add_line(command[0])

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page)

    async def did_you_mean(self, ctx, input_str):

        # GET ALL COMMANDS
        self.c.execute("SELECT * FROM Commands")
        commands = self.c.fetchall()

        # FIND POSSIBLE MATCHES
        # possible_commands = difflib.get_close_matches(input_str, [i[0] for i in commands])
        possible_command = bot_utils.close_match(input_str, [i[0] for i in commands])

        if not possible_command:
            return False

        if await bot_utils.await_confirm(ctx, f"Did you mean:\n```\n{self.bot.config['prefix']}{possible_command}\n```"):
            return possible_command
        else:
            return None

    async def string_substitute(self, string, **kwargs):
        for k, v in kwargs.items():
            string.replace(f"<{k}>", v)
        return string

def setup(bot):
    bot.add_cog(CommandsDB(bot))
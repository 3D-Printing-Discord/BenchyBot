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
        
        # IF NOT COMMAND NOT FOUND ERROR
        if not isinstance(error, commands.CommandNotFound):
            return

        # EXTRACT ARGS
        input_args = ctx.message.content.split(" ")
        input_command = input_args[0][1:]

        # COLLECT COMMAND FROM DATABASE
        self.c.execute("SELECT * FROM Commands WHERE command=?", (input_command,))

        # GET THE FIRST ONE RESULT
        command = self.c.fetchone()

        # CHECK COMMAND IS FOUND AND OFFER CORRECTION IF NOT
        if command == None:
            new_command = await self.did_you_mean(ctx, input_command)

            if new_command:
                # COLLECT COMMAND FROM DATABASE
                self.c.execute("SELECT * FROM Commands WHERE command=?", (new_command,))

                # GET THE FIRST ONE RESULT AND CORRECT THE COMMAND
                command = self.c.fetchone()
            else:
                return

        # HANDLE ALIASES
        if command[2] == 'alias':
            # COLLECT COMMAND FROM DATABASE
            self.c.execute("SELECT * FROM Commands WHERE command=?", (command[1],))

            # GET THE FIRST ONE RESULT AND CORRECT THE COMMAND
            command = self.c.fetchone()

            if command == None:
                await ctx.send("ERROR: Invalid Alias")
                   
        # GET RESPONSE
        response = command[1]

        flags, trimmed_response = bot_utils.simple_parse(response, embed='e', colour='c')

        if flags['embed']:
            if flags['colour'] == None:
                flags['colour'] = bot_utils.green
            else:
                try:
                    flags['colour'] = int(flags['colour'], 16)
                except ValueError:
                    flags['colour'] = bot_utils.green

            embed = discord.Embed(title=flags['embed'], description=trimmed_response, color=flags['colour'])
            await ctx.send(embed=embed)
        else:
            await ctx.send(bot_utils.sanitize_input(response))
            ctx.handled_in_local = True

    @commands.command()
    @commands.check(bot_utils.is_bot_channel)
    @commands.has_any_role(*bot_utils.reg_roles)
    async def hc(self, ctx, command=None, *, response=None):
        '''
        Used to create / delete help commands.
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

    # -- HELPER FUNCTIONS --

    async def add_command(self, ctx, command_type, command, response):
        """
        Adds a command to the database.
        """

        try:
            # ADD COMMAND TO THE DATABASE
            self.c.execute("DELETE FROM Commands WHERE command=? AND command_type=?", (command, command_type))
            self.c.execute("INSERT INTO Commands(command, response, command_type, owner, timestamp) VALUES (?, ?, ?, ?, ?)", (command.strip('```'), response, command_type, ctx.author.id, datetime.datetime.utcnow()))
            self.conn.commit()
            await ctx.send(f"New {command_type} command: '{command}'':\n{response}")

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
        result = self.c.fetchall()

        # CREATE PAGINATOR
        paginator = commands.Paginator(prefix='```\n', suffix='\n```')
        paginator.add_line(f'--- DATABASE COMMANDS ({len(result)}) ---')

        # ADD COMMANDS TO PAGINATOR
        for command in result:
            paginator.add_line(command[0])

        # SEND PAGINATOR
        for page in paginator.pages:
            await ctx.send(page, delete_after=60)

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
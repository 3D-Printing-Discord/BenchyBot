
import discord
from discord.ext import commands
import json
import os
import difflib 
import bot_utils
import zipfile
import requests
import shutil
import sqlite3


class GCode(commands.Cog):
    version = "v0.1"

    def __init__(self, bot):
        self.bot = bot

        self.config_data = []
        with open('modules/GCode/config.json') as f:
            self.config_data = json.load(f)

        self.conn = sqlite3.connect(self.bot.config['database'])
        self.c = self.conn.cursor()

    @commands.command()
    @commands.has_any_role(*bot_utils.admin_roles)
    async def _update_marlin_database(self, ctx):
        '''Refreshes the internal marlin database.'''

        async with ctx.typing():

            # CONFIRM
            if not await bot_utils.await_confirm(ctx, f"Confirm refresh of database. (This may take several seconds)", delete_after=False):
                return

            # DELETE EXISTING
            self.c.execute("DELETE FROM GCode WHERE flavour='marlin'")
            self.conn.commit()

            # DOWNLOAD MARLIN DOCS
            r = requests.get("https://github.com/MarlinFirmware/MarlinDocumentation/archive/master.zip", allow_redirects=True)
            open('runtimefiles/marlin_docs.zip', 'wb').write(r.content)

            # UNZIP
            with zipfile.ZipFile("runtimefiles/marlin_docs.zip", 'r') as zip_ref:
                # CREATE DIRECTORY
                try:
                    os.mkdir('runtimefiles/marlin_docs_extracted')
                except FileExistsError:
                    shutil.rmtree('runtimefiles/marlin_docs_extracted')
                    os.mkdir('runtimefiles/marlin_docs_extracted')
                
                zip_ref.extractall(path="runtimefiles/marlin_docs_extracted")

            # GET ALL GCODES
            files = os.listdir('runtimefiles/marlin_docs_extracted/MarlinDocumentation-master/_gcode')

            # BUILD DATABASE
            for f in files:

                temp_file_ob = open(f"runtimefiles/marlin_docs_extracted/MarlinDocumentation-master/_gcode/{f}", "r")
                temp_file = temp_file_ob.readlines()
                temp_file_ob.close()

                title = temp_file[2][7:]

                self.c.execute("INSERT INTO GCode(flavour, command, name) VALUES (?, ?, ?)", ('marlin', os.path.splitext(f)[0].strip(), title.strip()))
                self.conn.commit()

        await ctx.send("Done!")

    @commands.command()
    async def mg(self, ctx, *, request):
        '''Used to search Marlin Gcode Commands.'''

        request = request.lower()

        # COLLECT GCODES FROM DATABASE
        self.c.execute("SELECT * FROM GCode WHERE flavour='marlin'")
        results = self.c.fetchall()

        if request == 'list':
            results.sort(key=lambda x: x[1])

            # CREATE PAGINATOR
            paginator = commands.Paginator(prefix='```\n', suffix='\n```')
            paginator.add_line(f'--- MARLIN GCODE COMMANDS ({len(results)}) ---')

            # ADD COMMANDS TO PAGINATOR
            for command in results:
                paginator.add_line(f"{command[1]} - {command[2]}")

            # SEND PAGINATOR
            for page in paginator.pages:
                await ctx.send(page, delete_after=60)

            return

        name = bot_utils.close_match(request, [i[1] for i in results])

        if not name:
            name = bot_utils.close_match(request, [i[2] for i in results])

        if not name:
            await ctx.send("Im sorry, I dont know that one!")
            return

        # print(name)

        self.c.execute("SELECT * FROM GCode WHERE flavour='marlin' AND command=?", (name, ))
        result = self.c.fetchone()
        self.c.close()
        self.c = self.conn.cursor()

        # print(result)

        lookup = result[1]

        await ctx.send(f"https://marlinfw.org/docs/gcode/{lookup}.html")

def setup(bot):
    bot.add_cog(GCode(bot))
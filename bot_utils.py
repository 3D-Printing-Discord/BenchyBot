import discord
from datetime import datetime
import asyncio
import difflib
import shlex
import sqlite3

# ---------- STANDARDISED COLOURS ----------
blue = 0x89cff0
red = 0xcc0000
yellow = 0xffcc00
green = 0x66cc00
purple = 0x330099

# ---------- DATA ----------
admin_roles = [167872530860867586, 167872106644635648]
reg_roles = [260945795744792578] + admin_roles
bot_channels = [700421839872327741, 339978089411117076, 471446895089156108, 667463307963138058]
secret_channels = [339978089411117076]

# ---------- CHECKS ----------
async def is_admin(ctx):
    """
    Checks if user is an admin.
    """
    for role in admin_roles:
        test_role = discord.utils.get(ctx.guild.roles, id=role)
        if test_role in ctx.author.roles:
            return True
    return False

async def is_mod(ctx):
    """
    Checks if user is a mod. This function is depreciated and will be removed in a future version. Consider switching to is_admin.
    """
    print(f"{ctx.command} is using a legacy check that will become depreciated soon!!!")

    for role in admin_roles:
        test_role = discord.utils.get(ctx.guild.roles, id=role)
        if test_role in ctx.author.roles:
            return True
    return False

async def is_reg(ctx):
    """
    Checks if user is a reg. This function is depreciated and will be removed in a future version. Consider switching to is_admin.
    """
    for role in reg_roles:
        test_role = discord.utils.get(ctx.guild.roles, id=role)
        if test_role in ctx.author.roles:
            return True
    return False

async def is_bot_channel(ctx):
    """
    Checks if command is in a bot channel.
    """
    for channel in bot_channels:
        if channel == ctx.channel.id:
            return True
    return False

async def is_secret_channel(ctx):
    """
    Checks if command is a secret channel.
    """
    if ctx.channel.id in secret_channels:
        return True
    else:
        return False


# ---------- CHECKS ----------
def has_any_role(member, roles):
    return any([i in member.roles for i in roles])

async def bot_log(bot, log):
    """
    Logs bot activity
    """
    print("A depreciated log command is being used!")

    if bot.config['log_level'] in ("FULL", "CMD"):
        print(f"[!] {datetime.today()}: {log}")
    
    if bot.config['log_level'] == "FULL":
        channel = bot.get_channel(695039236117889054)
        await channel.send(f"{log}")

async def log(bot, title="Log", author=None, description=None, color=blue, **kwargs):
    embed=discord.Embed(title=title, description=description, color=color)

    for k, v in kwargs.items():
        embed.add_field(name=k, value=v, inline=False)

    log_message = await bot.get_channel(bot.config['bot_log_channel']).send(embed=embed)

    await log_message.add_reaction('📩')

async def await_mod_confirm(ctx, message, delete_after=True, confirm_time=10):
    '''
    Sends a message and waits for confirmation. 
    '''

    target_channel = ctx.bot.get_channel(ctx.bot.config['bot_log_channel'])

    # SEND THE SUGGESTIONS
    sent_message = await target_channel.send(message)

    # ADD THE CONFIRM EMOJI
    await sent_message.add_reaction('👍')
    await sent_message.add_reaction('👎')

    # DEF CHECK OF RESPONSE
    def check(reaction, user):
        return reaction.message.id == sent_message.id and user.id != ctx.bot.user.id

    # AWAIT AND HANDLE RESPONSE
    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=confirm_time, check=check)
        if delete_after:
            await sent_message.delete()
        else:
            await sent_message.edit(content=f"{message}\n`CONFIRMED`")
            await sent_message.clear_reactions()

        if str(reaction.emoji) == '👍':
            return True
        else:
            await sent_message.edit(content=f"{message}\n`REJECTED`")
            await sent_message.clear_reactions()
            return False

    except asyncio.TimeoutError:
        # CLEAN UP
        if delete_after:
            await sent_message.delete()
        else:
            await sent_message.edit(content=f"{message}\n`CANCELLED`")
            await sent_message.clear_reactions()
        return False

async def await_confirm(ctx, message, delete_after=True, confirm_time=10):
    '''
    Sends a message and waits for confirmation. 
    '''

    # SEND THE SUGGESTIONS
    sent_message = await ctx.send(message)

    # ADD THE CONFIRM EMOJI
    await sent_message.add_reaction('👍')

    # DEF CHECK OF RESPONSE
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) == '👍' and sent_message.id == reaction.message.id

    # AWAIT AND HANDLE RESPONSE
    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=confirm_time, check=check)
        if delete_after:
            await sent_message.delete()
        else:
            await sent_message.edit(content=f"{message}\n`CONFIRMED`")
            await sent_message.clear_reactions()
        return True

    except asyncio.TimeoutError:
        # CLEAN UP
        if delete_after:
            await sent_message.delete()
        else:
            await sent_message.edit(content=f"{message}\n`CANCELLED`")
            await sent_message.clear_reactions()
        return False

async def request_text(bot, channel, member, message, timeout=60):

        request_message = await channel.send(message)
        await request_message.add_reaction('❌')

        def message_check(m):
            return m.author == member and m.channel == channel

        def reaction_check(reaction, user):
            return str(reaction.emoji) == '❌' and user != bot.user and request_message.id == reaction.message.id 
            
        done, pending = await asyncio.wait([
                        bot.wait_for('message', check=message_check, timeout=timeout),
                        bot.wait_for('reaction_add', check=reaction_check, timeout=timeout)
                    ], return_when=asyncio.FIRST_COMPLETED)

        try:
            return_object = done.pop().result()
        except:
            exception = done.pop().exception()
            return_object = False

        for future in pending:
            future.cancel()

        await request_message.delete()

        if type(return_object) == discord.message.Message:
            await return_object.delete()
            return return_object.content
        else:
            return False

async def await_react_confirm(confirm_message, bot, emoji='✅', confirm_time=60, delete_after=True, requires_poster=False):
    '''
    Reacts to a message and awaits a user to agree.
    '''

    # ADD THE CONFIRM EMOJI
    try:
        await confirm_message.add_reaction(emoji)
    except:
        return False, None

    # DEF CHECK FOR RESPONSE
    def check(reaction, user):
        if requires_poster:
            return str(reaction.emoji) == emoji and user != bot.user and confirm_message.id == reaction.message.id and user.id == confirm_message.author.id
        else:
            return str(reaction.emoji) == emoji and user != bot.user and confirm_message.id == reaction.message.id

    # AWAIT AND HANDLE RESPONSE
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=confirm_time, check=check)
        if delete_after: await confirm_message.clear_reactions()
        return True, user
    except Exception:
        if delete_after: await confirm_message.clear_reactions()
        return False, None

def close_match(search, possible_matches):
    '''
    Finds close string matches using difflib.get_close_matches
    '''

    possible_matches_lower = [i.lower() for i in possible_matches]

    search_lower = search.lower()

    try:
        solution = difflib.get_close_matches(search_lower, possible_matches_lower)

        index = possible_matches_lower.index(solution[0])

        upper_result = possible_matches[index]

        return upper_result
    
    except IndexError:
        return None

def sanitize_input(input_string):
    '''
    Removes tags commands etc from inputs. 
    '''
    output_str = input_string.replace('@&', '@&/')
    output_str = output_str.replace("@here", "@/here")
    output_str = output_str.replace("@everyone", "@/everyone")
    return(output_str)

def simple_parse(input_string, **kwargs):
    '''
    Parses arguments from a string.
    '''

    args = {}

    # split_string = shlex.split(input_string)
    split_string = input_string.split(" ")

    for k, v in kwargs.items():

        try:
            arg_index = split_string.index(f"-{v}")
            string_value = split_string[arg_index+1] 

            args[k] = string_value
            split_string.remove(f"-{v}")
            split_string.remove(string_value)

        except ValueError:
            args[k] = None
            continue
    
    trimmed_string = " ".join(split_string)
    return args, trimmed_string

def convert_to_number(input_var):
    try:
        output = float(input_var)
        return output
    except:
        return None
import os, discord, asyncio, random

from matchup import matchup, teamsel
from lists import na_characters, rules, shufflerules, Teams, dirt, tascii
from db import DBConnect
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN=os.getenv("BOT_TOKEN")

bot = commands.Bot(command_prefix="++")

###########TEAMS###########

chs = []
for i in Teams:
    for x in i:
        if x not in chs:
            chs.append(x)
        else:
            pass
chslc = [x.lower() for x in chs]
ongoing = 0
ttype = 0

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("I'm Mr. Wolf. I solve problems."))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        embed = discord.Embed(title=":exclamation: Missing permissions", description="You cannot use this command", color=15844367)
        await ctx.send(embed=embed)

##Instructions command

@bot.command(name="instructions", help="Shows guideline for using the bot")
async def instr(ctx):
    embed = discord.Embed(title="Usage Guidelines", description='''**I'm Mr. Wolf. I solve problems. If self preservation is an instinct you posess, you will read the rules and apply them accordingly.**\n\n\n- Use **++bc** *char1* *char2* *char n* to filter out banned characters and generate a team list\n\n- Use space between every character name, no commas\n\n- Character names are NOT case sensitive\n\n- If a character name contains a space, use quotation makrs (e.g. ++bc "et zabuza" "sakura (s)"\n\n- Use **++teamwith** to generate a team that contains one or two characters (e.g. **++teamwith** *yk* *"et zabuza"*\n\n- Use **++chars** to view a list of all characters''', color=10038562)
    await ctx.send(embed=embed)


##Characters command

@bot.command(name="chars", help="Prints list of char names")
async def chr(ctx):
    embed = discord.Embed(title="Character list", description="\n".join(chs), color=10038562)
    await ctx.send(embed=embed)


##BC command

@bot.command(name="bc", help="Generates long war meta list according to specified bc")
async def bc(ctx, *args):
    argsl = [x.lower() for x in args]
    if not args:
        await ctx.send('No BC Specified')
    else:
        false = []
        tms = []
        for i in args:
            if not i.lower() in chslc:
                false.append(i.lower())
            else:
                pass
        if false:
            await ctx.send('**WARNING**: Following character name(s) is either misspelled or there are no teams including it: {}. Make sure you follow formatting instructions (**++instructions**). Use **++chars** to see exact name of each character\n\nPrinting teams without filtering out {} in 10 seconds'.format(false, false))
            await asyncio.sleep(10)
        else:
            pass
        setb = set(argsl)
        for x in dirt:
            lc = [n.lower() for n in x]
            set1 = set(lc)
            if set1.intersection(setb):
                pass
            else:
                tms.append(', '.join(x))
        dump = '\n'.join(tms)
        bc = ', '.join(x.capitalize() for x in args)
        await ctx.send('```css\nBanned Characters: {}\n```\n```json\n"Available Teams"\n\n{}\n```'.format(bc, dump))
    

#teamwith command

@bot.command(name="teamwith", help="Generates Team with Specified Character(s)")
async def t_with(ctx, *char):
    false = []
    for i in char:
        if not i.lower() in chslc:
            false.append(i.lower())
        else:
            pass
    if not false:
        if len(char) == 1:
            tms = []
            for x in Teams:
                lc = [n.lower() for n in x]
                if char[0].lower() in lc:
                    tms.append(', '.join(x))
                else:
                    pass    
            dump = '\n'.join(tms)
            await ctx.send('```json\n"Teams with {}"\n\n\n{}\n```'.format(char[0].capitalize(), dump))       
        elif len(char) == 2:
            duo = [char[0].lower(), char[1].lower()]
            tms = []
            for x in Teams:
                lc = [n.lower() for n in x]
                result = all(elem in lc for elem in duo)
                if result == True:
                    tms.append(', '.join(x))
                else:
                    pass
            dump = '\n'.join(tms)
            await ctx.send('```json\n"Teams with {} and {}"\n\n\n{}\n```'.format(char[0].capitalize(), char[1].capitalize(), dump))
    else:
        await ctx.send('{} could not be found in the list.  Make sure you follow formatting instructions (**++instructions**). Use **++chars** to see exact name of each character'.format([n for n in false]))         



###########WARSTATS###########


#stats command

@bot.command(name = 'stats', help = "Shows general and individual war statistics")
@commands.has_role('Alpha')
async def stats(ctx, *args):
    dbcon = DBConnect()
    names, wins, losses, ratio = dbcon.getall()
    if not args:
        t = 0 
        embed = discord.Embed(title="Alpha War Stats", description="**__Collective War Statistics__**", color=15844367)
        for n in range(len(names)):
            t += 1
            embed.add_field(name="**{}** | **__{}__**".format(t, names[n]), value=("**Wins:** {} | **Losses:** {} | **Ratio:** {}".format(wins[n], losses[n], ratio[n])), inline=False)  
    else:
        embed = discord.Embed(title="Alpha War Stats", description="**__Individual War Statistics__**\n", color=15844367)
        for x in args:
            if x.capitalize() not in names:
                embed.add_field(name=":x: **{}** not found".format(x.capitalize()), value=("Check the spelling"))
            else:
                for i in names:
                    if x.capitalize() == i:
                        xwins, xlosses, xratio = dbcon.getstat(x)
                        embed.add_field(name="**__{}__**".format(x.capitalize()), value=("**Wins:** {} | **Losses:** {} | **Ratio:** {}".format(xwins, xlosses, xratio)), inline=False)
    
    await ctx.send(embed=embed)


#add W/L command

@bot.command(name = 'add', hidden=True)
@commands.has_role('Record Keeper')
async def add(ctx, res, *players):
    dbcon = DBConnect()
    names = dbcon.nameget()
    if res.lower() == 'w':
        for x in players:
            if x.capitalize() in names:
                dbcon.addw(x)
                xwins, xlosses, xratio = dbcon.getstat(x)
                embed = discord.Embed(title=":regional_indicator_w: added to {}".format(x.capitalize()), description=("**Wins:** {} | **Losses:** {} | **Ratio:** {}".format(xwins, xlosses, xratio)), color=3447003)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=":x: **{}** not found".format(x.capitalize()), description=("Check the spelling"), color=15158332)
                await ctx.send(embed=embed) 
    elif res.lower() == 'l':
        for x in players:
            if x.capitalize() in names:
                dbcon.addl(x)
                xwins, xlosses, xratio = dbcon.getstat(x)
                embed = discord.Embed(title=":regional_indicator_l: added to {}".format(x.capitalize()), description=("**Wins:** {} | **Losses:** {} | **Ratio:** {}".format(xwins, xlosses, xratio)), color=3447003)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=":x: **{}** not found".format(x.capitalize()), description=("Check the spelling"), color=15158332)
                await ctx.send(embed=embed) 
    else:
        embed = discord.Embed(title=":x: Incorrect argument", description=("**Usage**: ++add W/L *name_1 name_2 ... name_x*"), color=15158332)
        await ctx.send(embed=embed)


#setx command

@bot.command(name = 'setx', hidden=True)
@commands.has_role('Record Keeper')
async def setx(ctx, name, w: int, l: int):
    dbcon = DBConnect()
    names = dbcon.nameget()
    if not name.capitalize() in names:
        embed = discord.Embed(title=":x: **{}** not found".format(name.capitalize()), description=("Check the spelling"), color=15158332)
        await ctx.send(embed=embed)
    else:
        dbcon.setx(name, w, l)
        winrate = '0%' if w+l == 0 else '{}%'.format(int(100/(w+l)*w))
        embed = discord.Embed(title=":arrows_counterclockwise: Stats for {} have been modified".format(name.capitalize()), description=("**Wins:** {} | **Losses:** {} | **Ratio:** {}".format(w, l, winrate)), color=15844367)
        await ctx.send(embed=embed)


#resetx command

@bot.command(name = 'resetx', hidden=True)
@commands.has_role('Record Keeper')
async def reset(ctx, *players):
    dbcon = DBConnect()
    names = dbcon.nameget()
    for name in players:
        if not name.capitalize() in names:
            embed = discord.Embed(title=":x: **{}** not found".format(name.capitalize()), description=("Check the spelling"), color=15158332)
            await ctx.send(embed=embed)
        else:
            dbcon.reset(name)
            embed = discord.Embed(title=":rewind: Stats for {} have been reset".format(name.capitalize()), description=("**Wins:** 0 | **Losses:** 0 | **Ratio:** 0%"), color=15844367)
            await ctx.send(embed=embed)


#add_player command

@bot.command(name="add_player", hidden=True)
@commands.has_role('Record Keeper')
async def add_player(ctx, name):
    dbcon = DBConnect()
    names = dbcon.nameget()
    if name.capitalize() in names:
        await ctx.send('Player already exists')
    else:
        dbcon.addentry(name.capitalize(), 0, 0)
        embed = discord.Embed(title=":information_source:", description=('**__{}__ has been added**'.format(name.capitalize())), color=15844367)
    await ctx.send(embed=embed)


#rem_player command

@bot.command(name="rem_player", hidden=True)
@commands.has_role('Record Keeper')
async def rem_player(ctx, name):
    dbcon = DBConnect()
    names = dbcon.nameget()
    if not name.capitalize() in names:
        await ctx.send('Not Found')
    else:
        dbcon.rementry(name.capitalize())
        embed = discord.Embed(title=":information_source:", description=('**__{}__ has been removed**'.format(name.capitalize())), color=15844367)
    await ctx.send(embed=embed)


###Internal

@bot.command(name="rule")
@commands.has_role('Internal')
async def rule(ctx):
    embed = discord.Embed(Title="Matchup Rule", description="You are not allowed to use {}".format(random.choice(rules)))
    await ctx.send(embed=embed)



###########TOURNAMENT###########


@bot.command(name="t")
async def tourny(ctx, *args):
    global ongoing, ttype
    ppool = [n.capitalize() for n in args]
    pnum = len(args)
    if not ongoing == 0:
        await ctx.send("{}-man tournament already underway".format(ttype))
    elif not (pnum & (pnum-1) == 0) and pnum != 0 and pnum > 2:
        await ctx.send('Number of Participants has to be a power of 2. (e.g.: 4, 8, 16)')
    elif pnum < 4:
        await ctx.send('Cannot start a tournament with fewer than 4 participants')
    else:
        dbcon = DBConnect()
        edition = dbcon.getcount()
        ongoing = pnum
        ttype = pnum
        mt = matchup(ppool)
        embed = discord.Embed(title=":game_die: Alpha Shuffle #{} || {}-man Tournament :game_die:".format(edition, pnum), description=shufflerules, color=10038562)
        embed.add_field(name="========================================================", value="=======================================================")
        for i in range(len(mt)):
            match = ' vs '.join(mt[i])
            embed.add_field(name="**Matchup [{}]: __{}__**".format(i+1, match), value="**{}'s Team:** {}\n**{}'s Team:** {}".format(mt[i][0], teamsel(), mt[i][1], teamsel()), inline=False)
        await ctx.send(embed=embed)


@bot.command(name="next")
async def advance(ctx, *args):
    global ongoing, ttype, stage
    if ongoing == 0:
        await ctx.send("No tournament started")
        return None
    elif ongoing != len(args)*2:
        await ctx.send("There were {} players last round. Next stage should have {}".format(ongoing, ongoing//2))
        return None
    elif ongoing == 2:
        await ctx.send("Finals already started, nowhere to advance")
        return None
    elif ongoing == 4:
        stage = 'Finals'
    elif ongoing == 8:
        stage = 'Semi-finals'
    else:
        stage = 'Last {}'.format(ongoing)
    ppool = [n.capitalize() for n in args]
    ongoing = len(args)   
    mt = matchup(ppool)
    if not stage == 'Finals':
        embed = discord.Embed(title="{}-man Tournament {}".format(ttype, stage), description=shufflerules, color=10038562)
        embed.add_field(name="=========================================================", value="=======================================================")
        for i in range(len(mt)):
            match = ' vs '.join(mt[i])
            embed.add_field(name="**Matchup [{}]: __{}__**".format(i+1, match), value="**{}'s Team:** {}\n**{}'s Team:** {}".format(mt[i][0], teamsel(), mt[i][1], teamsel()), inline=False)
    else:
        embed = discord.Embed(title="Finals: __{}__ vs __{}__".format(mt[0][0], mt[0][1]), description="**\n- Finals are 2/3\n- Each player will be given a pool of 3 teams\n- Each team can only be used once\n- Teams can be used in any order the player chooses**", color=10038562)
        embed.add_field(name="==========================================", value="=========================================")
        embed.add_field(name="**{}'s teams**".format(mt[0][0]), value='\n'.join([teamsel() for _ in range(3)]), inline=False)
        embed.add_field(name="**{}'s teams**".format(mt[0][1]), value='\n'.join([teamsel() for _ in range(3)]), inline=False)

    await ctx.send(embed=embed)

@bot.command(name='team', help='Generates random team')
async def team(ctx):
    await ctx.send(teamsel())


@bot.command(name="dice", help="Rolls a 6-sided dice.")
async def roll(ctx):
    dice_numbers = [1, 2, 3, 4, 5, 6]
    result = random.choice(dice_numbers)
    await ctx.send("You rolled a **{}**".format(result))


@bot.command(name="cancel", help='Cancels ongoing tournament')
async def cancel(ctx):
    global ongoing, ttype
    if ongoing == 0:
        await ctx.send(':x: No ongoing tournament - nothing to cancel')
    else:
        await ctx.send('{}-man Tournament cancelled.'.format(ttype))
        ttype = 0
        ongoing = 0
        

@bot.command(name="w", help="Declares tournament winner")
async def winner(ctx, name):
    global ongoing, ttype
    if not ongoing == 2:
        await ctx.send('Finals not played, cannot declare winner')
    else:
        dbcon = DBConnect()
        embed = discord.Embed(title=":trophy: Alpha Shuffle #{} WINNER: {}".format(dbcon.getcount(), name.capitalize()), description="You have been added to the hall of fame.", color=15844367)
        dbcon.addhof('{}-man'.format(ttype), name.capitalize())
        ttype = 0
        ongoing = 0
        pin = await ctx.send(embed=embed)
        await discord.Message.pin(pin) 

@bot.command(name='hof', help="Shows hall of fame")
async def hof(ctx):
    dbcon = DBConnect()
    rows = []
    ttypes, winners, editions = dbcon.gethof()
    for n in range(len(editions)):
        if n<9:
            rows.append('Shuffle #0{} || {} || WINNER: [{}]'.format(editions[n], ttypes[n], winners[n]))
        else:
            rows.append('Shuffle #{} || {} || WINNER: [{}]'.format(editions[n], ttypes[n], winners[n]))
    hof = '\n'.join(rows)
    await ctx.send('```\n{}\n``````css\n{}```'.format(tascii, hof))



bot.run(TOKEN)
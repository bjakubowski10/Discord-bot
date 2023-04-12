import discord #import discord.py, allows access to discords api
import os #used for getting the variable form the .env file
import json #needed to go through the websites
import ssl #will be used to ignore ssl certs
from dotenv import load_dotenv
import requests
from discord import app_commands
from discord import Embed
from discord.ext import tasks,commands #allows the use of command extension
from bs4 import BeautifulSoup
import datetime
from pytz import timezone
import aiohttp
import asyncio
import functools




load_dotenv()#loads the env file

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#gets the client object form discord.py, client is synonymous with bot
#bot = discord.Client(intents=intents)
newsK = os.getenv('NEWS_KEY')
newsD = os.getenv('DATA_KEY')

urltoembed = []
headline1 = []
img1 = []
url1toembed = []
headline2 = []
img2 = []

def news():
    main_url = "https://newsapi.org/v2/top-headlines?sources=the-wall-street-journal&apikey="+newsK
    news1 = requests.get(main_url).json() #gets the url, parses it, reads it, and decodes it onto a json
    article = news1['articles']
    for url in article:
        urltoembed.append(url['url'])
        headline1.append(url['title'])
        img1.append(url['urlToImage'])
            
def coinnews():
    main_url ="https://newsdata.io/api/1/news?apikey="+newsD+"&domain=cointelegraph"
    news1=requests.get(main_url).json()
    article = news1['results']
    for url in article:
        url1toembed.append(url['link'])
        headline2.append(url['title'])
        img2.append(url['image_url'])


bot = commands.Bot(command_prefix="/", intents = intents)
    
#event listener for when the bot has switched from offline to online
#discord is an asynchrous library so things r done with callbacks 
#aka a function called when something else happens
@bot.event #discord.py revolves around the concepts of events. as event is smth bot listens to and responds to
async def on_ready():#this function is called when bot is ready to start being used
    print(f'We have logged in as {bot.user}')
   #syncing slash commands 
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")#need to sync the commands to the bot itself
    except Exception as e:
        print(e)
        #can hook up the syncs to a command to have more control over it    
   
@bot.tree.command(name="newswsj",description = "display 5 top headlines from Wall Street Journal")
@app_commands.describe(number="How many links out of 5?")
async def wsj(interaction: discord.Interaction,number : int):
    news()
    
    await interaction.response.send_message(f"{interaction.user.mention} here's the data you requested")
    embed = discord.Embed(description='',color=0xFF5733)
    if number == 0:
        number = 1     
    number = min(number,5)
    for i in range(number):
        embed.description += f"[{headline1[i]}]({urltoembed[i]})\n\n"  
    embed.set_image(url=img1[number-1])
    embed.set_author(name=bot.user,icon_url=bot.user.avatar)
    embed.set_thumbnail(url=bot.user.avatar)
    embed.set_footer(text= "Click the hyperlinks for more information")    
    
    await interaction.followup.send(embed=embed)    
    
    headline1.clear()
    urltoembed.clear()
    img1.clear()    
  
  
  
bot.news_to_post = list()
bot.news_copy = list()  
  
@tasks.loop(hours=2)
async def setup_newsfeed():
    async with aiohttp.ClientSession() as session:#grab the json with aiohttp lib
        async with session.get("https://newsdata.io/api/1/news?apikey="+newsD+"&domain=cointelegraph") as resp:
            jsondata = await resp.json()
            
    channel = bot.get_channel(1058573318397116447) #get the crypto news channel
           
    article = jsondata['results'] #if data not in the list yet, we append it
    for data in article:
        if (data['title'],data['link'],data['image_url']) not in bot.news_to_post:
            bot.news_to_post.append((data['title'],data['link'],data['image_url']))
           
        
    for i in bot.news_to_post:#we print the news thats not in the copied list and append to it to check later, not using a list would break the branch
        if i not in bot.news_copy:
            embed = discord.Embed(title = i[0],url = i[1],description = f'Read the full article here...[LINK TO ARTICLE]({i[1]})\n\n')
            embed.set_image(url = i[2])
            embed.set_author(name = bot.user,icon_url = bot.user.avatar)
            embed.set_thumbnail(url=bot.user.avatar)
            embed.set_footer(text="Source: cointelegraph.com")
            await channel.send(embed=embed)
            bot.news_copy.append(i)   
        
#wait until the bot is ready before we do anything            
@setup_newsfeed.before_loop
async def beforenews():
    await bot.wait_until_ready()            
          
        
#prints the top 5 headlines from the source    
@bot.tree.command(name="coinnews",description="display top 5 headlines from Cointelegraph")
@app_commands.describe(number="How many links out of 5?")
async def coin(interaction: discord.Interaction,number : int):
    coinnews()
    await interaction.response.send_message(f"{interaction.user.mention} here's the data you requested")
    embed = discord.Embed(description='',color=0xFF5733)
    if number == 0:
        number = 1     
    number = min(number,5)
    for i in range(number):
        embed.description += f"[{headline2[i]}]({url1toembed[i]})\n\n"  
    embed.set_image(url=img2[number-1])
    embed.set_author(name=bot.user,icon_url=bot.user.avatar)
    embed.set_thumbnail(url=bot.user.avatar)
    embed.set_footer(text= "Click the hyperlinks for more information")    
    
    await interaction.followup.send(embed=embed)    
    
    headline2.clear()
    url1toembed.clear()
    img2.clear()    
    




#grab the updated json
bot.datadates = list()
bot.json_url = 'https://nfs.faireconomy.media/cc_calendar_thisweek.json'
async def grab_json_items():
    async with aiohttp.ClientSession() as session:
        async with session.get(bot.json_url) as resp:
            jsondata = await resp.json()
            return jsondata
def insert_json_into_tuple(needed_json): #insert the data of high relevance into the list as long as its not in it 
    for data in needed_json:
        if data['impact'] == 'High' and (data['date'],data['title'],data['country']) not in bot.datadates:
            bot.datadates.append((data['date'],data['title'],data['country']))

async def run_above_funcs2():#run the above functions in executor to not be blocking
    needed_json = await grab_json_items()
    callback = functools.partial(insert_json_into_tuple,needed_json)
    await bot.loop.run_in_executor(None,callback)
#task that runs the above code every 24hours to not miss the new json    
@tasks.loop(hours=24) 
async def weekly_json_grabber():
    await run_above_funcs2()
   
       
bot.us_east = timezone('US/Eastern')
bot.seconds_in_day=86400
bot.datadates_copy = list()
#checks for the event that is happening in less than 24 hours and posts a notification about it        
@tasks.loop(hours = 4)
async def data_checker(): 
    count = 0
    #print(bot.datadates)
    if len(bot.datadates) >0:
        for tup in reversed(bot.datadates):
        
            if tup not in bot.datadates_copy:
                count+=1
                #print(count)
                datetime_obj = datetime.datetime.fromisoformat(tup[0])
                curr_time = datetime.datetime.now(bot.us_east).replace(microsecond=0)
                if (datetime_obj - curr_time).total_seconds() < bot.seconds_in_day and (datetime_obj - curr_time).total_seconds() > 0:
            
                    embed = discord.Embed(title = 'Important event is happening soon!',url ='https://www.cryptocraft.com/calendar',description = f'{tup[1]} {tup[2]} at {datetime_obj.strftime("%I:%M%p %d/%m/%y ")}' )
                    embed.set_author(name=bot.user,icon_url=bot.user.avatar)
                    embed.set_thumbnail(url=bot.user.avatar)
                    embed.set_footer(text= "Click the title for a link to the event calendar") 
                    channel = bot.get_channel(1089512893164290048)
                    bot.datadates_copy.append(tup)
                    #await channel.send(f'{channel.guild.default_role}',embed=embed)
                    #await channel.send(f'{channel.guild.get_role(1052373829722320898).mention}',embed=embed)

                    await channel.send(embed=embed)
                    bot.datadates.remove(tup)
        #print(bot.datadates)    
            
@data_checker.before_loop
async def beforerunning():
    await bot.wait_until_ready()
#wait for the bot to be ready before running the task       
                    
@bot.event #bans people who join with account younger than a month
async def on_member_join(member : discord.Member):
    channel = bot.get_channel(1058562970810069103)
    creation = member.created_at
    if (discord.utils.utcnow() - creation).total_seconds() < 2628000:
        await channel.send(f'Your account is too young {member.mention}. Goodbye!')
        await member.ban(reason = "Account too young")
        
        
        

#the main function that runs the bot and the tasks in the background       
async def main():
    discord.utils.setup_logging()#shows all the errors
    weekly_json_grabber.start()
    data_checker.start()
    setup_newsfeed.start()
    await bot.start(os.getenv('DISCORD_TOKEN'))
asyncio.run(main()) 
    
#bot.run(os.getenv('DISCORD_TOKEN'),root_logger=True)


          
import discord #import discord.py, allows access to discords api
import os #used for getting the variable form the .env file
import newskey #api key
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
  
  
#bot.  
#@bot.tree.command(name = 'Newsfeed',description = 'Set up an automatic newsfeed in this channel')  
@tasks.loop(hours = 2)
async def setup_newsfeed():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://newsdata.io/api/1/news?apikey="+newsD+"&domain=cointelegraph") as resp:
            jsondata = await resp.json()
    article = jsondata['articles']
    embedurl = article[0]['link']
    headline = article[0]['title']
    img = article[0]['image_url']
            

#continue this later, gotta have my news be posted  
  
        
    
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
    





bot.datadates = list()
bot.json_url = 'https://nfs.faireconomy.media/cc_calendar_thisweek.json'
async def grab_json_items():
    async with aiohttp.ClientSession() as session:
        async with session.get(bot.json_url) as resp:
            jsondata = await resp.json()
            return jsondata
def insert_json_into_tuple(needed_json):
    for data in needed_json:
        if data['impact'] == 'High' and (data['date'],data['title'],data['country']) not in bot.datadates:
            bot.datadates.append((data['date'],data['title'],data['country']))

async def run_above_funcs2():
    needed_json = await grab_json_items()
    callback = functools.partial(insert_json_into_tuple,needed_json)
    await bot.loop.run_in_executor(None,callback)
    
@tasks.loop(hours=24) 
async def weekly_json_grabber():
    await run_above_funcs2()
       
bot.us_east = timezone('US/Eastern')
bot.seconds_in_day=86400
        
@tasks.loop(hours=24)
async def data_checker(): 
    count = 0
    print(bot.datadates)
    for tup in reversed(bot.datadates):
        count+=1
        print(count)
        datetime_obj = datetime.datetime.fromisoformat(tup[0])
        curr_time = datetime.datetime.now(bot.us_east).replace(microsecond=0)
        if (curr_time - datetime_obj).total_seconds() < bot.seconds_in_day:
            
            embed = discord.Embed(title = 'Important event is happening soon!',url ='https://www.cryptocraft.com/calendar',description = f'{tup[1]} {tup[2]} at {datetime_obj.strftime("%I:%M%p %d/%m/%y ")}' )
            embed.set_author(name=bot.user,icon_url=bot.user.avatar)
            embed.set_thumbnail(url=bot.user.avatar)
            embed.set_footer(text= "Click the title for a link to the event calendar") 
            channel = bot.get_channel(1052375001606660156)
            await channel.send(f'{channel.guild.default_role}',embed=embed)
            #await channel.send(embed=embed)
            bot.datadates.remove(tup)
            
@data_checker.before_loop
async def beforerunning():
    await bot.wait_until_ready()
            
                    
  


#the main function that runs the bot and the tasks in the background       
async def main():
    discord.utils.setup_logging()#shows all the errors
    weekly_json_grabber.start()
    data_checker.start()
    await bot.start(os.getenv('DISCORD_TOKEN'))
asyncio.run(main()) 
    
    
#bot.run(os.getenv('DISCORD_TOKEN'),root_logger=True)


          
          
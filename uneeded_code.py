#grabs the url needed from the html that was received in the function below with the aiohttp library
def retrieve_data_from_url(result): #BS4 is blocking so it cannot be run with async functions
    soup = BeautifulSoup(result,'html.parser')
    tags = soup('a')
    for tag in tags:
          if type(tag.get('href',None)) is str and "json" in tag.get('href',None):
            jsonurl1 = tag.get('href',None)
            return jsonurl1

#grabs the html of a given website and returns it to be used at a later date
async def retrieve_url_from_html():
     headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41'}
     async with aiohttp.ClientSession(headers=headers) as session:#we have a clientSession as session
        async with session.get('https://www.cryptocraft.com/calendar') as resp:#we have a clientResponse object called resp
            html= await resp.text()#we can get all the needed info from the response
            return html
        
#combiens the functions to the the final json url we need
#non async functions neededs to be ran in executor to not break the code
async def run_above_funcs(html):
    callback = functools.partial(retrieve_data_from_url,html)#basically inserts the html var as a param of the func
    finalurl = await bot.loop.run_in_executor(None,callback)#runs the function in a executor to not break the asyncio
    #need to run in exec when running blocking sync code within a coroutine context
    return finalurl

bot.final_url = ''
#sets the timed task to run the needed functions and give the final_url
#return in a task doesnt do anything if ur scheduling task to be run at specific tasks 
#so you need one big task to do all the sending
@tasks.loop(seconds=5)
async def everythingadded():
    html = await retrieve_url_from_html()
    bot.final_url = await run_above_funcs(html)

@everythingadded.error
async def everythingadded_handler():
    everythingadded.restart()

#tested function to check if we got the needed json file from the above commands        
@bot.tree.command(name = 'testurl')
async def test(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(bot.final_url)

import requests
from bs4 import BeautifulSoup
import re
import json
import datetime
from pytz import timezone
import aiohttp
import asyncio
import dateutil.parser

url = 'https://www.cryptocraft.com/calendar'
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41'}


#result= requests.get(url,headers=headers).text

async def async_func():
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get('https://www.cryptocraft.com/calendar') as resp:
            html= await resp.text()
            return html

result = asyncio.run(async_func())

print(result)
soup = BeautifulSoup(result, 'html.parser')
tags = soup('a')
jsonurl = ''
for tag in tags:
    #if type(tag.get('href',None)) is str
    print(tag.get('href',None))
    if tag.get("href", None) and "json" in tag.get('href',None):
        
        jsonurl = tag.get('href',None)

print('============================\n\n')
#print(jsonfile)
#find the json like https://nfs.faireconomy.media/cc_calendar_thisweek.json?version=5859908ea24dcc08ba33147e0bdc53e4

print(jsonurl)

print('============================\n\n')



jsonurl1 ='https://nfs.faireconomy.media/cc_calendar_thisweek.json?version=465d7297310eb9b6fe998a22cde180fa'


#above is completed for the bot, now its time for the bottom part
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

datadates = list()


async def async_func2(jsonurl1):
    async with aiohttp.ClientSession() as session:
        async with session.get(jsonurl1) as resp:
            json= await resp.json()
            return json

        
#jsonurl = requests.get(jsonurl).json()
grabbedjson = asyncio.run(async_func2(jsonurl1))

#print(json.dumps(grabbedjson,indent=4))

for data in grabbedjson:
    if data['impact'] == 'High':
        datadates.append((data['date'],data['title'],data['country']))

for i in datadates:
    print(i)
    
    
     
    
        
print('=====================\n\n')
seconds_in_day=86400
for tuples in datadates:
    time_to_check = tuples[0]
    print(type(time_to_check),time_to_check)
    print('===')
    datetimeobj = datetime.datetime.fromisoformat(tuples[0])
    print(datetimeobj, type(datetimeobj))
    us_east=timezone('US/Eastern')
    curr_time = datetime.datetime.now(us_east).replace(microsecond=0)#.isoformat()
    print(type(curr_time),curr_time)
    if (curr_time - datetimeobj).total_seconds() < seconds_in_day:
        print("it's time to send an announcement")
        print(datetimeobj)
        print('aaaaaa====aaaa')
    
    #isodate = dateutil.parser.parse(time_to_check)
    #print(isodate.isoformat(),type(isodate.isoformat()))
    #print('===')
    
us_east=timezone('US/Eastern')
print(datetime.datetime.now(us_east).replace(microsecond=0).isoformat())





          
          


#async_func()
    
#once i have the list of tuples, iterate thro each one every 24h and put them in vars to compare to time

    
#every day, something i havent coded yet, will check if the current time is 24h away from date 
#if so it will make an announcment which prints the date of the event, the events title and the country

    
    
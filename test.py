import requests
url1toembed = list()
headline2 = list()
img2=list()

newsD = 'pub_195595333709de4b0c7d3626dd55d1dadb79b'
def coinnews():
    main_url ="https://newsdata.io/api/1/news?apikey="+newsD+'&domain=cointelegraph'#&category=business,technology'#+"&domain=cointelegraph"
    news1=requests.get(main_url).json()
    article = news1['results']
    for url in article:
        print(url['title'])
    #article = news1['results']
    #for url in article:
     #   url1toembed.append(url['link'])
      #  headline2.append(url['title'])
       # img2.append(url['image_url'])
        
coinnews()

#for i in headline2:
 #       print(i)
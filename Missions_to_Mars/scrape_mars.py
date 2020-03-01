# Dependencies
from bs4 import BeautifulSoup
import requests
import pandas as pd
from splinter import Browser

def init_browser():
    executable_path = {"executable_path": "C:/Users/nickc/Downloads/chromedriver_win32/chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)
#function used to scrape websites
def scrape():
    #dictonary for all data collected from webscraping to be return and loaded in mongodb
    mars_data={}
    browser=init_browser()
    url="https://mars.nasa.gov/news/"
    browser.visit(url)
    html=browser.html
    soup=BeautifulSoup(html,'html.parser')

    news=soup.find('li', class_='slide')
    mars_data["news_title"]=news.find('h3').text
    mars_data["news_p"]=news.find('div',class_="rollover_description_inner").text

    url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    
    browser.visit(url)

    browser.fill('search','Featured')
    browser.type('search','\n')

    html=browser.html
    soup=BeautifulSoup(html,'html.parser')

    img_loc=soup.find('div',class_='img')
    img_title=img_loc.find('img').get('alt')

    browser.click_link_by_partial_text(img_title)

    html=browser.html
    soup=BeautifulSoup(html)

    li_slide=soup.find('li', class_='slide')
    image=li_slide.find('a',class_='fancybox').get('data-fancybox-href')
    mars_data["featured_image_url"]='https://www.jpl.nasa.gov'+image

    url='https://twitter.com/marswxreport?lang=en'

    response=requests.get(url)

    soup=BeautifulSoup(response.text,'html.parser')

    tweets=soup.select('#timeline li.stream-item')
    tweet_list=[]
    for tweet in tweets:
        tweet_temp=tweet.select('p.tweet-text')[0].get_text()
        tweet_list.append(tweet_temp)
    mars_data["mars_weather"]=tweet_list[0]

    url='https://space-facts.com/mars/'
    mars_table=pd.read_html(url)
    mars_table=pd.DataFrame(mars_table[0])
    mars_facts=[]
    #creating a dictonary for mars facts, used to create table in html page
    for i in  mars_table.index:
        mars_facts.append({"type":mars_table[0][i], "value":mars_table[1][i]})
    mars_data["mars_facts"]=mars_facts

    home_url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(home_url)
    html=browser.html
    soup=BeautifulSoup(html,'html.parser')

    names=soup.find_all('h3')
    hemisphere_names=[]
    for name in names:
        hemisphere_names.append(name.text)

    hemisphere_image_urls=[]
    for name in hemisphere_names:
        browser.click_link_by_partial_text(name)
        html=browser.html
        soup=BeautifulSoup(html,'html.parser')
        body=soup.find('div',class_='downloads')
        image_links=body.find('a')
        image_url=image_links.get('href')
        hemisphere_image_urls.append({'title':name,'img_url':image_url})
        browser.visit(home_url)
    mars_data["hemisphere_urls"]=hemisphere_image_urls

    return mars_data

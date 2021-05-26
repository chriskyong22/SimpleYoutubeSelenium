import urllib;
import urllib.parse;
import urllib.request;
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By 
from dotenv import load_dotenv
load_dotenv()
import os

# yt-simple-endpoint style-scope ytd-video-renderer
def searchYoutube(songName):

    driver = webdriver.Firefox(executable_path=os.environ.get("geckodriverPath"))
    
    query = urllib.parse.quote(songName)
    url = "https://www.youtube.com/results?search_query=" + query
    driver.get(url)

    VIDEO_ELEMENT = "video-title"

    elements = driver.find_elements_by_id(VIDEO_ELEMENT)
    links = []

    for element in elements:
        links.append(element.get_attribute("href"))
        print(links[-1])

    driver.close()

    return links
    

if (__name__ == "__main__"):
    youtubeLinks = searchYoutube("tester")
    print(youtubeLinks)
import urllib;
import urllib.parse;
import urllib.request;
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By 
from dotenv import load_dotenv
import os
import spotipy
from spotipy import client
from spotipy.oauth2 import SpotifyClientCredentials
import youtube_dl 

load_dotenv()

# yt-simple-endpoint style-scope ytd-video-renderer
def searchYoutube(songs):

    driver = webdriver.Firefox(executable_path=os.environ.get("geckodriverPath"))
    VIDEO_ELEMENT = "video-title"
    songLinks = []
    processed = 0
    for song in songs:
        query = urllib.parse.quote(song)
        url = "https://www.youtube.com/results?search_query=" + query
        driver.get(url)
        elements = driver.find_elements_by_id(VIDEO_ELEMENT)
        links = []
        for element in elements:
            if (element.get_attribute("href") == None):
                continue
            links.append(element.get_attribute("href"))
        songLinks.append(links)
        processed += 1
        print (f"Progress: {(processed / len(songs)) * 100}")
    driver.close()
    return songLinks
    
def getSpotifySongs(playlistID):
    songs = []
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=os.environ.get("spotify-client-id"), 
        client_secret=os.environ.get("spotify-client-secret")))
    results = spotify.playlist(playlistID, fields="tracks")
    for item in results['tracks']['items']:
        songs.append(f"{item['track']['name']} {item['track']['artists'][0]['name']}")
    return songs

if (__name__ == "__main__"):
    playlistID = '37i9dQZF1DX7Jl5KP2eZaS'
    urls = []
    urls = searchYoutube(getSpotifySongs(playlistID))
    print(urls)
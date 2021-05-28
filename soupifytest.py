import urllib;
import urllib.parse;
# import urllib.request;
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait 
# from selenium.webdriver.common.by import By 
from dotenv import load_dotenv
import os;
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
# from spotipy import client

import youtube_dl 

load_dotenv()

# yt-simple-endpoint style-scope ytd-video-renderer
def searchYoutube(songs):

    driver = webdriver.Firefox(executable_path=os.environ.get("geckodriverPath"))
    VIDEO_ELEMENT = "video-title"
    YOUTUBE_SEARCH = "https://www.youtube.com/results?search_query="
    LIMIT = 5
    songLinks = []

    for idx, song in enumerate(songs):

        query = urllib.parse.quote(song)
        url = YOUTUBE_SEARCH + query

        driver.get(url)

        elements = driver.find_elements_by_id(VIDEO_ELEMENT)
        
        links = []
        for element in elements:
            if (element.get_attribute("href") != None):
                links.append(element.get_attribute("href"))
                if len(links) == LIMIT:
                    break

        songLinks.append((song, links))

        print (f"Progress: {((idx + 1) / len(songs)) * 100}")

    driver.close()

    return songLinks
    
def getSpotifySongs(playlistID):

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=os.environ.get("spotify-client-id"), 
        client_secret=os.environ.get("spotify-client-secret")))

    # Retrieve the playlist contents
    results = spotify.playlist(playlistID, fields=["tracks"])

    songs = []

    # Parse the contents 
    for item in results['tracks']['items']:
        
        # Get all artists of the track
        artists = ""
        for artist in item['track']['artists']:
            artists += f"{artist['name']} "

        # Want to get rid of the last " " therefore -1 for artists
        songs.append(f"{item['track']['name']} {artists[:-1]}")

    return songs

if (__name__ == "__main__"):
    playlistID = '37i9dQZF1DX7Jl5KP2eZaS'
    urls = searchYoutube(getSpotifySongs(playlistID))
    for (song, url) in urls:
        print(song)
        print(url)
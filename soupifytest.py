import urllib;
import urllib.parse;
# import urllib.request;
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait 
# from selenium.webdriver.common.by import By 
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
# from spotipy import client
import sqlite3 
from sqlite3 import Error 
import datetime

from dotenv import load_dotenv
import os;
import youtube_dl 
load_dotenv()

class Logger(object):

    def debug(__self__, msg):
        pass

    def warning(__self__, msg):
        pass 

    def error(__self__, msg):
        print(msg)

def youtubeDownload(songs):

    options = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "download_archive": "downloaded.txt",
        'noplaylist' : True,
        "outtmpl": "./songs/%(title)s %(id)s.%(ext)s'",
        "logger": Logger(),
    }

    with youtube_dl.YoutubeDL(options) as ytdl:
        for (song, urls) in songs:
            if (len(urls) > 0):
                print(urls[0])
                ytdl.download([urls[0]])



# yt-simple-endpoint style-scope ytd-video-renderer
def searchYoutube(songs, limit=5):

    CSS_VIDEO_ID = "video-title"
    YOUTUBE_SEARCH = "https://www.youtube.com/results?search_query="

    songLinks = []
    numberOfSongs = len(songs)
    # Note if the browser has to update, the script will crash. 
    # (Just wait for update and then execute again)
    with webdriver.Firefox(executable_path=os.environ.get("geckodriverPath")) as driver:
        for idx, song in enumerate(songs, start=1):

            query = urllib.parse.quote(song)
            url = YOUTUBE_SEARCH + query

            driver.get(url)

            elements = driver.find_elements_by_id(CSS_VIDEO_ID)
            
            links = []
            for element in elements:
                if (element.get_attribute("href") != None):
                    links.append(element.get_attribute("href"))
                    if len(links) == limit:
                        break

            songLinks.append((song, links))

            print (f"Progress: {(idx / numberOfSongs) * 100}")

    return songLinks

def getPlaylistSpotifySongs(playlistID):

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

def getAlbumSpotifySongs(albumID):

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=os.environ.get("spotify-client-id"), 
        client_secret=os.environ.get("spotify-client-secret")))

    # Retrieve the album contents
    results = spotify.album(albumID)

    songs = []

    # Parse the contents 
    for item in results['tracks']['items']:

        # Get all artists of the track
        artists = ""
        for artist in item['artists']:
            artists += f"{artist['name']} " 

        # Want to get rid of the last " " therefore -1 for artists
        songs.append(f"{item['name']} {artists[:-1]}")

    return songs

def updateCache(songsFolder="./songs", cacheFile="./downloaded.txt"):
    directory = os.scandir(songsFolder)
    storedVideos = ""
    for file in directory:
        # Seperate the File Name into its respective parts listed in the options of youtube dl
        youtubeID = file.name.split(" ")

        # Get rid of the .mp3 extension
        youtubeID = youtubeID[-1].split(".")[0]

        storedVideos += f"youtube {youtubeID}\n"
    with open(cacheFile, "w") as cache:
        cache.write(storedVideos) 

def archiveURL(databaseLocation, songInfo):
    song = songInfo[0]
    urls = " ".join(songInfo[1])
    executeQuery(databaseLocation, 
            '''INSERT INTO urlCache (song, urls, dateEntered) 
                VALUES(?, ?, datetime('now')) 
                ON CONFLICT(song) DO UPDATE SET urls=(?), dateEntered=datetime('now')''', 
                (song, urls, urls)
            )
    
def retrieveURLFromCache(databaseLocation, song):
    urls = []
    SECONDS_IN_HOUR = 3600
    HOURS_IN_DAY = 24
    for row in executeQuery(databaseLocation, "select * from urlCache where song=(?)", (song,)):
        dateEntered = row[-1]
        current = datetime.datetime.utcnow()
        past = datetime.datetime.strptime(dateEntered, '%Y-%m-%d %H:%M:%S')
        timePassed = current - past
        if (timePassed.total_seconds() / SECONDS_IN_HOUR < HOURS_IN_DAY):
            urls = row[1].split(" ")
    return urls

def getURLs(songsInfo):
    databaseLocation = "./urlCache"
    songsWithURLs = []
    songsNotInCache = []
    for song in songsInfo:
        urls = retrieveURLFromCache(databaseLocation, song)
        if urls:
            songsWithURLs.append((song, urls))
        else:
            songsNotInCache.append(song)

    songsNotInCache = searchYoutube(songsNotInCache)
    for song in songsNotInCache:
        archiveURL(databaseLocation, song)
        print(song)

    return songsWithURLs
    

def executeQuery(databaseLocation, query, params=()):
    with sqlite3.connect(databaseLocation) as connection:
        cursor = connection.cursor()
        return cursor.execute(query, params)

def getAllRows():
    for row in executeQuery("./urlCache", '''select * from urlCache'''):
        print(row)

if (__name__ == "__main__"):
    databaseLocation = "./urlCache"
    executeQuery(databaseLocation, '''CREATE TABLE IF NOT EXISTS urlCache 
            (song varchar PRIMARY KEY, urls varchar, dateEntered TEXT)''')
    # print(retrieveURLFromCache(databaseLocation, "bob - tooty"))
    # archiveURL(databaseLocation, ("bob - tooty", ["youtube.com/tester", "youtube.com/testmaker"]))
    playlistID = '37i9dQZF1DX7Jl5KP2eZaS'

    urls = getURLs(getPlaylistSpotifySongs(playlistID))
    updateCache()
    for (song, url) in urls:
        print(song)
        print(url)
    # youtubeDownload(urls)
    
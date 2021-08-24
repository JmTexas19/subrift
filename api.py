import json
import requests
import uuid
import xml.etree.ElementTree as ET

from authentication import generateHash, generateSalt

#Retrieve data from json file
with open("subrift.json", "r") as read_file:
    data = json.load(read_file)

hostname = data["SUBSONICSERVER"]["HOST"]
username = data["USER"]["USERNAME"]
password = data["USER"]["PASSWORD"]

#Generate Salt, Client, & Hash
salt = generateSalt()
token = generateHash(password, salt)
client = 'Subrift'

#Namespaces
ns = {'sub' : 'http://subsonic.org/restapi'}

#Classes
class songInfo:
    def __init__(self, id, title, artist, album, coverArt):
        self.id = id
        self.title = title
        self.artist = artist
        self.album = album
        self.coverArt = coverArt

class albumInfo:
    def __init__(self, id, title, artist, coverArt):
        self.id = id
        self.title = title
        self.artist = artist
        self.coverArt = coverArt

class playlistInfo:
    def __init__(self, id, title):
        self.id = id
        self.title = title

#(string) Pings the server to test if online
def pingServer():
    #Test Request URL
    URL = hostname + '/rest/ping'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client
    }

    #Send Request
    r = requests.get(url = URL, params = PARAMS)

    #Parse XML & Print result
    root = ET.fromstring(r.text)

    #Pings the server to test if online
    print(root.attrib['status'])

#(string) Returns whether the license is valid
def getLicense():
    #Test Request URL
    URL = hostname + '/rest/getLicense'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client
    }

    #Send Request
    r = requests.get(url = URL, params = PARAMS)

    #Parse XML & Print result
    root = ET.fromstring(r.text)
    print('License Valid: ' + root[0].attrib['valid'])

#(xml) Returns xml object containing music folders
def getMusicFolders():
    #Test Request URL
    URL = hostname + '/rest/getMusicFolders'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client
    }

    #Send Request
    return requests.get(url = URL, params = PARAMS)

#Prints music folders
def printMusicFolders():
    #Parse XML
    root = ET.fromstring(getMusicFolders().text)

    #Print Name & ID of each music folder
    for musicFolders in root.findall("sub:musicFolders", namespaces=ns):
        for musicFolder in musicFolders.findall('sub:musicFolder', namespaces=ns):
            name = musicFolder.attrib["name"]
            id = musicFolder.attrib["id"]
            print(name, id)

#(xml) Returns xml object containing indexes
def getIndexes():
    #Test Request URL
    URL = hostname + '/rest/getIndexes'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client
    }

    #Send Request
    return requests.get(url = URL, params = PARAMS)

#(xml) Returns xml object containing music directory when given id
def getMusicDirectory(id):
    #Test Request URL
    URL = hostname + '/rest/getMusicDirectory'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client,
        "id": id
    }

    #Send Request
    return requests.get(url = URL, params = PARAMS)

#(xml) Returns xml object containing search results
def search(query):
    #Test Request URL
    URL = hostname + '/rest/search3'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client,
        "query": query
    }

    #Send Request
    return requests.get(url = URL, params = PARAMS)

#(binary) Returns request containing song data
def streamSong(id):
    #Test Request URL
    URL = hostname + '/rest/stream'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client,
        "id": id
    }

    #Send Request
    return requests.get(url = URL, params = PARAMS, stream=True)

#(binary) Returns request containing raw song data
def downloadSong(id):
    #Test Request URL
    URL = hostname + '/rest/stream'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client,
        "id": id
    }

    #Send Request
    return requests.get(url = URL, params = PARAMS)

#(binary) Searches song given query and returns the song data
def getSong(query):
    #Query song & save xml response into root
    root = ET.fromstring(search(query).text)

    #Create songInfo object that will hold song information
    song = None

    #Grab first song
    for result in root.findall("sub:searchResult3", namespaces=ns):
        #Get FIRST song result
        for song in result.findall("sub:song", namespaces=ns):
            #Check for empty attributes
            song_id = ''
            title = ''
            artist = ''
            album = ''
            coverArt = ''
            if 'id' in song.attrib:
                song_id = song.attrib["id"]
            if 'title' in song.attrib:
                title = song.attrib["title"]
            if 'artist' in song.attrib:
                artist = song.attrib["artist"]
            if 'album' in song.attrib:
                album = song.attrib["album"]
            if 'coverArt' in song.attrib:
                coverArt = song.attrib["coverArt"]

            #Create object & break
            song = songInfo(song_id, title, artist, album, coverArt)
            break

    return song

#(binary) Searches album given query and returns the album
def getAlbum(query):
    #Query album & save xml response into root
    root = ET.fromstring(search(query).text)

    #Create albumInfo object that will hold song information
    album = None

    #Grab first song
    for result in root.findall("sub:searchResult3", namespaces=ns):
        #Get FIRST song result
        for album in result.findall("sub:album", namespaces=ns):
            #Check for empty attributes
            album_id = ''
            title = ''
            artist = ''
            coverArt = ''
            if 'id' in album.attrib:
                album_id = album.attrib["id"]
            if 'name' in album.attrib:
                title = album.attrib["name"]
            if 'artist' in album.attrib:
                artist = album.attrib["artist"]
            if 'coverArt' in album.attrib:
                coverArt = album.attrib["coverArt"]

            #Create object & break
            album = albumInfo(album_id, title, artist, coverArt)
            break

    return album

#(binary) Returns request containing raw song data
def getCoverArt(id):
    #Test Request URL
    URL = hostname + '/rest/getCoverArt'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client,
        "id": id
    }

    #Send Request
    return requests.get(url = URL, params = PARAMS)


#(songInfo) Returns an array of songInfo objects that contain song info
def getSearchResults(query):
    #Query song and save xml response into root
    root = ET.fromstring(search(query).text)

    #Take all results from list as songInfo objects
    songInfoList = []
    for result in root.findall("sub:searchResult3", namespaces=ns):
        for song in result.findall("sub:song", namespaces=ns):
            #Check for empty attributes
            song_id = ''
            title = ''
            artist = ''
            album = ''
            coverArt = ''
            if 'id' in song.attrib:
                song_id = song.attrib["id"]
            else:
                continue
            if 'title' in song.attrib:
                title = song.attrib["title"]
            if 'artist' in song.attrib:
                artist = song.attrib["artist"]
            if 'album' in song.attrib:
                album = song.attrib["album"]
            if 'coverArt' in song.attrib:
                coverArt = song.attrib["coverArt"]

            #Create Object and Append
            songInfoList.append(songInfo(song_id, title, artist, album, coverArt))

    return songInfoList

#(binary) Returns a listing of songs in an album.
def getAlbumData(id):
    #Test Request URL
    URL = hostname + '/rest/getAlbum'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client,
        "id": id
    }

    #Send Request and Parse XML
    result = requests.get(url = URL, params = PARAMS)
    root = ET.fromstring(result.text)

    #Put All Songs in List
    songInfoList = []
    for album in root.findall("sub:album", namespaces=ns):
        for entry in album.findall("sub:song", namespaces=ns):
            #Check for empty attributes
            song_id = ''
            title = ''
            artist = ''
            album = ''
            coverArt = ''
            if 'id' in entry.attrib:
                song_id = entry.attrib["id"]
            else:
                continue
            if 'title' in entry.attrib:
                title = entry.attrib["title"]
            if 'artist' in entry.attrib:
                artist = entry.attrib["artist"]
            if 'album' in entry.attrib:
                album = entry.attrib["album"]
            if 'coverArt' in entry.attrib:
                coverArt = entry.attrib["coverArt"]

            #Create Object and Append
            songInfoList.append(songInfo(song_id, title, artist, album, coverArt))

    return songInfoList


#(binary) Returns a listing of files in a saved playlist.
def getPlaylistData(id):
    #Test Request URL
    URL = hostname + '/rest/getPlaylist'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client,
        "id": id
    }

    #Send Request and Parse XML
    result = requests.get(url = URL, params = PARAMS)
    root = ET.fromstring(result.text)

    #Put All Songs in List
    songInfoList = []
    for playlist in root.findall("sub:playlist", namespaces=ns):
        for entry in playlist.findall("sub:entry", namespaces=ns):
            #Check for empty attributes
            song_id = ''
            title = ''
            artist = ''
            album = ''
            coverArt = ''
            if 'id' in entry.attrib:
                song_id = entry.attrib["id"]
            else:
                continue
            if 'title' in entry.attrib:
                title = entry.attrib["title"]
            if 'artist' in entry.attrib:
                artist = entry.attrib["artist"]
            if 'album' in entry.attrib:
                album = entry.attrib["album"]
            if 'coverArt' in entry.attrib:
                coverArt = entry.attrib["coverArt"]

            #Create Object and Append
            songInfoList.append(songInfo(song_id, title, artist, album, coverArt))

    return songInfoList


#(playlistInfo) Returns list of playlist
def getPlaylist(query):

    #Test Request URL
    URL = hostname + '/rest/getPlaylists'

    #Parameters
    PARAMS = {
        "u" : username,
        "t" : token,
        "s" : salt,
        "v" : '1.15.0',
        "c" : client
    }

    #Send Request and Parse XML
    result = requests.get(url = URL, params = PARAMS)
    root = ET.fromstring(result.text)

    #Put All Playlist in List
    for playlistList in root.findall("sub:playlists", namespaces=ns):
        for playlist in playlistList.findall("sub:playlist", namespaces=ns):
            #Match and Return Playlist with Song Objects
            if(playlist.attrib["name"] == query):
                return getPlaylistData(playlist.attrib['id'])

        #No Results
        return None

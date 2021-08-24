import discord
import json
import api
import asyncio
import time
import random
import typing
from discord.ext import commands

#Classes
class Player():
    def __init__(self, ctx, vc, song):
        self.ctx = ctx
        self.vc = vc
        self.song = song

    #Start Song
    async def start(self):
        ctx = self.ctx
        vc = self.vc
        song = self.song

        #Check if bot was disconnected.
        if not client.voice_clients:
            #TO DO Clear Queue
            print("I can't feel my legs")
            clearQueue()
            client.loop.call_soon_threadsafe(playNext.set)

        #Otherwise, Play those BEATS
        else:
            #Embed Message
            embed = discord.Embed(
                title = 'Playing {0} by {1}'.format(song.title, song.artist),
                color = discord.Color.orange(),
                description = '[Download]({0})'.format(api.streamSong(song.id).url)
            )
            embed.set_author(name='SubRift')
            embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/699752709028446259/df9496def162ef55bcaa9a2005c75ab2.png?size=256')

            #Check cover art
            if song.coverArt != '':
                embed.set_image(url=api.getCoverArt(song.coverArt).url)

            await ctx.send(embed=embed)

            #Play
            serverQueue.pop(0)
            beforeArgs = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            vc.play(discord.FFmpegPCMAudio(source=api.streamSong(song.id).url,  before_options=beforeArgs), after=toggleNext)

#Queue & Event
songs = asyncio.Queue()
playNext = asyncio.Event()

#Queue List (For Printing)
serverQueue = []

#Assign client to commands bot
client = commands.Bot(command_prefix='s!')

#Retrieve data from json file
with open("subrift.json", "r") as read_file:
    data = json.load(read_file)

TOKEN = data["USER"]["TOKEN"]

#Logs Bot in
@client.event
async def on_ready():
    print('Logged in as {0.user}' .format(client))

#Ping bot
@client.command()
async def ping(ctx):
    if ctx.author == client.user:
        return

    await ctx.channel.send('Pong!')

#Audio Player
async def audioPlayer():
    while True:
        #Clear flag and get from queue
        playNext.clear()
        player = await songs.get()
        await player.start()
        await playNext.wait()

#Toggles next song
def toggleNext(self):
    client.loop.call_soon_threadsafe(playNext.set)

#Next Song
@client.command()
async def skip(ctx):
    #In Voice?
    if client.voice_clients is not None:
        #Playing Music?
        if client.voice_clients[0].is_playing():
            #Queue Empty?
            if songs.qsize() == 0:
                await ctx.send('Queue is empty')
            #Stop and play next song
            else:
                client.voice_clients[0].stop()
        else:
            await ctx.send('Nothing Playing')

#Play Song Discord Command
@client.command()
async def play(ctx, option: typing.Optional[int] = None, *, query):
    #Check if author is NOT in voice chat
    if ctx.author.voice is None:
        await ctx.send("You need to join a voice channel first.")
        return

    else:
        #Join channel if not already in one
        if not client.voice_clients:
            vc = await (ctx.author.voice.channel).connect()
        else:
            vc = client.voice_clients[0]

        #Check if player should add to queue or play immediately
        if vc.is_playing() == True:
            #Play Now
            if option == 1:
                vc.stop()
                clearQueue()
                serverQueue.clear()

        #Add to Queue & Play Song
        song = api.getSong(query)
        if song is not None:
            serverQueue.append(song)
            await ctx.send('Added to Queue')
            await playSong(ctx, vc, song)
        else:
            await ctx.send("Song Doesn't Exist")

#Play Song
async def playSong(ctx, vc, song):
    if song is not None:
        #Create Player & Place in queue
        player = Player(ctx, vc, song)
        await songs.put(player)
    else:
        await ctx.send("Does not exist")

@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Try `play [song-title]`')

#Stop Song
@client.command()
async def stop(ctx):\
    #Check if Bot is in Voice
    if client.voice_clients:
        vc = client.voice_clients[0]
        #Check if Music is Playing
        if vc.is_playing() == True:
            vc.stop()
            clearQueue()
            serverQueue.clear()
            await vc.disconnect()
        else:
            await ctx.channel.send('Nothing is playing')
    else:
        await ctx.channel.send('Plug me in')

#Pause Song
@client.command()
async def pause(ctx):
    if client.voice_clients:
        vc = client.voice_clients[0]
        if vc.is_playing() == True:
            vc.pause()
        else:
            await ctx.channel.send('Nothing is playing')
    else:
        await ctx.channel.send('Plug me in')

#Resume Song
@client.command()
async def resume(ctx):
    if client.voice_clients:
        vc = client.voice_clients[0]
        if vc.is_playing() == False:
            vc.resume()
        else:
            await ctx.channel.send('Song is already playing')
    else:
        await ctx.channel.send('Plug me in')

#Search Server
@client.command()
async def search(ctx, *, query):
    #Check bot didn't say nuthin
    if ctx.author == client.user:
        return
    #Display Search Results
    else:
        #Get Search Results
        songInfoList = api.getSearchResults(query)

        #Embed Message
        embed = discord.Embed(
            title = 'Search Results',
            color = discord.Color.orange()
        )
        embed.set_footer(text='https://cptg.dev')
        embed.set_author(name='SubRift')
        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/699752709028446259/df9496def162ef55bcaa9a2005c75ab2.png?size=256')

        #Add Field for every song
        for song in songInfoList:
            embed.add_field(
                name=str(song.id),
                value='{0} - {1}'.format(song.title, song.artist),
                inline=False
            )

        await ctx.send(embed=embed)

#Check Queue
@client.command()
async def queue(ctx):
    #Embed Message
    embed = discord.Embed(
        title = 'Queue',
        color = discord.Color.orange()
    )
    embed.set_footer(text='https://cptg.dev')
    embed.set_author(name='SubRift')
    embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/699752709028446259/df9496def162ef55bcaa9a2005c75ab2.png?size=256')

    #Add Field for every song
    count = 1
    for song in serverQueue:
        embed.add_field(
            name=count,
            value='{0} - {1}'.format(song.title, song.artist),
            inline=False
        )
        count = count + 1

    await ctx.send(embed=embed)

#Post download link to song
@client.command()
async def download(ctx, *, query):
    #Get Song Info
    song = api.getSong(query)

    if song is not None:
        #Create Player & Place in queues
        await ctx.send(api.streamSong(song.id).url)
    else:
        await ctx.send("Song does not exist")

#Post download link to song
@client.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.send("This is so sad...")
    await ctx.bot.logout()

#Play Playlist
@client.command()
async def playlist(ctx, option: typing.Optional[int] = None, *, query):
    #Check if author is NOT in voice chat
    if ctx.author.voice is None:
        await ctx.send("You need to join a voice channel first.")
        return

    else:
        #Join channel if not already in one
        if not client.voice_clients:
            vc = await (ctx.author.voice.channel).connect()
        else:
            vc = client.voice_clients[0]

        #Stop Current Song & Clear Queue
        if vc.is_playing() == True:
            vc.stop()
            clearQueue()
            serverQueue.clear()

        #Get Playlist Info
        playlist = api.getPlaylist(query)

        #Check if Empty
        if playlist is not None:

            #Shuffle if -s Given
            if option == 1:
                random.shuffle(playlist)

            #Populate Songs Queue
            for entry in playlist:
                await playSong(ctx, vc, entry)

            #Place all but current in Queue
            playlist.pop(0)
            for entry in playlist:
                serverQueue.append(entry)
        else:
            await ctx.send('Playlist Not Found. Enter Exact Name')

#Shuffle Queue
@client.command()
async def shuffle(ctx):
    #Check if author is NOT in voice chat
    if ctx.author.voice is None:
        await ctx.send("You need to join a voice channel first.")
        return

    else:
        #Check Queue is not empty
        if len(serverQueue) == 0:
            await ctx.send("Queue is empty")

        else:
            #Shuffle Service Queue
            random.shuffle(serverQueue)

            #Join channel if not already in one
            if not client.voice_clients:
                vc = await (ctx.author.voice.channel).connect()
            else:
                vc = client.voice_clients[0]

            #Clear Current Queue
            clearQueue()

            #Populate Queue
            for entry in serverQueue:
                await playSong(ctx, vc, entry)

#Clear Queue
def clearQueue():
    for _ in range(songs.qsize()):
        songs.get_nowait()
        songs.task_done()

client.loop.create_task(audioPlayer())
client.run(TOKEN)

import io
from re import search
import discord
from discord import client
from discord import voice_client
from discord import channel
from discord import embeds
from discord.errors import ClientException
from discord.ext import commands
from discord.ext.commands.core import command
from discord.voice_client import VoiceClient
import discord.utils
from discord.opus import Encoder
from youtubesearchpython import VideosSearch
from youtubesearchpython import *

#from discord.ext.commands import Bot
import asyncio
import logging
import time
import pickle
import json as js
import sys
import os
import youtube_dl
from datetime import datetime
from gtts import gTTS
from io import BytesIO
from discord import FFmpegPCMAudio
import subprocess
import shlex
import requests
import random
from dotenv import load_dotenv
from youtube_dl.postprocessor import ffmpeg

#SETTING UP LOGGING
#add speech to text maybe?
#logging.basicConfig(level=logging.INFO)

#setting up simple logging
bot = commands.Bot(command_prefix='!')
queue = {}
active = {}

#load token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

data = {}
load_file = 'players.json'
with open(load_file, 'r') as f:
    data = js.load(f)
    print(data)

quietmode_data ={}
quiet_file ='quiet.json'
with open(quiet_file,'r') as f:
    quietmode_data = js.load(f)
    print(quietmode_data)

#to store which channel to post lfg requests to
lfg_channels = {}
lfg_file = 'lfg.json'
with open(lfg_file,'r')as f:
    lfg_channels = js.load(f)
    print(lfg_channels)

#word list
L=[]
#open and load list change later
with open ('db.db', 'rb') as F:
    L = list(pickle.load(F))
    #print(L)
    print("loaded file")
    F.close()

        
# #simple time
named_tuple = time.localtime() # get struct_time
time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)

#start logging
# logger = logging.getLogger('discord')
# logger.setLevel(logging.INFO)
# handler = logging.FileHandler(filename='discord.verbose.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

#test ping

@bot.command()
async def ping(ctx):
    message = await ctx.send("Pong")
    print("got command")

@bot.command()
async def restart(ctx):
    if ctx.message.author.id == 500150174925193246:
        await ctx.send("restarting....")
        os.system(r'python3 "/home/pi/Desktop/discord-multipourpous-bot/Main.py"')
    
@bot.command()
async def avatar(ctx, *,  avamember : discord.Member=None):
    if avamember == None:
        userAvatarUrl = (ctx.message.author).avatar_url
        embed = discord.Embed(color=0xdfa3ff,title = 'Avatar', description=ctx.author.mention)
    else:
        userAvatarUrl = avamember.avatar_url
        embed = discord.Embed(color=0xdfa3ff,title = 'Avatar', description=avamember.mention)
        
    embed.set_image(url = userAvatarUrl)
    await ctx.send(embed=embed)

#adding to db
@bot.command()
async def addword(ctx,arg):
    print("got command")
    message = await ctx.send("added word: "+arg)
    with open('scrapdb.db', 'wb') as F:
        # Dump the list to file
        L.append(str(arg))
        pickle.dump(L, F)
        print("data pickled.")
        print(L)
        F.close()

@bot.command()
async def viewdb(ctx):
    await ctx.send(str(L))

@bot.command()
async def rm(ctx,arg):
    #print(ctx.message.author.id)
    if ctx.message.author.id == 500150174925193246:
        print('yes')
        L.remove(arg)
        print(L)
        await ctx.send("removed word "+arg)

@bot.command()
async def add(ctx):
    if data.get(str(ctx.author.id)) == None:
        data[str(ctx.author.id)] = []
        data[str(ctx.author.id)].append({
        'points':0
        })
         #js.dump(data,load_file)
        print("added user: "+str(ctx.author.id))
        print(str(data[str(ctx.author.id)][0]['points'])) 
        await ctx.send("Welcome to Shimoneta Detector "+ctx.author.mention)
    else:
        await ctx.send("You are already added "+ctx.author.mention)

    #if ctx.message.author.id in data:
        #await ctx.send('User '+ctx.message.author.mention+" is already registered")
    
def hasAny (k, str):
    print(k)
    print(str)
    #print(list(map(lambda w: w == k, str.split())))
    print(list(map(lambda w: w == k,str(str))))
    #return any(list(map(lambda w: w == k, str.split())))
    return any(list(map(lambda w: w == k,str(str))))

#quiet mode   
@bot.command(pass_context=True)
async def quiet(ctx,*,opt=None):
    if quietmode_data.get(str(ctx.message.guild.id)) == None:
        quietmode_data[str(ctx.message.guild.id)] = []
        quietmode_data[str(ctx.message.guild.id)].append({
                    'quiet':False
                    })
        
    if opt == 'true' or opt == 'True':
        quietmode_data[str(ctx.message.guild.id)][0]["quiet"]=True
        await ctx.send("Quiet Mode enabled")

    if opt == 'false'or opt =='False':
        quietmode_data[str(ctx.message.guild.id)][0]["quiet"]=False
        await ctx.send("Quiet Mode disabled")

    if opt == None and (opt!='true' or opt !='false' or opt !='True' or opt != 'False'):
        embedVar = discord.Embed(
        title="!quiet", description="Can be invoked with !quiet with parameters true or false. used to turn off messaging every time it detects a word", color=0x336EFF
                )
        await ctx.send(embed = embedVar)


#score viewing
@bot.command(pass_context=True)
async def score(ctx):
    await ctx.send(ctx.message.author.mention +" has "+ str(data[str(ctx.message.author.id)][0]["points"]) +" Points")

#random shindann
@bot.command(pass_context=True)
async def shindan(ctx):
    url = 'https://shindanmaker.com/'+str(random.randint(10000,99999))
    r = requests.get(url)

    while r.status_code!=200:
        url = 'https://shindanmaker.com/'+str(random.randint(10000,99999))
        r = requests.get(url)

    await ctx.send(url+" requested by "+ctx.message.author.mention)


#message handler
@bot.event
async def on_message(message):

    #setting active to false so bot does not error
    if active.get(str(message.guild.id))==None:
        active[str(message.guild.id)] = []
        active[str(message.guild.id)].append({
            'status':False
            })
    
    if quietmode_data.get(str(message.guild.id))==None:
        quietmode_data[str(message.guild.id)] = []
        quietmode_data[str(message.guild.id)].append({
                'quiet':False
            })

    a= datetime.now().hour
    if a == 15:
        with open(load_file,'w') as f:
            js.dump(data, f)
            f.close()
            print(data)
        with open('db.db','wb')as g:
            pickle.dump(L,g)
        with open(quiet_file,'w') as f:
            js.dump(quietmode_data,f)
    #print("incoming message:")
    print(message.content)
    content = message.content.split()
    for word in content:
        for words in L:
            #print(words)
            if word == words and message.author != bot.user:
                print("contains a key word")
                print(message.author.id)
                print(data[str(message.author.id)])
                data[str(message.author.id)][0]["points"] +=1  
                if active[str(message.guild.id)][0] != 'Active' and quietmode_data[str(message.guild.id)][0]['quiet'] == False:
                    await message.channel.send("Detected word. word count currently "+str(data[str(message.author.id)][0]['points'])+" Message is: "+str(message.content)+" From: "+str(message.author))
    await bot.process_commands(message)





@bot.command()
async def backup(ctx):
    global data
    with open(load_file,'w') as f:
        js.dump(data, f)
        f.close()
        print(data)
    with open('db.db','wb')as g:
        pickle.dump(L,g)
    with open(quiet_file,'w') as f:
        js.dump(quietmode_data,f)
        print(quietmode_data)

    with open(lfg_file,'w')as f:
        js.dump(lfg_channels,f)
        print(lfg_channels)

@bot.command()
async def verify(ctx):
    with open('players.json','r') as f:
        j = js.load(f)
        await ctx.send(j)
        print(j)
    # if ('FOO' in message.content and message.author != bot.user):
        # global wordcount
        # wordcount+=1
        # await message.channel.send("Detected word. word count currently "+str(wordcount)+" Message is: "+str(message.content)+" From: "+str(message.author))
    # await bot.process_commands(message)
        
#     #log into simple logging
#     with open('simplelog','a', encoding="utf-8") as slog:
#         slog.write("Got message "+str(message.content)+" From "+str(message.author)+'\n')

#help


class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self,ctx):
        embed=discord.Embed(title="Help", description="Help Page for Shimoneta Detector", color=0xae00ff)
        embed.set_author(name="Shimoneta Detector", url="https://github.com/Yaurrdautia", icon_url="https://cdn.discordapp.com/attachments/845781070237401088/845781477908021278/Shimoneta_logo.png")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/845781070237401088/845781477908021278/Shimoneta_logo.png")
        embed.add_field(name="!help", value="displays the help screen.", inline=True)
        embed.add_field(name="!ping", value="checks if server is alive.", inline=False)
        embed.add_field(name="!addword", value="adds word to the wordlist. Wordlist is currently shared across all servers. (it will change soon)", inline=True)
        embed.add_field(name="!viewdb", value="command to display the database of words in the form of a list.", inline=True)
        embed.add_field(name="!add", value="the command used to add an user to the user database.", inline=True)
        embed.add_field(name="!quiet", value="(still under development) used to set if the bot sends you a message every time you say a word that is in the wordlist.", inline=True)
        embed.add_field(name="!join", value="makes the bot join the voice chat you currently are in", inline=True)
        embed.add_field(name="!pause", value="Makes the bot pause the music/video that is currently playing", inline=True)
        embed.add_field(name="!resume", value="Resumes the track you just paused.", inline=True)
        embed.add_field(name="!leave ", value="Makes the bot leave the voice chat.", inline=True)
        await ctx.send(embed=embed)
    print(embeds)
client.help_command = MyHelpCommand()

    

#music stuff--------------------------
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def search(cls, search, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def join(self,ctx):
        channel = bot.get_channel(ctx.author.voice.channel.id)
        await channel.connect()

    #takes a lot of space. so no
    #@commands.command()
    #async def play(self,ctx, *, url):
    #    async with ctx.typing():
    #        player = await YTDLSource.from_url(url, loop= bot.loop)
    #        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    #        await ctx.send('Now playing: {}'.format(player.title))
    @commands.command(pass_context = True)
    async def pause(self,ctx):
        await ctx.voice_client.pause()

    @commands.command(pass_context=True)
    async def resume(self,ctx):
        await ctx.voice_client.resume()

    @commands.command()
    async def leave(self,ctx):
        #channel = bot.get_channel(ctx.author.voice.channel.id)
        await ctx.voice_client.disconnect()


    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")
    
    @commands.command()
    async def play(self,ctx, *, searchterm):
        global queue
        #global vid_url
        #vid_url =''
        #print(searchterm)
        if ('youtube.com' in searchterm) or ('youtu.be' in searchterm):
            #print('NO')
            vid_url = searchterm
            #print(vid_url)
            try:
                queue[ctx.guild.id].append(vid_url)
            except:
                queue[ctx.guild.id] = [vid_url]

        #elif ('youtube.com' or 'youtu.be')not in searchterm:
        else:
            #print('YES')
            videosearch = VideosSearch(searchterm,limit=1)
            result = videosearch.result()
            #print(result)
            vid_url = result['result'][0]['link']
            #print(vid_url)
            try:
                queue[ctx.guild.id].append(vid_url)
            except:
                queue[ctx.guild.id] = [vid_url]
            

        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            #vid_url = 'https://www.youtube.com/watch?v=n1-Jjxh5RgY'
            player = await YTDLSource.from_url(vid_url, loop=bot.loop,stream=True)
            voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        
        #print("start stack trace here")
        #print(searchterm)
        #print(vid_url)
        videoInfo = Video.getInfo(vid_url, mode = ResultMode.dict)
        #print(vid_url)
        tn = videoInfo['thumbnails'][1]['url']
        title = videoInfo['title']
        embed = discord.Embed(color=0xb4eeb4,title = 'Music', description='**Now Playing: **'+title+'\n'+vid_url)
        embed.set_thumbnail(url=tn)
        await ctx.send(embed = embed)
        del(queue[ctx.guild.id][0])
        vid_url=''

#@commands.command()
#async def play(ctx, *, url):
#    async with ctx.typing():
#            player = await YTDLSource.from_url(url, loop=self.bot.loop)
#            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
#
#            await ctx.send('Now playing: {}'.format(player.title))
bot.add_cog(Music(bot))



class FFmpegPCMAudio2(discord.AudioSource):
    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
        stdin = None if not pipe else source
        args = [executable]
        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))
        args.append('-i')
        args.append('-' if pipe else source)
        args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning'))
        if isinstance(options, str):
            args.extend(shlex.split(options))
        args.append('pipe:1')
        self._process = None
        try:
            self._process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
            self._stdout = io.BytesIO(
                self._process.communicate(input=stdin)[0]
            )
        except FileNotFoundError:
            raise discord.ClientException(executable + ' was not found.') from None
        except subprocess.SubprocessError as exc:
            raise discord.ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(exc)) from exc
    def read(self):
        ret = self._stdout.read(Encoder.FRAME_SIZE)
        if len(ret) != Encoder.FRAME_SIZE:
            return b''
        return ret
    def cleanup(self):
        proc = self._process
        if proc is None:
            return
        proc.kill()
        if proc.poll() is None:
            proc.communicate()

        self._process = None




mp3_fp = io.BytesIO()


class tts(commands.Cog):
    global mp3_fp
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def shimo_start(self,ctx, domain ,lang:str):
        channel = ctx.author.voice.channel
        global channel_id
        channel_id = ctx.channel.id
        await channel.connect()
        #tts1 = gTTS('Started',domain,lang,False)
        #tts1.write_to_fp(mp3_fp)
        print(mp3_fp)
        server = ctx.message.guild
        voice = server.voice_client
        #voice.play(FFmpegPCMAudio('test.mp3', **FFMPEG_OPTS), after=lambda e: print('done', e))
        mp3_fp.seek(0)
        file = FFmpegPCMAudio2(mp3_fp.read(), pipe = True)
        voice.play(file)
        if data.get(str(ctx.author.id)) == None:
            active[str(ctx.guild.id)] = []
            active[str(ctx.guild.id)].append({
                'status':'Active'
            })
            active[str(ctx.guild.id)].append ({
                'domain':str(domain)
                })
            active[str(ctx.guild.id)].append ({
                'lang':str(lang)
                })
            print(active)
        else:
            active[str(ctx.guild.id)] = []
            active[str(ctx.guild.id)].append('Active')
            active[str(ctx.guild.id)].append (str(domain))
            active[str(ctx.guild.id)].append (str(lang))

    @commands.command()
    async def startdict(self,ctx):
        text_channel_id = ctx.guild.id
    
    @commands.command()
    async def end(self,ctx):
        channel = ctx.author.voice.channel.id
        del(active[str(ctx.guild.id)][0])
        del(active[str(ctx.guild.id)][1])
        await ctx.voice_client.disconnect()

    @commands.command()
    async def say(self,ctx,*,content):  
        print(active)
        if active[str(ctx.guild.id)][0] == 'Active':
            mp3_fp.flush()
            mp3_fp.seek(0)
            tts = gTTS(content,active[str(ctx.guild.id)][1],active[str(ctx.guild.id)][2],False)
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            file = FFmpegPCMAudio2(mp3_fp.read(), pipe = True)
            server = ctx.message.guild
            voice = server.voice_client
            voice.play(file)
            #mp3_fp.close()
            mp3_fp.flush()
            mp3_fp.seek(0)
        
        

bot.add_cog(tts(bot))

#@bot.event
#async def on_message(message):
lfg_chan = 743329302480814251
lfg_inv = "https://discord.gg/Y4VbBdBG8s"
lfg_guild = 500457407005327361



class lfg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #command to post link to server
    global lfg_chan
    @commands.command(pass_context = True)
    async def lfg(self,ctx):
        if ctx.guild.id != lfg_guild:
            embed = discord.Embed(color=0x483d8b,title = 'LFG', description="Please use This Server for LFG."+lfg_inv)
            await ctx.send(embed=embed)
        elif ctx.guild.id == lfg_guild:
            if ctx.channel.id != lfg_chan:
                embed = discord.Embed(color=0xb536f0,title = 'LFG', description="Please use the LFG channel.")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(color=0x00537a,title = 'LFG', description="Please use the recruit command.")
                await ctx.send(embed=embed)

    @commands.command(pass_context = True)
    async def setup(self,ctx,*, channel: discord.TextChannel=None):
        if channel == None:
            embed = discord.Embed(color=0xff7f50,title = 'LFG setup', description="You need to specify a channel.")
            await ctx.send(embed = embed)

        if lfg_channels.get(str(ctx.guild.id))==None:
            lfg_channels[str(ctx.message.guild.id)] = []
            lfg_channels[str(ctx.message.guild.id)].append({
                "channel_id":channel.id
                })
            embed = discord.Embed(color=0xff7f50,title = 'LFG setup finished', description="You lfg channel has been set to "+str(channel)+" all lfg posts will be posted here.")
            await ctx.send(embed =embed)
            #print(lfg_channels)
        else:
            lfg_channels[str(ctx.message.guild.id)][0]['channel_id'].append (channel.id)
            embed = discord.Embed(color=0xff7f50,title = 'LFG setup finished', description="You lfg channel has been changed to "+str(channel)+" all lfg posts will be posted here.")
            await ctx.send(embed = embed)
            

    #@commands.command(pass_context=True)
    #async def msg(self,ctx, *, msg:str):
    #    for guild in bot.guilds:
    #        await guild.text_channels[0].send(msg)

    @commands.command(pass_context = True)
    async def recruit(self,ctx,game_name:str, time:int ,amt_people:int,*,opt_message:str=""):
        print(lfg_channels)
        for channels in lfg_channels.values():
            print(channels[0]['channel_id'])
            channels = bot.get_channel(channels[0]['channel_id'])
            author = ctx.author.mention
            embed = discord.Embed(color=0x00AB9E,title = 'Recruiting '+str(amt_people), description=author +" is looking to play " + game_name +" within the next "+str(time)+" hours. "+author+" is recruiting "+str(amt_people)+" people. "+" Contact "+str(ctx.author)+" for more info "+ opt_message)
            await channels.send(embed=embed)
                    #embed = discord.Embed(color=0x00AB9E,title = 'Recruiting '+str(amt_people), description=author +" is looking to play " + game_name +"within the next "+str(time)+" hours. "+author+" is recruiting "+str(amt_people)+" people. "+ opt_message)
                    #await channel.send(embed=embed)

bot.add_cog(lfg(bot))
players = {}


#@bot.command()
#async def join(ctx):
#    channel = ctx.author.voice.channel
#    await channel.connect()

bot.run(TOKEN)

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

from youtube_dl.postprocessor import ffmpeg

#SETTING UP LOGGING
#add speech to text maybe?
#logging.basicConfig(level=logging.INFO)

#setting up simple logging
bot = commands.Bot(command_prefix='!')
queue = {}


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

#word list
L=[]
#open and load list change later
with open ('scrap.db', 'rb') as F:
    L = list(pickle.load(F))
    print(L)
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
        os.system(r'py "C:\Users\yutar_p8dg94\OneDrive\Desktop\programming\shimoneta detector\Main.py"')

    

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
async def quiet(ctx,opt=None):
    if data.get(str(ctx.message.guild.id)) == None:
        quietmode_data[str(ctx.message.guild.id)] = []
        quietmode_data[str(ctx.message.guild.id)].append({
                    'quiet':'False'
                    })
    if opt == None:
        embedVar = discord.Embed(
        title="!quiet", description="Can be invoked with !quiet with parameters true or false. used to turn off messaging every time it detects a word", color=0x336EFF
                )
        await ctx.send(embed = embedVar)
        
    if opt == 'true' or 'True':
        data[str(ctx.message.guild.id)][0]["quiet"] = 'True'

    if opt == 'false'or'False':
            data[str(ctx.message.guild.id)][0]["quiet"] = 'False'
    else:
        await ctx.send('quiet mode can not be '+opt+' please use True or False')



#message handler
@bot.event
async def on_message(message):
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
                if active[str(message.guild.id)][0] != 'Active':
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
        print(queue)
   
        if 'youtube.com' in searchterm:
            try:
                queue[ctx.guild.id].append(searchterm)
            except:
                queue[ctx.guild.id] = [searchterm]

        elif 'youtube.com' not in searchterm:
            results =search(searchterm, offset=1, mode = "dict", max_results=1).result()   
            url = results['search_result'][0]['link']
            try:
                queue[ctx.guild.id].append(url)
            except:
                queue[ctx.guild.id] = [url]
            

        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            player = await YTDLSource.from_url(queue[ctx.guild.id][0], loop=bot.loop,stream=True)
            
            voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send(f'**Now playing:** {player.title}')
        del(queue[ctx.guild.id][0])

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
active = {}

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
    

players = {}


#@bot.command()
#async def join(ctx):
#    channel = ctx.author.voice.channel
#    await channel.connect()






bot.run('TOKEN')
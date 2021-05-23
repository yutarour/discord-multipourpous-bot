import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import asyncio
from discord import client

bot = commands.Bot(command_prefix="!")

async def on_ready():
    print ("Ready")

@bot.command()
async def join(ctx):
    channel = bot.get_channel(ctx.author.voice.channel.id)
    await channel.connect()
    members = channel.members
    print(members)
    a=0
    for i in members:
        a +=1
    print(a)

bot.run("")

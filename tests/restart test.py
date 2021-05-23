import discord
import os
from discord.ext import commands


bot = commands.Bot(command_prefix='?')
# def restart_program():
#     python = os.system.executable
#     os.execl(python, python, * os.system.argv)

@bot.command()
async def ping(ctx):
    message = await ctx.send("Pong")
    print("got command")

bot.run('')

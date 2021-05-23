import json as js
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

data = {}

test = input("user input example: ")
points = int(input("points: "))

with open('players.json','r') as f:
    data = js.load(f)

data[test]={}
obj = {'points':points}
data.update(obj)
with open('players.json','w') as f:
    js.dump(data,f)


with open('players.json','r')as file:
    data = js.load(file)
    print(data)




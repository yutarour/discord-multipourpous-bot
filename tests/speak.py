from gtts import gTTS
from discord.ext import commands
import discord.utils

class tts:
    def __init__(self, bot):
        self.bot = bot

    @commands.command
    async def shimo_start(self,ctx,*,domain,lang):
        tts = gTTS('',domain,lang,False)

    @commands.command
    async def tts_join(self,ctx):
        channelid = discord.utils.get(ctx.guild.channels,ctx.message.author)
def setup(bot):
    bot.add_cog(tts(bot))


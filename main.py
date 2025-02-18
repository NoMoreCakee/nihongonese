import discord
import dotenv
import asyncio
import os

from discord.ext import commands
from discord import Embed, Color

dotenv.load_dotenv()

prefix = input("Enter a command prefix: ")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user}!")
    await bot.tree.sync()


# I don't want to make a new cog just for this command :3 - Cake

@bot.hybrid_command(name="starthere", description="Provides a list of beginner Japanese learning resources.")
async def starthere(interaction: discord.Interaction):
    embed = Embed(
        title="Beginner Resources",
        description="Here are some useful resources that will help you learn Japanese. \nYour absolute first step should be learning kana. After that, you could choose to learning everything separately or using a textbook/course.",
        color=Color.blue()
    )
    embed.add_field(
        name="Learn Kana",
        value="[Tofugu's Hiragana Guide](https://www.tofugu.com/japanese/learn-hiragana/)\n[Tofugu's Katakana Guide](https://www.tofugu.com/japanese/learn-katakana/)\n[Tofugu's Kana Quiz](https://kana-quiz.tofugu.com/)",
        inline=False
    )
    embed.add_field(
        name="Learn Kanji",
        value="[Remembering the Kanji](https://www.kanji.koohii.com/)\n[WaniKani](https://www.wanikani.com/) (Paid!)",
        inline=False
    )
    embed.add_field(
        name="Learn Grammar",
        value="[Cure Dolly's Organic Japanese Video Series](https://www.youtube.com/playlist?list=PLg9uYxuZf8x_A-vcqqyOFZu06WlhnypWj)\n[Bunpro](https://bunpro.jp/) (Paid!)",
        inline=False
    )
    embed.add_field(
        name="Vocabulary",
        value="[Setting Up Anki](https://www.youtube.com/watch?v=husCWKdxiRI)\n[Anki Deck - Kaishi 1.5k](https://ankiweb.net/shared/info/1196762551)",
        inline=False
    )
    embed.add_field(
        name="Textbooks",
        value="[ToKini Andy's Genki Video Series](https://www.youtube.com/playlist?list=PLA_RcUI8km1NMhiEebcbqdlcHv_2ngbO2)\n[Tobira Textbook](https://www.amazon.com/Tobira-Beginning-Japanese-Resources-Multilingual/dp/4874248705) (Paid!)",
        inline=False
    )
    embed.add_field(
        name="Podcasts",
        value="[Easy Japanese Podcast](https://www.youtube.com/playlist?list=PLyoFx8ILlVNG5_PrMj5t5otyqs8q8apOr)\n[Japanese for Beginners (Genki-Based)](https://www.youtube.com/playlist?list=PLUqu4MKiV5q_0_8JRUXVIJ-yuX1RNYJlF)",
        inline=False
    )
    await interaction.channel.send(embed=embed)

async def main():
    async with bot:
        await load_cogs()
        await bot.start(dotenv.get_key(".env", "API_KEY"))

asyncio.run(main())
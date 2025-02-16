import discord
import dotenv
import asyncio

from discord.ext import commands

dotenv.load_dotenv()

prefix = "::"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user}!")

async def main():
    async with bot:
        await bot.start(dotenv.get_key(".env", "API_KEY"))
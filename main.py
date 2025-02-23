import os
import asyncio
import discord
import dotenv
from discord.ext import commands

dotenv.load_dotenv()

prefix = input("Enter a command prefix: ")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

WELCOME_CHANNEL = int(dotenv.get_key('.env', 'CHANNEL_ID'))


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user}!")
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(e)
    else:
        print(f"Synced {len(synced)} slash command(s)")

@bot.event
async def on_member_join(member: discord.Member):
    channel=bot.get_channel(WELCOME_CHANNEL)

    if not channel:
        print("Channel not found")
        return

    embed=discord.Embed(title="New Member!", description=f"Welcome {member.mention} to Nihongonese! Nice to have you here!", color=discord.Color.blue())
    await channel.send(embed=embed)


async def main():
    async with bot:
        await load_cogs()
        await bot.start(dotenv.get_key(".env", "API_KEY"))


asyncio.run(main())
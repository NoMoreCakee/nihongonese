from discord.ext import commands
from discord import *

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def strip_id(user_id):
        if user_id[:2] == "<@" and user_id[-1] == ">": return user_id[2:-1]
        else: return user_id

    @commands.command()
    async def hello(self, ctx: commands.context.Context):
        await ctx.send("Hello, world!")

    @commands.command()
    async def kick(self, ctx: commands.context.Context, user_id, reason=None):
        """Allows for kicking a user"""
        user_id = self.strip_id(user_id)

        user = await ctx.guild.fetch_member(user_id)
        globalname = user.name

        try: await ctx.guild.kick(user, reason=reason)

        except Forbidden: await ctx.send("You don't have permission to kick this member.")
        except HTTPException: await ctx.send("Kicking failed. Possibly server error.")
        except NotFound: await ctx.send("User does not exist in the server.")

        else:
            if not reason: await ctx.send(f"Successfully kicked {globalname}.")
            else: await ctx.send(f"Successfully kicked {globalname} with the reason: \"{reason}\"")

    @commands.command()
    async def ban(self, ctx: commands.context.Context, user_id, reason=None):
        """Allows for banning a user"""
        user_id = self.strip_id(user_id)
        print(user_id)

        user = await ctx.guild.fetch_member(user_id)
        globalname = user.name
        print(user)

        try: await ctx.guild.ban(user, reason=reason)

        except Forbidden: await ctx.send("You don't have permission to ban this member.")
        except HTTPException: await ctx.send("Banning failed. Possibly server error.")
        except NotFound: await ctx.send("User does not exist in the server.")

        else:
            if not reason: await ctx.send(f"Successfully banned {globalname}.")
            else: await ctx.send(f"Successfully banned {globalname} with the reason: \"{reason}\"")

    @commands.command()
    async def unban(self, ctx: commands.context.Context, user_id):
        """Allows for unbanning a user"""
        user_id = self.strip_id(user_id)
        user = await self.bot.fetch_user(user_id)
        globalname = user.name

        try: await ctx.guild.unban(user)

        except NotFound: await ctx.send("User is either not banned or non-existent.")
        except Forbidden: await ctx.send("You don't have the permission to unban this member.")
        except HTTPException: await ctx.send("Unbanning failed. Possibly server error.")

        else: await ctx.send(f"Successfully unbanned {globalname}.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
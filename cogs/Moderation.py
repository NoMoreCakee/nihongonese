from discord.ext import commands
from discord import *

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def strip_id(user_id):
        if user_id[:2] == "<@" and user_id[-1] == ">": return user_id[2:-1]
        else: return user_id

    @commands.hybrid_command(name="hello", description="Checks bot connectivity.")
    async def hello(self, ctx: commands.context.Context):
        """Shows this message."""
        await ctx.send("Hello, world!")

    @commands.hybrid_command(name="kick", description="Kicks a user.")
    async def kick(self, ctx: commands.context.Context, user_id, reason=None):
        """Allows for kicking a user"""

        if not ctx.author.guild_permissions.kick_members:
            await ctx.send("You have no permissions to perform this.")
            return

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

    @commands.hybrid_command(name="ban", description="Bans a user.")
    async def ban(self, ctx: commands.context.Context, user_id, reason=None):
        """Allows for banning a user"""

        if not ctx.author.guild_permissions.ban_members:
            await ctx.send("You have no permissions to perform this.")
            return

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

    @commands.hybrid_command(name="unban", description="Unbans a user.")
    async def unban(self, ctx: commands.context.Context, user_id):
        """Allows for unbanning a user"""

        if not ctx.author.guild_permissions.ban_members:
            await ctx.send("You have no permissions to perform this.")
            return

        user_id = self.strip_id(user_id)
        user = await self.bot.fetch_user(user_id)
        globalname = user.name

        try: await ctx.guild.unban(user)

        except NotFound: await ctx.send("User is either not banned or non-existent.")
        except Forbidden: await ctx.send("You don't have the permission to unban this member.")
        except HTTPException: await ctx.send("Unbanning failed. Possibly server error.")

        else: await ctx.send(f"Successfully unbanned {globalname}.")

    @commands.hybrid_command(name="purge", description="Mass deletes up to a 100 messages. Messages must be sent within 2 weeks.")
    async def purge(self, ctx: commands.context.Context, amount: int):
        """Mass deletes up to a 100 messages. Messages must be sent within 2 weeks."""
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You have no permissions to perform this.")
            return
        
        if not amount:
            await ctx.send("Please provide an amount.")
            return
        
        if amount > 100:
            await ctx.send("Limit is 100 messages.\nDeleting 100 messages...")
            amount = 99

        await ctx.channel.purge(limit=amount)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
from discord.ext import commands
from discord import Embed, Forbidden, HTTPException, NotFound, Color
import time

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def strip_id(user_id):
        if user_id[:2] == "<@" and user_id[-1] == ">": return user_id[2:-1]
        else: return user_id

    @commands.hybrid_command(name="hello", description="Checks bot connectivity.")
    async def hello(self, ctx: commands.context.Context):
        await ctx.send(embed=Embed(title="Hello there!", description="I'm working!", color=Color.blue()))

    @commands.hybrid_command(name="kick", description="Kicks a user.")
    async def kick(self, ctx: commands.context.Context, user_id=None, reason=None):
        """Allows for kicking a user"""

        if not ctx.author.guild_permissions.kick_members:
            embed = Embed(
                title=":x: Error!",
                description="You have no permissions to perform this.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return

        if user_id is None:
            embed = Embed(
                title=":x: Error!",
                description="Please provide a user id or mention them.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return

        user_id = self.strip_id(user_id)

        user = await ctx.guild.fetch_member(user_id)
        globalname = user.name

        try: await ctx.guild.kick(user, reason=reason)

        except Forbidden:
            embed = Embed(
                title=":x: Error!",
                description="I don't have permission to kick this member.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
        except HTTPException:
            embed = Embed(
                title=":x: Error!",
                description="Failed to kick member. Possibly server error.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
        except NotFound: 
            embed = Embed(
                title=":x: Error!",
                description="User does not exist in the server.",
                color=Color.red()
            )
            await ctx.send(embed=embed)

        else:
            if not reason: 
                embed = Embed(
                    title=":white_check_mark: Success!",
                    description=f":hammer: Successfully kicked `{globalname}`.",
                    color=Color.green()
                )
                await ctx.send(embed=embed)
            else:
                embed = Embed(
                    title=":white_check_mark: Success!",
                    description=f":hammer: Successfully kicked `{globalname}` with the reason: \"{reason}\"",
                    color=Color.green()
                ) 
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="ban", description="Bans a user.")
    async def ban(self, ctx: commands.context.Context, user_id=None, reason=None):
        """Allows for banning a user"""

        if not ctx.author.guild_permissions.ban_members:
            embed = Embed(
                title=":x: Error!",
                description="You have no permissions to perform this.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if user_id is None:
            embed = Embed(
                title=":x: Error!",
                description="Please provide a user id or mention them.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return

        user_id = self.strip_id(user_id)

        user = await ctx.guild.fetch_member(user_id)
        globalname = user.name

        try: await ctx.guild.ban(user, reason=reason)

        except Forbidden:
            embed = Embed(
                title=":x: Error!",
                description="I don't have permission to ban this member.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
        except HTTPException:
            embed = Embed(
                title=":x: Error!",
                description="Failed to ban member. Possibly server error.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
        except NotFound: 
            embed = Embed(
                title=":x: Error!",
                description="User does not exist in the server.",
                color=Color.red()
            )
            await ctx.send(embed=embed)

        else:
            if not reason: 
                embed = Embed(
                    title=":white_check_mark: Success!",
                    description=f":hammer: Successfully banned `{globalname}`.",
                    color=Color.green()
                )
                await ctx.send(embed=embed)
            else:
                embed = Embed(
                    title=":white_check_mark: Success!",
                    description=f":hammer: Successfully banned `{globalname}` with the reason: \"{reason}\"",
                    color=Color.green()
                ) 
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="unban", description="Unbans a user.")
    async def unban(self, ctx: commands.context.Context, user_id=None):
        """Allows for unbanning a user"""

        if not ctx.author.guild_permissions.ban_members:
            embed = Embed(
                title=":x: Error!",
                description="You have no permissions to perform this.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if user_id is None:
            embed = Embed(
                title=":x: Error!",
                description="Please provide a user id or mention them.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return

        user_id = self.strip_id(user_id)
        user = await self.bot.fetch_user(user_id)
        globalname = user.name

        try: await ctx.guild.unban(user)

        except NotFound: 
            embed = Embed(
                title=":x: Error!",
                description="User is either not banned or non-existent.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
        except Forbidden:
            embed = Embed(
                title=":x: Error!",
                description="I don't have permission to unban this member.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
        except HTTPException:
            embed = Embed(
                title=":x: Error!",
                description="Failed to unban member. Possibly server error.",
                color=Color.red()
            )
            await ctx.send(embed=embed)

        else: 
            embed = Embed(
                title=":white_check_mark: Success!",
                description=f":hammer: Successfully unbanned `{globalname}`.",
                color=Color.green()
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="purge", description="Mass deletes up to a 100 messages. Messages must be sent within 2 weeks.")
    async def purge(self, ctx: commands.context.Context, amount: int):
        """Mass deletes up to a 100 messages. Messages must be sent within 2 weeks."""
        if not ctx.author.guild_permissions.manage_messages:
            embed = Embed(
                title=":x: Error!",
                description="You have no permissions to perform this.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if not amount:
            embed = Embed(
                title=":x: Error!",
                description="Please provide an amount.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if amount > 100:
            embed = Embed(
                title=":x: Error!",
                description="Limit is 100 messages.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return

        await ctx.channel.purge(limit=amount)
        
        embed = Embed(
            title=":white_check_mark: Success!",
            description=f"Successfully deleted {amount} messages.",
            color=Color.green()
        )
        msg = await ctx.send(embed=embed)
        time.sleep(3)
        await msg.delete()

async def setup(bot):
    await bot.add_cog(Moderation(bot))
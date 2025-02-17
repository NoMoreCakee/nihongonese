from discord.ext import commands
from discord import Color, Forbidden, HTTPException

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def listroles(self, ctx: commands.context.Context):
        roles = ctx.guild.roles
        roles_str = "\n".join(role.name for role in roles)
        await ctx.send(roles_str)

    # @commands.hybrid_command(name="addrole", description="Adds a role to the server.")
    @commands.command()
    async def addrole(self, ctx: commands.context.Context, rolename: str, color: str):
        print("breakpoint 1")
        try:
            dc_color = Color(int(color.lstrip("#"), 16))
            guild_role = await ctx.guild.create_role(name=rolename, color=dc_color)   

        except Forbidden:
            await ctx.send("You don't have the permission to perform this.")
        
        except HTTPException:
            await ctx.send("Failed to create role. Possibly server error.")

        except TypeError:
            await ctx.send("One of the given arguments is invalid.")

        else:
            await ctx.send(f"Successfully created {guild_role.name} role.")
        print("breakpoint 2")

async def setup(bot):
    await bot.add_cog(Roles(bot))
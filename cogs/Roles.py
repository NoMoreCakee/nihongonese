from discord.ext import commands
from discord import Embed, Forbidden, HTTPException, Color

class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed = Embed()

    @commands.hybrid_group(name="role")
    async def role(self, ctx: commands.context.Context):
        if ctx.invoked_subcommand is None:
            ctx.send("That argument doesn't exist for roles.")

    @role.command()
    async def list(self, ctx: commands.context.Context):
        roles = ctx.guild.roles
        roles_str = "\n".join(role.name for role in roles)
        self.embed.title = "Roles"
        self.embed.color = Color.default()
        self.embed.description = f"{roles_str}"
        await ctx.send(embed=self.embed)

    @role.command()
    async def add(self, ctx: commands.context.Context, rolename: str):
        try:
            guild_role = await ctx.guild.create_role(name=rolename)   

        except Forbidden:
            self.embed.title = ":x: Error!"
            self.embed.description = "I don't have the permission to perform this."
            self.embed.color = Color.red()
            await ctx.send(embed=self.embed)
        
        except HTTPException:
            self.embed.title = ":x: Error!"
            self.embed.description = "Failed to create role. Possibly server error."
            self.embed.color = Color.red()
            await ctx.send(embed=self.embed)

        except TypeError:
            self.embed.title = ":x: Error!"
            self.embed.description = "One of the given arguments is invalid."
            self.embed.color = Color.red()
            await ctx.send(embed=self.embed)

        else:
            self.embed.title = ":white_check_mark: Success!"
            self.embed.description = f"Successfully created {guild_role.name} role."
            self.embed.color = Color.green()
            await ctx.send(embed=self.embed)

    @role.command()
    async def remove(self, ctx: commands.context.Context, role_name: str=None):

        roles = ctx.guild.roles
        if role_name is None:
            self.embed.title = ":x: Error!"
            self.embed.description = "The provided input is invalid."
            self.embed.color = Color.red()
            await ctx.send(embed=self.embed)
            return

        found = False

        for r in roles:
            if r.name == role_name:
                found = True
                try: 
                    await r.delete()
                except Forbidden:
                    self.embed.title = ":x: Error!"
                    self.embed.description = "I don't have permission to perform this."
                    await ctx.send(embed=self.embed)
                except HTTPException:
                    self.embed.title = ":x: Error!"
                    self.embed.description = "Failed to remove role. Possibly server error."
                    await ctx.send(embed=self.embed)
                else:
                    self.embed.title = ":white_check_mark: Success!"
                    self.embed.color = Color.green()
                    self.embed.description = ":wastebasket: Successfully deleted role."
                    await ctx.send(embed=self.embed)
                return

        if not found:
            self.embed.title = ":x: Error!"
            self.embed.color = Color.red()
            self.embed.description = "Role not found."
            await ctx.send(embed=self.embed) 

async def setup(bot):
    await bot.add_cog(Roles(bot))
from discord.ext import commands
from discord import Embed, Forbidden, HTTPException, Color, Role

class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_group(name="role")
    async def role(self, ctx: commands.context.Context):
        if ctx.invoked_subcommand is None:
            self.embed.title = ":x: Error!"
            self.embed.description = "Invalid argument, if any."
            self.embed.color = Color.red()
            await ctx.send(embed=self.embed)

    @role.command()
    async def list(self, ctx: commands.context.Context):
        """Allows for listing roles."""

        if not ctx.author.guild_permissions.manage_roles:
            embed = Embed(
                title=":x: Error!",
                description="You don't have the permission to manage roles.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return

        roles = ctx.guild.roles
        roles_str = "\n".join(role.name for role in roles)

        embed = Embed(
            title="Roles",
            description=f"{roles_str}",
            color=Color.blue()
        )

        await ctx.send(embed=embed)

    @role.command()
    async def add(self, ctx: commands.context.Context, *, rolename: str=None):
        """Allows for creating a role."""

        if not ctx.author.guild_permissions.manage_roles:
            embed = Embed(
                title=":x: Error!",
                description="You don't have the permission to manage roles.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return

        if rolename is None:
            embed = Embed(
            title=":x: Error!",
            description="Please provide a name for the role.",
            color=Color.red()
            )
        
            await ctx.send(embed=embed)
            return

        try:
            guild_role = await ctx.guild.create_role(name=rolename)   

        except Forbidden:
            embed = Embed(
            title=":x: Error!",
            description="I don't have the permission to perform this.",
            color=Color.red()
            )
            await ctx.send(embed=embed)
        
        except HTTPException:

            embed = Embed(
            title=":x: Error!",
            description="Failed to create role. Possibly server error.",
            color=Color.red()
            )
            await ctx.send(embed=embed)

        except TypeError:

            embed = Embed(
            title=":x: Error!",
            description="One of the given arguments is invalid.",
            color=Color.red()
            )
            await ctx.send(embed=embed)

        else:

            embed = Embed(
            title=":white_check_mark: Success!",
            description=f"Successfully created {guild_role.name} role.",
            color=Color.green()
            )
            await ctx.send(embed=embed)

    @role.command()
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx: commands.Context, *, role_name: str):
        """Allows for removing a role."""

        if not ctx.author.guild_permissions.manage_roles:
            embed = Embed(
                title=":x: Error!",
                description="You don't have the permission to manage roles.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return

        if role_name is None:
            embed = Embed(
                title=":x: Error!",
                description="Please provide a role to delete.",
                color=Color.red()
            )
            await ctx.send(embed=embed)

        async def delete_role(ctx: commands.context.Context, role_to_delete: Role):
            try:
                    await role_to_delete.delete()
                
            except Forbidden:
                embed = Embed(
                    title=":x: Error!",
                    description="I don't have permission to perform this.",
                    color=Color.red()
                )
                

            except HTTPException:
                embed = Embed(
                    title=":x: Error!",
                    description="Failed to remove role. Possibly server error.",
                    color=Color.red()
                )

            else:
                embed = Embed(
                    title=":white_check_mark: Success!",
                    description=f":wastebasket: Successfully deleted `{role_to_delete.name}` role.",
                    color=Color.green()
                )

            await ctx.send(embed=embed)
                

        if not ctx.guild.me.guild_permissions.manage_roles:
            embed = Embed(
                title=":x: Error!",
                description="I don't have permission to manage roles.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        roles_to_delete = [r for r in ctx.guild.roles if r.name.lower() == role_name.lower()] or None

        if roles_to_delete is None:
            embed = Embed(
                title=":x: Error!",
                description=f"No role named `{role_name.lower()}` found.",
                color=Color.red()
            )
            await ctx.send(embed=embed)
            return

        elif type(roles_to_delete) == list:
            for role_to_delete in roles_to_delete:
                await delete_role(ctx, role_to_delete)

        else:
            await delete_role(ctx, roles_to_delete)

async def setup(bot):
    await bot.add_cog(Roles(bot))
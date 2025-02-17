import discord
from discord.ext import commands, tasks
from discord import app_commands

class ClubCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_empty_clubs.start()  # Start the auto-cleanup task

    def get_overwrites(self, guild: discord.Guild, role: discord.Role, owner: discord.Member):
        """Define permissions for club channels."""
        return {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True),
            owner: discord.PermissionOverwrite(administrator=True)
        }

    @commands.hybrid_group(name="club", with_app_command=True, description="Manage clubs (create, delete, join, leave, list)")
    async def club(self, ctx):
        """Base club management command"""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=self.error_embed("Use `/club create <name>`, `/club delete <name>`, `/club join <name>`, `/club leave <name>`, `/club list`."))

    @club.command(name="create", description="Create a new club with a role and channels")
    async def create(self, ctx, club_name: str):
        """Create a club with an owner, role, and private channels."""
        guild = ctx.guild

        if discord.utils.get(guild.roles, name=club_name):
            await ctx.send(embed=self.error_embed(f"A club named **{club_name}** already exists!"))
            return

        club_role = await guild.create_role(name=club_name, mentionable=True)
        overwrites = self.get_overwrites(guild, club_role, ctx.author)
        club_category = await guild.create_category(club_name, overwrites=overwrites)

        text_channel = await guild.create_text_channel(f"{club_name.lower()}-chat", category=club_category)
        voice_channel = await guild.create_voice_channel(f"{club_name.lower()}-voice", category=club_category)

        await ctx.author.add_roles(club_role)

        embed = discord.Embed(
            title="🏆 Club Created!",
            description=f"**Owner:** {ctx.author.mention}\n"
                        f"**Role:** {club_role.mention}\n"
                        f"**Text Channel:** {text_channel.mention}\n"
                        f"**Voice Channel:** {voice_channel.name}",
            color=discord.Color.green()
        ).set_footer(text="Club system by Your Bot")
        await ctx.send(embed=embed)

    @club.command(name="delete", description="Delete an existing club")
    async def delete(self, ctx, club_name: str):
        """Delete a club (role + channels)"""
        guild = ctx.guild
        club_role = discord.utils.get(guild.roles, name=club_name)
        club_category = discord.utils.get(guild.categories, name=club_name)

        if not club_role:
            await ctx.send(embed=self.error_embed(f"No club found with the name **{club_name}**."))
            return

        if club_category:
            for channel in club_category.channels:
                await channel.delete()
            await club_category.delete()

        await club_role.delete()
        await ctx.send(embed=self.success_embed(f"🗑️ Club **{club_name}** has been deleted."))

    @club.command(name="join", description="Join an existing club")
    async def join(self, ctx, club_name: str):
        """Join a club and get access"""
        guild = ctx.guild
        club_role = discord.utils.get(guild.roles, name=club_name)

        if not club_role:
            await ctx.send(embed=self.error_embed(f"❌ No club found with the name **{club_name}**."))
            return

        if club_role in ctx.author.roles:
            await ctx.send(embed=self.error_embed(f"⚠️ You are already a member of **{club_name}**!"))
            return

        await ctx.author.add_roles(club_role)

        # Send welcome message in club chat
        club_category = discord.utils.get(guild.categories, name=club_name)
        if club_category:
            text_channel = discord.utils.get(club_category.text_channels, name=f"{club_name.lower()}-chat")
            if text_channel:
                await text_channel.send(f"🎉 Welcome {ctx.author.mention} to **{club_name}**!")

        await ctx.send(embed=self.success_embed(f"✅ You have joined **{club_name}**!"))

    @club.command(name="leave", description="Leave a club")
    async def leave(self, ctx, club_name: str):
        """Leave a club and lose access"""
        guild = ctx.guild
        club_role = discord.utils.get(guild.roles, name=club_name)

        if not club_role:
            await ctx.send(embed=self.error_embed(f"❌ No club found with the name **{club_name}**."))
            return

        if club_role not in ctx.author.roles:
            await ctx.send(embed=self.error_embed(f"⚠️ You are not a member of **{club_name}**!"))
            return

        await ctx.author.remove_roles(club_role)
        await ctx.send(embed=self.success_embed(f"🚪 You have left **{club_name}**."))

    @club.command(name="list", description="List all existing clubs")
    async def list(self, ctx):
        """List all clubs with their associated roles"""
        guild = ctx.guild
        club_roles = [role for role in guild.roles if role.name in [c.name for c in guild.categories]]

        if not club_roles:
            await ctx.send(embed=self.error_embed("There are no clubs yet!"))
            return

        embed = discord.Embed(
            title="📜 Active Clubs",
            description="\n".join([f"🏆 **{role.name}**" for role in club_roles]),
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @tasks.loop(hours=1)
    async def cleanup_empty_clubs(self):
        """Auto-delete clubs with 0 members"""
        for guild in self.bot.guilds:
            for role in guild.roles:
                if discord.utils.get(guild.categories, name=role.name):  # Check if role is a club
                    if len(role.members) == 0:
                        category = discord.utils.get(guild.categories, name=role.name)
                        if category:
                            for channel in category.channels:
                                await channel.delete()
                            await category.delete()
                        await role.delete()

    def error_embed(self, message: str):
        """Return an error embed."""
        return discord.Embed(title="❌ Error", description=message, color=discord.Color.red())

    def success_embed(self, message: str):
        """Return a success embed."""
        return discord.Embed(title="✅ Success", description=message, color=discord.Color.green())

async def setup(bot):
    await bot.add_cog(ClubCog(bot))

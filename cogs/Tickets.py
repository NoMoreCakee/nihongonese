import dotenv
import discord
from discord.ext import commands
from discord import Color, Embed, Forbidden, HTTPException, TextChannel, PermissionOverwrite, Role, ButtonStyle, utils, Interaction
from discord.ui import Button, View

import asyncio

dotenv.load_dotenv()

class TicketMessageView(View):
    def __init__(self, ctx: commands.Context, ticket_author: discord.Member):
        super().__init__()
        self.ctx = ctx
        self.ticket_author = ticket_author

    def get_role(self, role_name):
        return utils.get(self.ctx.guild.roles, name=role_name)

    async def interaction_check(self, interaction: Interaction):
        if not self.get_role('Ticket') in interaction.user.roles or self.ticket_author != interaction.user:
            await interaction.response.send_message("Only the creator of the ticket or users with the Ticket role are able to close tickets.")
            return False
        return True

    async def on_timeout(self):
        return await self.message.edit(view=None)

    async def send(self, channel: TextChannel):
        self.ticket_channel = channel
        self.message = await channel.send(embed=self.create_embed(), view=self)

    def create_embed(self):
        return Embed(
            title=":white_check_mark: Success!",
            description="Your ticket is successfully created! You can now talk with the staff team privately.",
            color=Color.green()
        )

    @discord.ui.button(label="Close Ticket", style=ButtonStyle.danger)
    async def close_ticket(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        await self.ticket_channel.send(embed=Embed(
            title=":information_source: Closing Ticket!",
            description="This channel will be deleted in 5 seconds...",
            color=Color.blue()
        ))

        await asyncio.sleep(5)

        await self.ticket_channel.delete()

class TicketsView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.ticket_category: discord.CategoryChannel = None

    async def interaction_check(self, interaction: Interaction):
        if not self.verified_role in interaction.user.roles:
            await interaction.response.send_message("Only verified members can request a ticket. If you have problem getting verified, please DM a staff member.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        await self.message.edit(view=None)

    async def send(self, role: Role, channel: TextChannel):
        self.verified_role = role
        self.message = await channel.send(embed=self.create_embed(), view=self)

    def create_embed(self):
        return Embed(
            title="Tickets",
            description="You can create a ticket to create a channel directly connecting you to the staff team where you can propose your suggestions or report users.",
            color=Color.blue()
        )

    @discord.ui.button(label="Create Ticket", style=ButtonStyle.primary)
    async def create_ticket(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        new_ticket_channel: discord.TextChannel = await self.ticket_category.create_text_channel(name=f"ticket-{interaction.user.name}")


        ticket_view = TicketMessageView(ctx=self.ctx, ticket_author=interaction.user)
        await ticket_view.send(new_ticket_channel)


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed: Embed = Embed()
        self.ticket_count = 0

    @commands.hybrid_group(name="tickets")
    async def tickets(self, ctx: commands.Context):
        embed = Embed()

        if not ctx.invoked_subcommand:
            embed.title = ":x: Error!"
            embed.description = "Invalid argument, if any."
            embed.color = Color.red()
            await ctx.send(embed=embed)
        return
    
    @tickets.command(name="create")
    async def create(self, ctx: commands.Context):
        embed = Embed()

        if not ctx.author.guild_permissions.manage_channels:
            embed.title = ":x: Error!"
            embed.description = "You don't have the permission to perform this."
            embed.color = Color.red()
            await ctx.send(embed=embed)
            return
        
        ticket_role = utils.get(ctx.guild.roles, name="Ticket")

        if not ticket_role:
            await ctx.send(
                embed=Embed(
                    title=":x: Error!",
                    description="The role `Ticket` is not found. Please create it in order to create tickets."
                )
            )
            return
        
        try: 
            category = await ctx.guild.create_category(name="Tickets")

        except Forbidden:
            await ctx.send(
                embed=Embed(
                    title=":x: Error!",
                    description="I don't have permission to create channels and categories."
                )
            )

        except TypeError:
            await ctx.send(
                embed=Embed(
                    title=":x: Error!",
                    description="A Type Error happened."
                )
            )

        except HTTPException:
            await ctx.send(
                embed=Embed(
                    title=":x: Error!",
                    description="Couldn't create category. Possibly server error."
                )
            )
        
        else:
            await category.set_permissions(ctx.guild.get_member(self.bot.user.id), manage_channels=True, send_messages=True, read_messages=True, manage_messages=True)

            await ctx.send(
                embed=Embed(
                    title=":information_source: Info!",
                    description="Ticket category created. Not done yet...",
                    color=Color.blue()
                )
            )

            verified_role: Role = ctx.guild.get_role(int(dotenv.get_key('.env', "VERIFIED_ROLE")))

            if not verified_role:
                await ctx.send(
                    embed=Embed(
                        title=":x: Error!",
                        description="Verified role not found in server.",
                        color=Color.red()
                    )
                )
                return

            overwrites = {
                ctx.guild.default_role: PermissionOverwrite(read_messages=False),
                verified_role: PermissionOverwrite(read_messages=True),
            }


            ticket_channel: TextChannel = await category.create_text_channel(name="tickets", overwrites=overwrites)

            if not ticket_channel:
                await ctx.send(
                    embed=Embed(
                        title=":x: Error!",
                        description="Failed to create tickets channel.",
                        color=Color.red()
                    )
                )
                return

            await ctx.send(
                embed=Embed(
                    title=":information_source: Info!",
                    description="Tickets channel set up. Almost done...",
                    color=Color.blue()
                )
            )

            ticket_view = TicketsView(ctx=ctx)
            print("ticket view")
            await ticket_view.send(verified_role, ticket_channel)
            ticket_view.ticket_category = category
            print("ticket sent")

            await ctx.send(
                embed=Embed(
                    title=":white_check_mark: Success!",
                    description="Tickets are successfully set up.",
                    color=Color.green()
                )
            )
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
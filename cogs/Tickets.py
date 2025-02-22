import dotenv
import discord
from discord.ext import commands
from discord import Color, Embed, Forbidden, HTTPException, TextChannel, PermissionOverwrite, Role, ButtonStyle, Message, utils, Interaction
from discord.ui import Button, View

dotenv.load_dotenv()

class TicketsView():
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx

    async def interaction_check(self, interaction: Interaction):
        if not self.verified_role in interaction.user.roles:
            interaction.response.send_message("Only verified members can request a ticket. If you have problem getting verified, please DM a staff member.")
            return False
        return True
    
    async def on_timeout(self):
        await self.message.edit(view=None)

    async def send(self):
        self.verified_role = await utils.get(self.ctx.guild.roles, name="Verified")
        print(self.verified_role)
        self.message = await self.ctx.send(embed=self.create_embed(), view=self)

    def create_embed(self):
        return Embed(
            title="Tickets",
            description="You can create a ticket to create a channel directly connecting you to the staff team where you can propose your suggestions or report users.",
            color=Color.blue()
        )

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary)
    async def create_ticket(self, interaction: Interaction, button: discord.ui.Button, category: discord.CategoryChannel):
        await interaction.response.defer()
        await category.create_text_channel(name=f"ticket-{interaction.user.name}")

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
            await ctx.send(embed=Embed(
                title=":x: Error!",
                description="The role `Ticket` is not found. Please create it in order to create tickets."
            ))
            return
        
        try: 
            category = await ctx.guild.create_category(name="Tickets")

        except Forbidden: ctx.send(embed=Embed(title=":x: Error!", description="I don't have permission to create channels and categories."))
        except TypeError: ctx.send(embed=Embed(title=":x: Error!", description="A Type Error happened."))
        except HTTPException: ctx.send(embed=Embed(title=":x: Error!", description="Couldn't create category. Possibly server error."))
        
        else:
            await category.set_permissions(ctx.guild.get_member(self.bot.user.id), manage_channels=True, send_messages=True, read_messages=True, manage_messages=True)

            await ctx.send(embed=Embed(
                title=":information_source: Info!",
                description="Ticket category created. Not done yet...",
                color=Color.blue()
            ))

            verified_role: Role = ctx.guild.get_role(int(dotenv.get_key('.env', "VERIFIED_ROLE")))

            if not verified_role:
                await ctx.send(embed=Embed(
                    title=":x: Error!",
                    description="Verified role not found in server.",
                    color=Color.red()
                ))
                return

            overwrites = {
                ctx.guild.default_role: PermissionOverwrite(read_messages=False),
                verified_role: PermissionOverwrite(read_messages=True),
            }


            ticket_channel: TextChannel = await category.create_text_channel(name="tickets", overwrites=overwrites)

            if not ticket_channel:
                await ctx.send(embed=Embed(
                    title=":x: Error!",
                    description="Failed to create tickets channel.",
                    color=Color.red()
                ))
                return

            await ctx.send(embed=Embed(
                title=":information_source: Info!",
                description="Tickets channel set up. Almost done...",
                color=Color.blue()
            ))

            ticket_view = TicketsView(ctx=ctx)
            print("ticket view")
            await ticket_view.send()
            print("ticket sent")
            await ticket_view.create_ticket()
            print("ticket created")

    
async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
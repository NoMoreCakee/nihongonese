from discord.ext import commands
from discord import Embed, Forbidden, HTTPException, NotFound, Color
import time


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def strip_id(user_id):
        return user_id.strip("<@!") if user_id else None

    async def send_embed(self, ctx, title, description, color):
        await ctx.send(embed=Embed(title=title, description=description, color=color))

    async def perform_action(self, ctx, action, action_name, user_id, reason=None):
        if not getattr(ctx.author.guild_permissions, f"{action}_members", False):
            return await self.send_embed(ctx, ":x: Error!", "You don't have permission to perform this action.",
                                         Color.red())

        if not user_id:
            return await self.send_embed(ctx, ":x: Error!", "Please provide a user ID or mention them.", Color.red())

        user_id = self.strip_id(user_id)
        try:
            user = await ctx.guild.fetch_member(user_id) if action != "unban" else await self.bot.fetch_user(user_id)
            globalname = user.name

            if action == "unban":
                await ctx.guild.unban(user)
            else:
                await getattr(ctx.guild, action)(user, reason=reason)

            success_msg = f":hammer: Successfully {action_name} `{globalname}`" + (f' for "{reason}"' if reason else "")
            await self.send_embed(ctx, ":white_check_mark: Success!", success_msg, Color.green())

        except Forbidden:
            await self.send_embed(ctx, ":x: Error!", f"I don't have permission to {action} this member.",
                                  Color.red())
        except NotFound:
            await self.send_embed(ctx, ":x: Error!", "User not found or does not exist in the server.", Color.red())
        except HTTPException:
            await self.send_embed(ctx, ":x: Error!", f"Failed to {action} the member. Possibly a server error.",
                                  Color.red())

    @commands.hybrid_command(name="hello", description="Checks bot connectivity.")
    async def hello(self, ctx: commands.Context):
        await self.send_embed(ctx, "Hello there!", "I'm working!", Color.blue())

    @commands.hybrid_command(name="kick", description="Kicks a user.")
    async def kick(self, ctx: commands.Context, user_id=None, reason=None):
        await self.perform_action(ctx, "kick", "kicked", user_id, reason)

    @commands.hybrid_command(name="ban", description="Bans a user.")
    async def ban(self, ctx: commands.Context, user_id=None, reason=None):
        await self.perform_action(ctx, "ban", "banned", user_id, reason)

    @commands.hybrid_command(name="unban", description="Unbans a user.")
    async def unban(self, ctx: commands.Context, user_id=None):
        await self.perform_action(ctx, "unban", "unbanned", user_id)

    @commands.hybrid_command(name="purge", description="Mass deletes up to 100 messages.")
    async def purge(self, ctx: commands.Context, amount: int):
        if not ctx.author.guild_permissions.manage_messages:
            return await self.send_embed(ctx, ":x: Error!", "You don't have permission to perform this action.",
                                         Color.red())

        if not amount or amount > 100:
            return await self.send_embed(ctx, ":x: Error!", "Please provide a valid amount (1-100).", Color.red())

        await ctx.channel.purge(limit=amount)
        msg = await self.send_embed(ctx, ":white_check_mark: Success!", f"Successfully deleted {amount} messages.",
                                    Color.green())
        time.sleep(3)
        await msg.delete()


async def setup(bot):
    await bot.add_cog(Moderation(bot))
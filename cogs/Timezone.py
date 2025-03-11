import datetime
import discord
from discord.ext import commands


def test():
    UTC.format="%m/%d/%Y %I:%M %p"
    print(UTC)
    print(UTC-4)
    print(UTC+"5:30")


class UTC(datetime.tzinfo):
    _utcoffset = datetime.timedelta(0)
    _dst = _utcoffset

    def __init__(self, format=""):
        self.format = format

    def now(self):
        return datetime.datetime.now(tz=self)

    def setdelta(self, time):
        if isinstance(time, str):
            h, m = time.split(":") if ":" in time else (time, 0)
            return datetime.timedelta(hours=int(h), minutes=int(m))
        return datetime.timedelta(hours=time)

    def __add__(self, time):
        offset = self.setdelta(time)
        if not self.format:
            return self.now() + offset
        return (self.now() + offset).strftime(self.format)

    def __sub__(self, time):
        offset = self.setdelta(time)
        if not self.format:
            return self.now() - offset
        return (self.now() - offset).strftime(self.format)

    def __str__(self):
        if not self.format:
            return str(self.now())
        return self.now().strftime(self.format)

    def utcoffset(self, dt):
        return self._utcoffset

    def dst(self, dt):
        return self._dst


class TimeZone(commands.Cog):
    # TODO - tidy up
    times = {} # TODO - convert to database
    utc = UTC(format="%m/%d/%Y %I:%M %p")

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="time", description="Sets a UTC timezone")
    async def time(self, ctx: commands.context):
        # TODO - add embeds
        if not ctx.invoked_subcommand:
            await ctx.reply(f"Do `{self.bot.command_prefix(self.bot, "")[-1]}help time` for list of commands")

    @time.command(name="set", description="Sets a time")
    async def _set(self, ctx: commands.context, arg: str):
        # TODO - add embeds
        self.times[ctx.author.id] = arg
        await ctx.reply(f"Timezone of `UTC{'+' if int(arg) > 0 else '-'}{arg.strip('-+')}` for user {ctx.author} has been set successfully. Do `{self.bot.command_prefix(self.bot, "")[-1]}time get` to get the current time.")

    @time.command(description="Gets an existing time")
    async def get(self, ctx: commands.context, arg: str = ""):
        # TODO - add embeds
        if arg:
            user_id = self.bot.get_cog("Moderation").strip_id(arg)
            user = await ctx.guild.fetch_member(user_id)
            offset = self.times.get(user_id)

        else:
            user_id = ctx.author.id
            user = ctx.author
            offset = self.times.get(user_id)

        if not self.is_validated(user_id):
            await ctx.reply(f"Must have a time set before viewing others' time.")
            
        else:
            if offset:
                await ctx.reply(f"Displaying time `{self.utc+offset}` for {user}")

            else:
                await ctx.reply(f"No time set for {user}.")
    
    @time.command(description="Gets all user's times")
    async def all(self, ctx):
        # TODO - better embeds
        if self.is_validated(ctx.author.id):
            data = {f"<@!{k}>": f"{self.utc+v}" for k, v in self.times.items()}
            await ctx.send(embed=self.create_embed(data))
    
    @time.command(description="Removes a user's time")
    async def remove(self, ctx, arg=""):
        if arg:
            # TODO - only admins can remove time from other members
            user_id = self.bot.get_cog("Moderation").strip_id(arg)
            self.times.pop(user_id, None)
            await ctx.reply("Time has been removed")

        else:
            if self.is_validated(ctx.author.id):
                self.times.pop(ctx.author.id, None)
                await ctx.reply("Time has been removed")
    
    def create_embed(self, data: dict) -> discord.Embed:
        embed = discord.Embed(title="All users", colour=discord.Colour.random())
        for k, v in data.items():
            embed.add_field(name="Time", value=f"{k}, {v}", inline=False)
        return embed
    
    def is_validated(self, user_id):
        return user_id in self.times


async def setup(bot):
    await bot.add_cog(TimeZone(bot))


if __name__ == "__main__":
    UTC = UTC()
    test()
import datetime
import discord
from discord.ext import commands


def test():
    UTC.format="%d/%m/%Y %I:%M%p"
    print(UTC-4)


class UTC(datetime.tzinfo):
    _utcoffset = datetime.timedelta(0)
    _dst = _utcoffset

    def __init__(self, format=""):
        self.format = format

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

    def now(self):
        return datetime.datetime.now(tz=self)

    def setdelta(self, time):
        if isinstance(time, str):
            h, m = time.split(":") if ":" in time else (time, 0)
            return datetime.timedelta(hours=int(h), minutes=int(m))
        return datetime.timedelta(hours=time)


class TimeZone(commands.Cog):
    members = {}
    utc = UTC(format="%d/%m/%Y %I:%M%p")

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="timezone", with_app_command=True, description="timezones idk")
    async def timezone(self, ctx: commands.context):
        if not ctx.invoked_subcommand:
            await ctx.reply("Do `help timezone` for list of commands")

    @timezone.command(name="set", description="Sets a timezone")
    async def _set(self, ctx: commands.context, arg: str):
        time = self.utc+arg
        self.members[ctx.author] = arg
        await ctx.reply(f"Timezone of `UTC{arg}` {time} has been set successfully. Do `timezone get` to get the current time")

    @timezone.command(name="get", description="Gets an existing timezone")
    async def _get(self, ctx: commands.context, arg: str = ""):
        if not arg:
            offset = self.members.get(ctx.author)
        else:
            offset = self.members.get(arg) # TODO - parse "arg" for the ctx.author equivalent

        if offset:
            await ctx.reply(self.utc+offset)
        else:
            await ctx.reply("No timezone set")



async def setup(bot):
    await bot.add_cog(TimeZone(bot))


if __name__ == "__main__":
    UTC = UTC()
    test()
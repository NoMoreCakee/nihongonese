import sys
import json
import re
import traceback

import discord
from discord.ext import commands
from jisho_api.word import Word
from jisho_api.kanji import Kanji
from jisho_api.sentence import Sentence
from jisho_api.tokenize import Tokens

URL = "https://jisho.org/search/"


def test():
    # test to display how the text will be formatted on discord
    all_cmds = ("word", "kanji", "examples", "token")
    while (cmd:=input(f"Enter command option from {all_cmds}: ").lower()) in all_cmds:
        while (text:=input(f"Enter {cmd} to search for or (b: back): ").lower()) != "b":
            print(f"<------------{cmd.capitalize()} search for {text}------------>")
            for result in getattr(Jisho, f"{cmd.lower()}_search")(text):
                print(result)
                print("--end--")


class PageView(discord.ui.View):
    def __init__(self, ctx: commands.context, arg: str, data: list, *, timeout: int = 180):
        super().__init__(timeout=timeout)

        self.current_page = 1
        self.sep = 1

        self.ctx = ctx
        self.arg = arg

        self.data = data
        self.invoked_command = ctx.invoked_with
    
    async def interaction_check(self, interaction: discord.interactions) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Only the author of this command can perform this action.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self) -> None:
        await self.message.edit(view=None)

    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("I could not find member '{error.argument}'. Please try again", ephemeral=True)

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"'{error.param.name}' is a required argument.", ephemeral=True)

        else:
            print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def send(self) -> None:
        # try block to debug code
        try:
            self.message = await self.ctx.send(view=self)
            await self.update_message(self.data[:self.sep])
        except Exception as e:
            print(e)

    def create_embed(self, data: list) -> discord.Embed:
        url = URL + ("%20".join(self.arg.split()))
        embed = discord.Embed(title=self.arg, url=url, colour=discord.Colour.random())

        if len(self.data) > 1:
            for entry in data:
                embed.add_field(name=f"Page {self.current_page} of {int(len(self.data) / self.sep)}", value=entry, inline=False)
                embed.title = self.arg
        else:
            for entry in data:
                embed.add_field(name="Result", value=entry, inline=False)
                embed.title = self.arg

        return embed

    async def update_message(self, data: list) -> None:
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data), view=self)

    def update_buttons(self) -> None:
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False

        if self.current_page == int(len(self.data) / self.sep):
            self.next_button.disabled = True
            self.last_page_button.disabled = True
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
        
        if self.invoked_command in ("jisho", "j", "J"):
            self.jisho_button.disabled = True
        else:
            self.jisho_button.disabled = False
        
        if self.invoked_command in ("kanji", "k", "K"):
            self.kanji_button.disabled = True
        else:
            self.kanji_button.disabled = False
        
        if self.invoked_command in ("examples", "e", "E"):
            self.examples_button.disabled = True
        else:
            self.examples_button.disabled = False

        if self.invoked_command in ("tokenize", "tn"):
            self.token_button.disabled = True
        else:
            self.token_button.disabled = False

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.primary)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.current_page = 1
        until_item = self.current_page * self.sep
        await self.update_message(self.data[:until_item])

    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.current_page -= 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item])

    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.current_page += 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item])

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.current_page = int(len(self.data) / self.sep)
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:])

    @discord.ui.button(label="言葉", style=discord.ButtonStyle.primary)
    async def jisho_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.data = Jisho.word_search(self.arg)
        self.current_page = 1
        self.invoked_command = "j"
        await self.update_message(self.data[:self.sep])

    @discord.ui.button(label="漢字", style=discord.ButtonStyle.primary)
    async def kanji_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.data = Jisho.kanji_search(self.arg)
        self.current_page = 1
        self.invoked_command = "k"
        await self.update_message(self.data[:self.sep])

    @discord.ui.button(label="例文", style=discord.ButtonStyle.primary)
    async def examples_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.data = Jisho.examples_search(self.arg)
        self.current_page = 1
        self.invoked_command = "e"
        await self.update_message(self.data[:self.sep])
    
    @discord.ui.button(label="作文", style=discord.ButtonStyle.primary)
    async def token_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.data = Jisho.token_search(self.arg)
        self.current_page = 1
        self.invoked_command = "tn"
        await self.update_message(self.data[:self.sep])


class Jisho(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def word_search(arg: str) -> list:
        request = Word.request(arg)

        if not request:
            return [f"No word found for {arg}."]
        
        entries = json.loads(request.json())
        results = [item for item in entries["data"]]
        data = []
        
        add_nl = lambda s: "\n" + s
        join_c = lambda s: ", ".join(s)
        bold_i = lambda s: "***" + s + "***"
        add_i = lambda s: "*" + s + "*"

        for result in results:
            entry = ""
            word = _word if (_word:=result["japanese"][0]["word"]) else result["japanese"][0]["reading"]
            reading = _reading if word and (_reading:=result["japanese"][0]["reading"]) else ""

            fq = "common word" if result["is_common"] else ""
            jlpt = join_c(_jlpt) if (_jlpt:=result["jlpt"]) else ""
            tags = join_c(_tags) if (_tags:=result["tags"]) else ""
            
            joined = add_nl(f"`{_joined}`") if (_joined:=join_c([i for i in (fq, jlpt, tags) if i])) else ""
            entry += f"**{word}【{reading}】**{joined}\n"

            for index, senses in enumerate(result["senses"], start=1):
                parts_of_speech = add_nl(bold_i(join_c(_parts_of_speech))) if (_parts_of_speech:=senses["parts_of_speech"]) else ""
                links = _links if (_links:=senses["links"]) else ""

                english_definitions = join_c(senses["english_definitions"])
                tags = join_c(_tags) if (_tags:=senses["tags"]) else ""
                restrictions = "Only applies to " + join_c(_restrictions) if (_restrictions:=senses["restrictions"]) else ""

                _see_also = "".join(senses["see_also"])
                see_also_link = URL + ("%20".join(_see_also.split()))
                see_also = f"*see also [{_see_also}]({see_also_link})*" if _see_also else ""

                info = join_c(_info) if (_info:=senses["info"]) else ""
                joined = add_nl(_joined) if (_joined:=join_c([i for i in (tags, restrictions, see_also, info) if i])) else ""
                entry += f"{parts_of_speech}\n{index}. {english_definitions}{joined}"

                if links:
                    list_ = []
                    
                    for link in links:
                        text = link["text"]
                        url = link["url"]
                        text_url = f"[{text}]({url})"
                        list_.append(text_url)
                        
                    entry += add_nl(add_i("\n".join(list_)))
                    
                entry += "\n"

            if len(result["japanese"]) > 1:
                list_ = []
                
                for dict_ in result["japanese"][1:]:
                    otherword = _word if (_word:=dict_["word"]) else dict_["reading"]
                    otherreading = f"【{dict_['reading']}】" if dict_["word"] else ""
                    other_form = f"{otherword}{otherreading}"
                    list_.append(other_form)
                    
                entry += "\nOther forms\n" + "、".join(list_)

            if len(entry) > 1015:
                entry = entry[:1015] + " [...]"

            data.append(entry)
            
        return data

    @staticmethod
    def find_kanji(arg: str) -> list:
        # Regex pattern for Kanji (CJK Ideographs)
        kanji_pattern = re.compile(r'[\u4E00-\u9FFF]')
        return kanji_pattern.findall(arg)
    
    @staticmethod
    def find_hiragana(arg: str) -> list:
        # Regex pattern for Hiragana
        hiragana_pattern = re.compile(r'[\u3040-\u309F]')
        return hiragana_pattern.findall(arg)
    
    @staticmethod
    def find_katakana(arg: str) -> list:
        # Regex pattern for Katakana
        katakana_pattern = re.compile(r'[\u30A0-\u30FF]')
        return katakana_pattern.findall(arg)
    
    @staticmethod
    def find_roman(arg: str) -> list:
        # Regex pattern for Roman
        roman_pattern = re.compile(r'[\u0061-\u007A]')
        return roman_pattern.findall(arg)

    @staticmethod
    def kanji_search(arg: str) -> list:
        # TODO - make hiragana, katakana, and romaji also able to do a kanji search
        if kanji:=Jisho.find_kanji(arg):
            results = [json.loads(r.json()) for i in kanji if (r:=Kanji.request(i))]
    
        else:
           return [f"No kanji found for {arg}."]
        
        data = []

        for result in results:
            entry = ""
            kanji = result["data"]["kanji"]
            strokes = result["data"]["strokes"]
            
            main_meanings = result["data"]["main_meanings"]
            kun_readings = result["data"]["main_readings"]["kun"]
            on_readings = result["data"]["main_readings"]["on"]
            
            grade = result["data"]["meta"]["education"]["grade"]
            jlpt = result["data"]["meta"]["education"]["jlpt"]
            newspaper_rank = result["data"]["meta"]["education"]["newspaper_rank"]
            
            entry += f"Kanji: {kanji}\nStrokes: {strokes}\nMain meanings: {main_meanings}\nKun-readings: {kun_readings}\nOn-readings: {on_readings}\nGrade: {grade}\nJLPT: {jlpt}\nNewspaper rank: {newspaper_rank}"
            data.append(entry)
            
        return data
    
    @staticmethod
    def examples_search(arg: str) -> list:
        request = Sentence.request(arg)

        if not request:
            return [f"No examples found for {arg}."]
            
        results = json.loads(request.json())
        data = []
        entry = ""

        for index, result in enumerate(results["data"], start=1):
            japanese = result["japanese"]
            en_translation = result["en_translation"]
            entry += f"{index}. {japanese}\n{en_translation}\n\n"

        if len(entry) > 1015:
            entry = entry[:1015]  + " [...]"

        data.append(entry)

        return data
    
    @staticmethod
    def token_search(arg: str) -> list:
        request = Tokens.request(arg)

        if not request:
            return [f"No tokens found for {arg}."]
        
        results = json.loads(request.json())
        data = []
        entry = ""
        
        for token in results["data"]:
            entry += f"{token['token']} {token['pos_tag']}\n"
            
        data.append(entry)
        
        return data

    @commands.command(aliases=["j", "J"])
    async def jisho(self, ctx: commands.context, *, arg: str) -> None:
        page_view = PageView(ctx=ctx, arg=arg, data=self.word_search(arg))
        await page_view.send()
    
    @commands.command(aliases=["k", "K"])
    async def kanji(self, ctx: commands.context, *, arg: str) -> None:
        page_view = PageView(ctx=ctx, arg=arg, data=self.kanji_search(arg))
        await page_view.send()
    
    @commands.command(aliases=["e", "E"])
    async def examples(self, ctx: commands.context, *, arg: str) -> None:
        page_view = PageView(ctx=ctx, arg=arg, data=self.examples_search(arg))
        await page_view.send()
    
    @commands.command(aliases=["tn"])
    async def tokenize(self, ctx: commands.context, *, arg: str) -> None:
        page_view = PageView(ctx=ctx, arg=arg, data=self.token_search(arg))
        await page_view.send()


async def setup(bot):
    await bot.add_cog(Jisho(bot))


if __name__ == "__main__":
    test()
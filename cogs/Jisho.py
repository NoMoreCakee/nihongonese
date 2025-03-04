import json
import re
import discord
from discord.ext import commands
from jisho_api.word import Word
from jisho_api.kanji import Kanji
from jisho_api.sentence import Sentence
from jisho_api.tokenize import Tokens


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

    async def send(self) -> None:
        self.message = await self.ctx.send(view=self)
        await self.update_message(self.data[:self.sep])

    def create_embed(self, data: list) -> discord.Embed:
        url = Jisho.URL + ("%20".join(self.arg.split()))
        embed = discord.Embed(title=self.arg, url=url, colour=discord.Colour.random())

        if len(self.data) > 1:
            name = f"Page {self.current_page} of {int(len(self.data) / self.sep)}"
        
        else:
            name = "Result"

        for base in data:
            embed.add_field(name=name, value=base, inline=False)
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
    URL = "https://jisho.org/search/"

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
            word = _word if (_word:=result["japanese"][0]["word"]) else result["japanese"][0]["reading"]
            reading = _reading if word and (_reading:=result["japanese"][0]["reading"]) else ""

            fq = "common word" if result["is_common"] else ""
            jlpt = join_c(_jlpt) if (_jlpt:=result["jlpt"]) else ""
            tags = join_c(_tags) if (_tags:=result["tags"]) else ""
            
            joined = add_nl(f"`{_joined}`") if (_joined:=join_c([i for i in (fq, jlpt, tags) if i])) else ""
            base = f"**{word}【{reading}】**{joined}\n"

            for index, senses in enumerate(result["senses"], start=1):
                parts_of_speech = add_nl(bold_i(join_c(_parts_of_speech))) if (_parts_of_speech:=senses["parts_of_speech"]) else ""
                links = _links if (_links:=senses["links"]) else ""

                english_definitions = join_c(senses["english_definitions"])
                tags = join_c(_tags) if (_tags:=senses["tags"]) else ""
                restrictions = "Only applies to " + join_c(_restrictions) if (_restrictions:=senses["restrictions"]) else ""

                _see_also = "".join(senses["see_also"])
                see_also_link = Jisho.URL + ("%20".join(_see_also.split()))
                see_also = f"*see also [{_see_also}]({see_also_link})*" if _see_also else ""

                info = join_c(_info) if (_info:=senses["info"]) else ""
                joined = add_nl(_joined) if (_joined:=join_c([i for i in (tags, restrictions, see_also, info) if i])) else ""
                base += f"{parts_of_speech}\n{index}. {english_definitions}{joined}"

                if links:
                    list_ = []
                    
                    for link in links:
                        text = link["text"]
                        url = link["url"]
                        text_url = f"[{text}]({url})"
                        list_.append(text_url)
                        
                    base += add_nl(add_i("\n".join(list_)))
                    
                base += "\n"

            if len(_japanese:=result["japanese"]) > 1:
                list_ = []
                
                for dict_ in _japanese[1:]:
                    other_word = _word if (_word:=dict_["word"]) else dict_["reading"]
                    other_reading = f"【{dict_['reading']}】" if dict_["word"] else ""
                    other_form = f"{other_word}{other_reading}"
                    list_.append(other_form)
                    
                base += "\nOther forms\n" + "、".join(list_)

            if len(base) > 1015:
                base = base[:1015] + " [...]"

            data.append(base)
            
        return data

    @staticmethod
    def find_kanji(arg: str) -> list:
        # Regex pattern for Kanji (CJK Ideographs)
        kanji_pattern = re.compile(r'[\u4E00-\u9FFF]')
        return kanji_pattern.findall(arg)

    @staticmethod
    def kanji_search(arg: str) -> list:
        # TODO - make hiragana, katakana, and romaji also able to do a kanji search
        if kanji:=Jisho.find_kanji(arg):
            results = [json.loads(r.json()) for i in kanji if (r:=Kanji.request(i))]
    
        else:
           return [f"No kanji found for {arg}."]
        
        data = []

        for result in results:
            kanji = "`Kanji`: " + result["data"]["kanji"]
            strokes = result["data"]["strokes"]

            main_meanings = "`Meanings`\n" + (", ".join(result["data"]["main_meanings"]))
            kun_readings = "\n`Kun`\n" + ("、".join(_kun)) + "\n" if (_kun:=result["data"]["main_readings"]["kun"]) else ""
            on_readings = "\n`On`\n" + ("、".join(_on)) + "\n" if (_on:=result["data"]["main_readings"]["on"]) else ""
            
            grade = result["data"]["meta"]["education"]["grade"]
            jlpt = result["data"]["meta"]["education"]["jlpt"]
            newspaper_rank = result["data"]["meta"]["education"]["newspaper_rank"]
            
            rad_alt_forms = "（" + (", ".join(_alt)) + "）" if (_alt:=result["data"]["radical"]["alt_forms"]) else ""
            rad_meaning = result["data"]["radical"]["meaning"]
            rad_parts = " `Parts`: " + (" ".join(_parts)) if (_parts:=result["data"]["radical"]["parts"]) else ""

            rad_basis = result["data"]["radical"]["basis"]
            rad_variants = " `Variants`: " + (" ".join(_variants)) if (_variants:=result["data"]["radical"]["variants"]) else ""
            rad = f" `Radical`: {rad_meaning} {rad_basis}"

            kun_examples = result["data"]["reading_examples"]["kun"]
            on_examples = result["data"]["reading_examples"]["on"]

            base = f"{kanji} `Strokes`: {strokes}\n{rad}{rad_alt_forms}{rad_parts}{rad_variants}\n`JLPT`: {jlpt}, `Taught in`: {grade}, `Newspaper rank`: {newspaper_rank}\n\n{main_meanings}\n{kun_readings}{on_readings}"

            if kun_examples:
                base += "\n`Kunyomi examples`"

                for ex in kun_examples[:3]:
                    word = ex["kanji"]
                    reading = ex["reading"]
                    meanings = ", ".join(ex["meanings"])
                    base += f"\n**{word}【{reading}】**\n{meanings}"
                
                base += "\n"
            
            if on_examples:
                base += "\n`Onyomi examples`"

                for ex in on_examples[:3]:
                    word = ex["kanji"]
                    reading = ex["reading"]
                    meanings = ", ".join(ex["meanings"])
                    base += f"\n**{word}【{reading}】**\n{meanings}"
            
            if len(base) > 1015:
                base = base[:1015]  + " [...]"

            data.append(base)
            
        return data
    
    @staticmethod
    def examples_search(arg: str) -> list:
        request = Sentence.request(arg)

        if not request:
            return [f"No examples found for {arg}."]
            
        results = json.loads(request.json())
        data = []
        base = ""

        for index, result in enumerate(results["data"], start=1):
            japanese = result["japanese"]
            en_translation = result["en_translation"]
            base += f"{index}. {japanese}\n{en_translation}\n\n"

        if len(base) > 1015:
            base = base[:1015]  + " [...]"

        data.append(base)

        return data
    
    @staticmethod
    def token_search(arg: str) -> list:
        request = Tokens.request(arg)

        if not request:
            return [f"No tokens found for {arg}."]
        
        results = json.loads(request.json())
        data = []
        base = ""
        
        for token in results["data"]:
            base += f"{token['token']} {token['pos_tag']}\n"
        
        if len(base) > 1015:
            base = base[:1015]  + " [...]"
            
        data.append(base)
        
        return data

    @commands.hybrid_command(aliases=["j", "J"], description="Searches for Japanese words")
    async def jisho(self, ctx: commands.context, *, arg: str) -> None:
        page_view = PageView(ctx=ctx, arg=arg, data=self.word_search(arg))
        await page_view.send()
    
    @commands.hybrid_command(aliases=["k", "K"], description="Searches for kanji")
    async def kanji(self, ctx: commands.context, *, arg: str) -> None:
        page_view = PageView(ctx=ctx, arg=arg, data=self.kanji_search(arg))
        await page_view.send()
    
    @commands.hybrid_command(aliases=["e", "E"], description="Searches for Japanese example sentences")
    async def examples(self, ctx: commands.context, *, arg: str) -> None:
        page_view = PageView(ctx=ctx, arg=arg, data=self.examples_search(arg))
        await page_view.send()
    
    @commands.hybrid_command(aliases=["tn"], description="Searches for tokens(parts) in a Japanese sentence")
    async def tokenize(self, ctx: commands.context, *, arg: str) -> None:
        page_view = PageView(ctx=ctx, arg=arg, data=self.token_search(arg))
        await page_view.send()


async def setup(bot):
    await bot.add_cog(Jisho(bot))


if __name__ == "__main__":
    test()
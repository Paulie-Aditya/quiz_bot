import nextcord
from nextcord.ext import commands
from typing import Optional         #Used to make slash commands optional
import urllib.request               #Used to open urls of opentdb.com
import random                       #Used to randomize choices of each question
import asyncio                      #Used to keep a waiting time between questions, by default 10s
import json                         #Used to convert bytes to json while reading content from opentdb.com
import html                         #Used to convert few special characters to readable characters when reading from json, fetched from the api

import config_quiz_bot

prefix = "&"
bot = commands.Bot(command_prefix = prefix, intents = nextcord.Intents.all())

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


#Default Values
api_url = "https://opentdb.com/api.php"         #API used to fetch Questions
duration = 10                                   #Standard duration between questions


class Options:
    #Adds category to api url, optional
    def category(category:str):
        api_key_dict = {"General Knowledge": 9, "Books": 10, "Films":11, "Music":12, "Musicals and Theatre":13, "Television":14, "Video Games":15,"Board Games":16, "Science & Nature":17, "Computers":18, "Mathematics":19, "Mythology":20, "Sports":21, "Geography":22,"History":23, "Politics":24, "Art":25, "Celebrities":26, "Animals":27, "Vehicles":28, "Comics":29, "Gadgets":30, "Japanese Anime & Manga":31, "Cartoon & Animations":32}
        global api_url
        api_url+="&category="+str(api_key_dict[category])
        pass

    #Adds difficulty to api url, optional
    def difficulty(difficulty:str):
        global api_url
        api_url+="&difficulty="+ difficulty.lower()
        pass

    #Required parameter, defines the number of questions
    def amount(amount:int):
        global api_url
        api_url += '?amount='+str(amount)
        pass

class Quiz:
        #Converts html special characters to readable content
        def replace(arg):
            arg = html.unescape(arg)
            return arg

        #Main function
        def quiz(stuff:dict):
            category = stuff['category']
            question_type = stuff['type']
            question = stuff['question']
            question = Quiz.replace(question)
            correct_ans = stuff['correct_answer']
            incorrect_ans = stuff['incorrect_answers']

            options = list(incorrect_ans)
            options.append(correct_ans)
            random.shuffle(options)

            description = f'''**Your Question is:** {question}\n\n'''

            embed = nextcord.Embed(title = f'Category: {category}',description= description,color= 0x21f9fd)
            correct = options.index(correct_ans)

            for i in range(len(options)):
                options[i] = Quiz.replace(options[i])

            if question_type == 'boolean':
                embed.add_field(name = f":regional_indicator_a: {options[0]}", value= "",inline=False)
                embed.add_field(name = f":regional_indicator_b: {options[1]}", value= "",inline=False)
            else:
                embed.add_field(name = f":regional_indicator_a: {options[0]}", value= "",inline=False)
                embed.add_field(name = f":regional_indicator_b: {options[1]}", value= "",inline=False)
                embed.add_field(name = f":regional_indicator_c: {options[2]}", value= "",inline=False)
                embed.add_field(name = f":regional_indicator_d: {options[3]}", value= "",inline=False)


            return embed, options,correct, question_type, question

@bot.slash_command(name = 'start',description = "Start a Quiz!")
async def start(
    interaction: nextcord.Interaction,

    amount: int = nextcord.SlashOption(required=True),

    category: Optional[str] = nextcord.SlashOption(
        name="category",
        choices=["General Knowledge", "Books", "Films", "Music", "Musicals and Theatre", "Television", "Video Games","Board Games", "Science & Nature", "Computers", "Mathematics", "Mythology", "Sports", "Geography","History", "Politics", "Art", "Celebrities", "Animals", "Vehicles", "Comics", "Gadgets", "Japanese Anime & Manga", "Cartoon & Animations"],
        required= False,
    ),

    difficulty: Optional[str] = nextcord.SlashOption(
        name = "difficulty",
        choices = ["Easy","Medium","Difficult"],
        required= False,
    ),

):
    global api_url
    api_url = "https://opentdb.com/api.php"
    if amount <0 or amount>50:
        await interaction.response.send_message("Please enter a Valid Amount. Max Questions allowed is 50")
        exit
    else:
        Options.amount(amount)

    if category:
        Options.category(category)
    else:
        pass
    if difficulty:
        Options.difficulty(difficulty)
    else:
        pass
    await interaction.response.send_message(f'Starting Quiz Now')

    #Opening up the api link, and converting into readable format (json)
    webUrl = urllib.request.urlopen(api_url)
    questions = webUrl.read()

    questions = str(questions,'UTF-8')
    questions.replace("'",'"')
    my_json = json.loads(questions)



    for i in my_json['results']:

        embed, options,correct, question_type, question= Quiz.quiz(i)

        #View Component for Question
        class Question(nextcord.ui.View):
            def __init__(self) -> None:
                super().__init__()
                self.value = None

            if question_type == 'boolean':
                @nextcord.ui.button(label = f'{options[0]}', style=nextcord.ButtonStyle.grey, emoji="🇦")
                async def option_0(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    self.value = 0
                    await Question.correct_or_not(self,interaction)
                    self.stop()

                @nextcord.ui.button(label = f'{options[1]}', style=nextcord.ButtonStyle.grey, emoji="🇧")
                async def option_1(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    self.value = 1
                    await Question.correct_or_not(self,interaction)
                    self.stop()
            else:
                @nextcord.ui.button(label = f'{options[0]}', style=nextcord.ButtonStyle.grey, emoji="🇦")
                async def option_0(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    self.value = 0
                    await Question.correct_or_not(self,interaction)
                    self.stop()

                @nextcord.ui.button(label = f'{options[1]}', style=nextcord.ButtonStyle.grey, emoji="🇧")
                async def option_1(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    self.value = 1
                    await Question.correct_or_not(self,interaction)
                    self.stop()

                @nextcord.ui.button(label = f'{options[2]}', style=nextcord.ButtonStyle.grey, emoji= "🇨")
                async def option_2(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    self.value = 2
                    await Question.correct_or_not(self,interaction)
                    self.stop()

                @nextcord.ui.button(label = f'{options[3]}', style=nextcord.ButtonStyle.grey, emoji= "🇩")
                async def option_3(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    self.value = 3
                    await Question.correct_or_not(self,interaction)
                    self.stop()

            #Checks's whether the button clicked by the user is the correct option or not
            async def correct_or_not(self, interaction:nextcord.Interaction):
                if self.value == correct:
                    await interaction.send("Correct! ✅",ephemeral=True)

                else:
                    await interaction.send("Incorrect! ❌", ephemeral=True)

        #View component for Answer (sent after duration between questions)
        class Answer(nextcord.ui.View):
            style = [nextcord.ButtonStyle.grey, nextcord.ButtonStyle.grey, nextcord.ButtonStyle.grey, nextcord.ButtonStyle.grey]
            style[correct] = nextcord.ButtonStyle.green

            def __init__(self) -> None:
                super().__init__()


            if question_type == 'boolean':
                @nextcord.ui.button(label = f'{options[0]}', style= style[0] ,emoji="🇦", disabled=True)
                async def option_0(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    pass

                @nextcord.ui.button(label = f'{options[1]}',  style= style[1] ,emoji="🇧",disabled=True)
                async def option_1(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = f'{options[0]}', style= style[0] ,emoji="🇦", disabled=True)
                async def option_0(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    pass

                @nextcord.ui.button(label = f'{options[1]}', style= style[1] ,emoji="🇧", disabled=True)
                async def option_1(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    pass

                @nextcord.ui.button(label = f'{options[2]}', style= style[2] ,emoji= "🇨", disabled=True)
                async def option_2(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    pass

                @nextcord.ui.button(label = f'{options[3]}', style= style[3] ,emoji= "🇩", disabled=True)
                async def option_3(self, button: nextcord.Button, interaction:nextcord.Interaction):
                    pass

        await interaction.send(embed= embed, view=Question(), delete_after=float(duration-1))
        await asyncio.sleep(duration-1)
        ans_embed = nextcord.Embed(title = f'🥁The CORRECT Answer to Question: `{question}` IS 🥁', description= f'**:regional_indicator_{chr(97+correct)}: {options[correct]}**' ,color= 0x10eb38)
        await interaction.send(embed = ans_embed, view= Answer())
    exit

bot.run(config_quiz_bot.quiz_bot_token)
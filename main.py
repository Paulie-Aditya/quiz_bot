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
duration = 10                                   #Standard duration used in various places

#Function to handle users joining the quiz about to start
def participate():
    points = {}
    users = []
    class Participate(nextcord.ui.View):
        global embed
        embed = nextcord.Embed(title= f"Quiz starting in {duration} seconds", description= "React below to join!", color= 0x0c97f6)

        @nextcord.ui.button(label="Join the Quiz!",style=nextcord.ButtonStyle.blurple)
        async def callback(self, button:nextcord.Button, interaction: nextcord.Interaction):
            points[interaction.user.id] = 0
            users.append(interaction.user.id)
    view = Participate()
    return embed, view, points


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

        #Main Function which handles Questions
        def quiz(stuff:dict):
            category = stuff['category']
            question_type = stuff['type']
            question = stuff['question']
            question = Quiz.replace(question)
            correct_ans = stuff['correct_answer']
            incorrect_ans = stuff['incorrect_answers']

            options = list(incorrect_ans)
            options.append(correct_ans)

            if len(options) == 2:
                options = ["True","False"]
            else:
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

    amount: int = nextcord.SlashOption(
        required=True, 
        description="Number of Questions",
    ),
    category: Optional[str] = nextcord.SlashOption(
        name="category",
        choices=["General Knowledge", "Books", "Films", "Music", "Musicals and Theatre", "Television", "Video Games","Board Games", "Science & Nature", "Computers", "Mathematics", "Mythology", "Sports", "Geography","History", "Politics", "Art", "Celebrities", "Animals", "Vehicles", "Comics", "Gadgets", "Japanese Anime & Manga", "Cartoon & Animations"],
        required= False,
        description="Choose Category of the Quiz.", 
    ),

    difficulty: Optional[str] = nextcord.SlashOption(
        name = "difficulty",
        choices = ["Easy","Medium","Difficult"],
        required= False,
        description="Choose Difficulty of the Quiz.", 
    ),

):
    global api_url
    api_url = "https://opentdb.com/api.php"
    if amount <0 or amount>50:
        await interaction.response.send_message("Please enter a Valid Amount.Max Questions allowed is 50")
        return
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

    #Opening up the api link, and converting into readable format (json)
    webUrl = urllib.request.urlopen(api_url)
    questions = webUrl.read()

    questions = str(questions,'UTF-8')
    questions.replace("'",'"')
    my_json = json.loads(questions)

    embed,view,points = participate()
    await interaction.response.send_message(embed = embed, view= view, delete_after=duration)
    await asyncio.sleep(duration)
    #print(points)




    for i in my_json['results']:

        embed, options,correct, question_type, question= Quiz.quiz(i)
        ans_embed = nextcord.Embed(title = f'🥁The CORRECT ANSWER IS 🥁', description= "\n\n",color= 0x10eb38)
        ans_embed.add_field(name = f'Question: {question} \n\n**:regional_indicator_{chr(97+correct)}: {options[correct]}**' , value = " ")

        #View Component for Question
        class Question(nextcord.ui.View):
            global done
            done = duration
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
                
                #await interaction.message.edit(embed=ans_embed, view=Answer())
                #await interaction.message.delete(delay=None)
                
                if self.value == correct:
                    correct_or_incorrect = f"Their Answer is Correct! 🎊 🎊"
                    try:
                        points[interaction.user.id] +=1
                        await interaction.message.edit(embed=ans_embed, view=Answer())
                        await interaction.send(f'{interaction.user.mention} answered First! {correct_or_incorrect}')
                    except KeyError:
                        await interaction.send(f'{interaction.user.mention}, You have not joined the Quiz, please wait for the next round.', ephemeral=True)
                    
                    #color = 0x03f142
                else:
                    correct_or_incorrect = f"Their Answer is Incorrect! 😔"
                    try:
                        points[interaction.user.id] +=0
                        await interaction.message.edit(embed=ans_embed, view=Answer())
                        await interaction.send(f'{interaction.user.mention} answered First! {correct_or_incorrect}')
                    except KeyError:
                        await interaction.send(f'{interaction.user.mention}, You have not joined the Quiz, please wait for the next round.', ephemeral=True)
                    
                    #color = 0xf1031d


            embed.set_thumbnail(url="https://clipart-library.com/images/ATbr7A4Xc.jpg")



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

        await interaction.send(embed= embed, view=Question(), delete_after= duration-1)
        await asyncio.sleep(duration-1)
        await interaction.send(embed=ans_embed, view=Answer())

        #await interaction.send(embed = ans_embed, view= Answer())

    leaderboard = nextcord.Embed(title= " 🏆 Leaderboard 🏆", color= 0x00ffdc)

    #winners = sorted(points.keys(), key= lambda x:x[1], reverse=True)
    points  = sorted(points.items(), key = lambda x:x[1], reverse=True)


    i = 0
    while (i<10):
        emoji = ""
        if i+1 <=3:
            if i+1 == 1:
                emoji = '🥇 '
            elif i+1 == 2:
                emoji = '🥈 '
            elif i+1 == 3:
                emoji = '🥉 '
        try:
            leaderboard.add_field(name = f'{emoji}#{i+1}', value= f"<@{points[i][0]}> with **{points[i][1]} POINTS!**\n", inline= False)
        except:
            if i == 0:
                leaderboard.add_field(name=f'Sadly no one joined the Quiz 😔', value="\n")
            break
        i+=1
    await interaction.send(embed=leaderboard)

    exit


bot.run(config_quiz_bot.quiz_bot_token)

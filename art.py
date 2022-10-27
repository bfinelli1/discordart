#! /usr/bin/python3
# art.py
import os
from tkinter import E
import discord
from dotenv import load_dotenv
from discord.ext import commands
import requests
import random
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()

response = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&isHighlight=true&q=*")
ids = response.json()['objectIDs']


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="anadosbot help menu",
    intents=intents,
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


@bot.command()
async def add(ctx: commands.Context, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(str(left + right))

@bot.command()
async def roll(ctx: commands.Context, dice: str):
    """Rolls a die in NdN format."""
    try:
        rolls, limit = map(int, dice.split("d"))
    except ValueError:
        await ctx.send("Format has to be in NdN!")
        return

    # _ is used in the generation of our result as we don't need the number that comes from the usage of range(rolls).
    result = ", ".join(str(random.randint(1, limit)) for _ in range(rolls))
    await ctx.send(result)

@bot.command()
async def ask(ctx: commands.Context):
    """ask a jeopardy question and wait for a number response 1-3"""
    numQuestions=5
    idlist=[]
    qlist = []
    qlistlength=0
    timeout=30
    channel = ctx.channel
    while qlistlength<=4: #check if there are too few qs in the category
        response = requests.get("https://jservice.io/api/random")
        categoryid = response.json()[0]['category_id']
        questionlist = requests.get(f"https://jservice.io/api/clues?category={categoryid}")
        print(f"{categoryid} amount in category: {len(questionlist.json())}")
        qlistlength = len(questionlist.json())
    newq=response.json()[0]
    answernum = random.randint(1, numQuestions)
    print(f"answer: {answernum}")
    for i in range(numQuestions):
        while newq['id'] in idlist: #check if q is already added by id
            newq = random.choice(questionlist.json())
        qlist.append(newq)
        idlist.append(int(newq['id']))
    await ctx.channel.send(f"Trivia category: {response.json()[0]['category']['title']}\n\n")
    await ctx.channel.send(f"Question: {qlist[answernum-1]['question']}")
    output=""
    for i, e in enumerate(qlist):
        output += f"{i+1} {e['answer']}\n"
        #await ctx.send(f"{i+1}  {e['answer']}")
    await ctx.send(output)

    def check(m):
        return m.content.isnumeric() and int(m.content[0])  == answernum and m.channel == channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=timeout)
    except asyncio.TimeoutError:
        await ctx.channel.send(f"time's up, the answer was {answernum}")
    else:
        await ctx.channel.send("correct!")

@bot.command()
async def art(ctx: commands.Context):
    """displays art from the met api."""
    url = ""
    while not url:
        str = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{random.choice(ids)}"
        response = requests.get(str)
        try:
            url = response.json()['primaryImage']
        except KeyError:
            print(f"keyerror i guess.\n{str}\n---")
            url=""
    url = url.replace(" ", "%20")
    print(f"{str}\n{url}")
    #await ctx.send(f"here's some random art from the met {url}")
    await ctx.send(url)

@bot.command()
async def artsearch(ctx: commands.Context, term: str):
    """search for a keyword and return a random result from the met"""
    ids=[]
    total=0
    tries=0
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?tags=true&q={term}"
    secondurl = f"https://collectionapi.metmuseum.org/public/collection/v1/search?title=true&q={term}"
    response = requests.get(url)
    ids = response.json()['objectIDs']
    total=response.json()['total']
    if not ids:
        ids = []
    
    response = requests.get(secondurl)
    secondids = response.json()['objectIDs']
    if not secondids:
        secondids = []
    ids.extend(secondids)
    total+=response.json()['total']
    ids = list(set(ids))

    if total<=0:
        await ctx.send("no results")
    else: 
        url = ""
        while not url and tries < 10:
            str = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{random.choice(ids)}"
            response = requests.get(str)
            try:
                url = response.json()['primaryImage']
            except KeyError:
                print(f"keyerror\n{str}\n---")
                url=""
            tries+=1
        tries=0
        url = url.replace(" ", "%20")
        print(f"{str}\n{url}")
        if not url:
            url = "not found"
        await ctx.send(url)


bot.run(TOKEN)

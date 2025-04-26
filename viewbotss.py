import os
import discord
import requests
import random
from flask import Flask
from threading import Thread
from discord.ext import commands

# --- CONFIG ---

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  # pulled from environment
SMMFLARE_API_KEY = os.getenv('SMMFLARE_API_KEY')
SERVICE_ID = 5483  # Instagram Views [Normal/IGTV/Reels]

COMMAND_PREFIX = "?"

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# --- KEEP ALIVE WEB SERVER ---

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- FUNCTION TO SEND VIEWS ---

def send_instagram_views(post_url, views_count):
    url = "https://smmflare.com/api/v2"
    payload = {
        "key": SMMFLARE_API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": post_url,
        "quantity": views_count
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        data = response.json()
        if 'order' in data:
            print(f"✅ Successfully sent {views_count} views to {post_url}")
            return True
        else:
            print(f"⚠️ SMMFlare Error: {data.get('error', 'Unknown error')}")
            return False
    else:
        print("⚠️ Failed to connect to SMMFlare.")
        return False

# --- BOT EVENTS ---

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if any(x in message.content for x in ['instagram.com/p/', 'instagram.com/reel/', 'instagram.com/tv/']):
        post_url = message.content.strip().split('?')[0]

        views = random.randint(1758, 9862)

        success = send_instagram_views(post_url, views)

        if success:
            await message.channel.send(f"✅ Sent {views} views to your Instagram video!")
        else:
            await message.channel.send(f"⚠️ Failed to send views to {post_url}")

        return

    await bot.process_commands(message)

# --- BOT COMMANDS ---

@bot.command()
async def viewbot(ctx, url: str, views: int):
    await ctx.send(f"Attempting to send {views} views to {url}...")
    success = send_instagram_views(url, views)
    if success:
        await ctx.send(f"✅ Successfully sent {views} views to {url}!")
    else:
        await ctx.send(f"⚠️ Failed to send views to {url}.")

@bot.command()
async def helpme(ctx):
    help_text = """
**Instagram ViewBot Help**

__Automatic Mode:__
- Send any Instagram Post, Reel, or IGTV link.
- The bot automatically sends random views (1758–9862).

__Manual Commands:__
- `?viewbot <url> <amount>` — Send a specific number of views manually.
- `?helpme` — Show this help message.
"""
    await ctx.send(help_text)

# --- RUN THE BOT ---

keep_alive()
bot.run(DISCORD_TOKEN)
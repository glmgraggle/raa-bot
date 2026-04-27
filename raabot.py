import discord
from discord.ext import commands
from datetime import datetime, timezone

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

import asyncio

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(midnight_clear())

async def midnight_clear():
    while True:
        now = datetime.now(timezone.utc)
        # Calculate seconds until next midnight UTC
        seconds_until_midnight = (
            (23 - now.hour) * 3600 +
            (59 - now.minute) * 60 +
            (60 - now.second)
        )
        await asyncio.sleep(seconds_until_midnight)
        
        departures.clear()
        channel = bot.get_channel(BOARD_CHANNEL_ID)
        message = await channel.fetch_message(BOARD_MESSAGE_ID)
        await message.edit(content=build_board())
        print("Board cleared at midnight UTC")

departures = []

BOARD_CHANNEL_ID = 1497869185240530944
BOARD_MESSAGE_ID = 1498121151959007453

# Add any channel IDs where !depart is allowed (your server + other airline servers)
ALLOWED_SUBMIT_CHANNELS = [
    1497869771449041037,
    1498125481180921958
          # replace with your actual #submit-dep channel ID
]   

def build_board():
    unix_time = int(datetime.now(timezone.utc).timestamp())
    header = (
        "**RAA GLOBAL DEPARTURES**\n"
        "Roblox Aviation Alliance\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "TIME   FLIGHT   ROUTE          GATE   STATUS\n"
        "──────────────────────────────────────────────\n"
    )
    if not departures:
        rows = "  No departures scheduled.\n"
    else:
        rows = ""
        for d in departures:
            rows += f"{d['time']:5}  {d['flight']:6}   {d['route']:13}  {d['gate']:4}   {d['status']}\n"

    footer = (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🟢 ON TIME  🟡 BOARDING  🔵 DELAYED  🔴 CLOSED\n\n"
        f"Updated: <t:{unix_time}:t>\n"
    )
    return header + rows + footer


@bot.command()
async def depart(ctx, flight, origin, dest, time, gate, status):
    if ctx.channel.id not in ALLOWED_SUBMIT_CHANNELS:
        await ctx.message.delete()
        return

    status_map = {
        "ontime": "🟢 ON TIME",
        "boarding": "🟡 BOARDING",
        "delayed": "🔵 DELAYED",
        "closed": "🔴 CLOSED"
    }
    formatted_status = status_map.get(status.lower(), "🟢 ON TIME")
    route = f"{origin}→{dest}"

    departures.append({
        "flight": flight,
        "route": route,
        "time": time,
        "gate": gate,
        "status": formatted_status
    })

    channel = bot.get_channel(BOARD_CHANNEL_ID)
    message = await channel.fetch_message(BOARD_MESSAGE_ID)
    await message.edit(content=build_board())
    await ctx.message.delete()

@bot.command()
async def clear(ctx):
    if ctx.channel.id not in ALLOWED_SUBMIT_CHANNELS:
        await ctx.message.delete()
        return

    departures.clear()
    channel = bot.get_channel(BOARD_CHANNEL_ID)
    message = await channel.fetch_message(BOARD_MESSAGE_ID)
    await message.edit(content=build_board())
    await ctx.message.delete()

import os
bot.run(os.environ.get("DISCORD_TOKEN"))
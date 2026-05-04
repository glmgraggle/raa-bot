import discord
from discord.ext import commands
from discord.ui import View, Select, Button
from datetime import datetime, timezone
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

departures = []

live_flight = None
live_flight_auto_remove_task = None

BOARD_CHANNEL_ID = 1497869185240530944
BOARD_MESSAGE_ID = 1500036971995594752
LIVE_STATUS_CHANNEL_ID = 1497869224335511633
LIVE_STATUS_MESSAGE_ID = 1500654494479024189
ANNOUNCEMENTS_CHANNEL_ID = 1497869538480488458
STAFF_ROLE_ID = 1500394070080749658
LIAISON_ROLE_ID = 1497870013623832717

ALLOWED_SUBMIT_CHANNELS = [
    1497869771449041037,
    1498125481180921958,
]

WATCHED_ANNOUNCEMENT_CHANNELS = [
    1500270751826051242,
    987654321098765432,
]

RAA_GOLD = 0xF5C842

AIRLINES = [
    {
        "name": "Air Canada",
        "code": "ACA",
        "description": "Canada's largest airline, operating an extensive domestic and international network from hubs in Toronto, Montreal, and Vancouver.",
        "invite": "https://discord.gg/aircanada",
        "color": 0xC8102E
    },
    {
        "name": "British Airways",
        "code": "BAW",
        "description": "The UK's flag carrier, connecting London Heathrow to destinations across the globe with a fleet of modern wide-body aircraft.",
        "invite": "https://discord.gg/example2",
        "color": 0x2B5FAD
    },
    {
        "name": "Qatar Airways",
        "code": "QTR",
        "description": "Award-winning Gulf carrier based in Doha, renowned for its premium cabin experience and extensive global route network.",
        "invite": "https://discord.gg/example3",
        "color": 0x5C0632
    },
    {
        "name": "Emirates",
        "code": "UAE",
        "description": "Dubai's flagship carrier and one of the world's largest airlines, operating long-haul routes across six continents.",
        "invite": "https://discord.gg/example4",
        "color": 0xD71920
    },
    {
        "name": "Qantas",
        "code": "QFA",
        "description": "Australia's national carrier, the Flying Kangaroo, operating domestic and long-haul international services from Sydney and Melbourne.",
        "invite": "https://discord.gg/example5",
        "color": 0xEE2A24
    },
    {
        "name": "Delta Air Lines",
        "code": "DAL",
        "description": "One of America's largest carriers, operating a vast domestic network and international routes from hubs across the United States.",
        "invite": "https://discord.gg/example6",
        "color": 0x003A70
    },
    {
        "name": "Lufthansa",
        "code": "DLH",
        "description": "Germany's flag carrier, connecting Frankfurt and Munich to destinations worldwide with a reputation for precision and reliability.",
        "invite": "https://discord.gg/example7",
        "color": 0x05164D
    },
    {
        "name": "Singapore Airlines",
        "code": "SIA",
        "description": "Consistently ranked among the world's best airlines, Singapore Airlines offers exceptional service on routes across Asia and beyond.",
        "invite": "https://discord.gg/example8",
        "color": 0x1B3F8B
    },
    {
        "name": "Air New Zealand",
        "code": "ANZ",
        "description": "New Zealand's national airline, known for its friendly Kiwi service and award-winning long-haul routes across the Pacific.",
        "invite": "https://discord.gg/example9",
        "color": 0x000000
    },
    {
        "name": "Cathay Pacific",
        "code": "CPA",
        "description": "Hong Kong's home carrier, operating a premium network of routes connecting Asia to Europe, Oceania, and the Americas.",
        "invite": "https://discord.gg/example10",
        "color": 0x006564
    },
    {
        "name": "Air France",
        "code": "AFR",
        "description": "France's flag carrier, offering elegant service from Paris Charles de Gaulle to destinations across Europe and the world.",
        "invite": "https://discord.gg/example11",
        "color": 0x002157
    },
    {
        "name": "KLM Royal Dutch Airlines",
        "code": "KLM",
        "description": "The Netherlands' national airline and one of the oldest carriers in the world, based at Amsterdam Schiphol Airport.",
        "invite": "https://discord.gg/example12",
        "color": 0x009CE0
    },
    {
        "name": "United Airlines",
        "code": "UAL",
        "description": "A major US carrier with one of the world's largest route networks, operating from hubs including Chicago, Houston, and Newark.",
        "invite": "https://discord.gg/example13",
        "color": 0x005DAA
    },
    {
        "name": "Japan Airlines",
        "code": "JAL",
        "description": "Japan's flagship carrier, offering premium Japanese hospitality on domestic routes and international services from Tokyo.",
        "invite": "https://discord.gg/example14",
        "color": 0xC8102E
    },
    {
        "name": "Turkish Airlines",
        "code": "THY",
        "description": "Flying to more countries than any other airline, Turkish Airlines connects Istanbul to an unmatched global destination list.",
        "invite": "https://discord.gg/example15",
        "color": 0xC8102E
    },
]

# ═══════════════════════════════════════════
# BUILD FUNCTIONS
# ═══════════════════════════════════════════

def build_live_status(flight=None):
    if not flight:
        embed = discord.Embed(
            title="🛫  RAA LIVE FLIGHT STATUS",
            description=(
                "**Roblox Aviation Alliance — Live Operations**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "No flight currently in progress."
            ),
            color=RAA_GOLD
        )
        embed.set_footer(text="Roblox Aviation Alliance  ·  Live Status")
        embed.timestamp = datetime.now(timezone.utc)
        return embed

    status_colors = {
        "🟢 ON TIME": 0x2ECC71,
        "🟡 BOARDING": 0xF1C40F,
        "🔵 DELAYED": 0x3498DB,
        "🔴 CLOSED": 0xE74C3C,
    }
    color = status_colors.get(flight["status"], RAA_GOLD)

    embed = discord.Embed(
        title="🛫  RAA LIVE FLIGHT STATUS",
        description=(
            "**Roblox Aviation Alliance — Live Operations**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "A flight is currently in progress. See details below."
        ),
        color=color
    )
    embed.add_field(name="✈  Airline", value=f"`{flight['airline']}`", inline=True)
    embed.add_field(name="🔢  Flight Number", value=f"`{flight['flight']}`", inline=True)
    embed.add_field(name="🛩  Aircraft", value=f"`{flight['aircraft']}`", inline=True)
    embed.add_field(name="🗺  Route", value=f"`{flight['route']}`", inline=True)
    embed.add_field(name="🚪  Gate", value=f"`{flight['gate']}`", inline=True)
    embed.add_field(name="📊  Status", value=flight["status"], inline=True)
    if flight.get("note"):
        embed.add_field(name="📝  Staff Note", value=flight["note"], inline=False)
    if flight.get("private_link"):
        embed.add_field(
            name="🔗  Private Server",
            value=f"[Click to join]({flight['private_link']})",
            inline=False
        )
    embed.set_footer(text="Roblox Aviation Alliance  ·  Live Status")
    embed.timestamp = datetime.now(timezone.utc)
    return embed

def status_emoji(status):
    if "ON TIME" in status: return "🟢"
    elif "BOARDING" in status: return "🟡"
    elif "DELAYED" in status: return "🔵"
    elif "CLOSED" in status: return "🔴"
    return "⚪"

def build_embed(filter_airline=None, filter_status=None):
    filtered = departures

    if filter_airline and filter_airline != "ALL":
        filtered = [d for d in filtered if d['airline'].upper() == filter_airline.upper()]
    if filter_status and filter_status != "ALL":
        filtered = [d for d in filtered if filter_status.upper() in d['status'].upper()]

    embed = discord.Embed(
        title="✈  RAA GLOBAL DEPARTURES",
        description=(
            "**Roblox Aviation Alliance — Live Departures Board**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        ),
        color=RAA_GOLD
    )

    if not filtered:
        embed.add_field(
            name="No Departures",
            value="No flights match the selected filter." if (filter_airline or filter_status) else "No flights currently scheduled.",
            inline=False
        )
    else:
        for d in filtered:
            embed.add_field(
                name=f"{status_emoji(d['status'])}  {d['flight']}  ·  {d['airline']}",
                value=(
                    f"**Route:** `{d['route']}`\n"
                    f"**Time:** `{d['time']}`  **Gate:** `{d['gate']}`\n"
                    f"**Status:** {d['status']}"
                ),
                inline=True
            )

    active_filters = []
    if filter_airline and filter_airline != "ALL":
        active_filters.append(f"Airline: {filter_airline.upper()}")
    if filter_status and filter_status != "ALL":
        active_filters.append(f"Status: {filter_status}")

    filter_text = "  ·  Filters: " + ", ".join(active_filters) if active_filters else ""
    embed.set_footer(text=f"Roblox Aviation Alliance{filter_text}")
    embed.timestamp = datetime.now(timezone.utc)
    return embed

def get_airline_options():
    airlines = list(set(d['airline'].upper() for d in departures))
    options = [discord.SelectOption(label="All Airlines", value="ALL", emoji="✈")]
    for airline in sorted(airlines):
        options.append(discord.SelectOption(label=airline, value=airline))
    return options

# ═══════════════════════════════════════════
# BOARD VIEW
# ═══════════════════════════════════════════

class BoardView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.filter_airline = None
        self.filter_status = None

    @discord.ui.select(
        placeholder="🔽  Filter by Airline...",
        options=[discord.SelectOption(label="All Airlines", value="ALL", emoji="✈")],
        custom_id="airline_filter"
    )
    async def airline_select(self, interaction: discord.Interaction, select: Select):
        select.options = get_airline_options()
        self.filter_airline = select.values[0]
        await interaction.response.edit_message(
            embed=build_embed(self.filter_airline, self.filter_status),
            view=self
        )

    @discord.ui.select(
        placeholder="🔽  Filter by Status...",
        options=[
            discord.SelectOption(label="All Statuses", value="ALL", emoji="🔄"),
            discord.SelectOption(label="On Time", value="ON TIME", emoji="🟢"),
            discord.SelectOption(label="Boarding", value="BOARDING", emoji="🟡"),
            discord.SelectOption(label="Delayed", value="DELAYED", emoji="🔵"),
            discord.SelectOption(label="Closed", value="CLOSED", emoji="🔴"),
        ],
        custom_id="status_filter"
    )
    async def status_select(self, interaction: discord.Interaction, select: Select):
        self.filter_status = select.values[0]
        await interaction.response.edit_message(
            embed=build_embed(self.filter_airline, self.filter_status),
            view=self
        )

    @discord.ui.button(label="Reset Filters", style=discord.ButtonStyle.secondary, emoji="↩", custom_id="reset")
    async def reset_button(self, interaction: discord.Interaction, button: Button):
        self.filter_airline = None
        self.filter_status = None
        await interaction.response.edit_message(
            embed=build_embed(),
            view=self
        )

# ═══════════════════════════════════════════
# UPDATE FUNCTIONS
# ═══════════════════════════════════════════

async def update_board():
    channel = bot.get_channel(BOARD_CHANNEL_ID)
    message = await channel.fetch_message(BOARD_MESSAGE_ID)
    view = BoardView()
    view.children[0].options = get_airline_options() if departures else [
        discord.SelectOption(label="All Airlines", value="ALL", emoji="✈")
    ]
    await message.edit(embed=build_embed(), view=view)

async def update_live_status():
    channel = bot.get_channel(LIVE_STATUS_CHANNEL_ID)
    if not channel:
        return
    try:
        message = await channel.fetch_message(LIVE_STATUS_MESSAGE_ID)
        await message.edit(embed=build_live_status(live_flight))
    except discord.NotFound:
        pass

async def auto_remove_flight(flight_data):
    await asyncio.sleep(1200)
    if flight_data in departures:
        departures.remove(flight_data)
        await update_board()
        print(f"Auto-removed closed flight {flight_data['flight']}")

async def auto_clear_live():
    global live_flight, live_flight_auto_remove_task
    await asyncio.sleep(1200)
    live_flight = None
    live_flight_auto_remove_task = None
    await update_live_status()
    print("Live status auto-cleared after 20 minutes")

async def schedule_live_status(flight_data: dict, departure_time_str: str):
    global live_flight, live_flight_auto_remove_task

    try:
        now = datetime.now(timezone.utc)

        # Parse the departure time as today in UTC
        dep_time = datetime.strptime(departure_time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc
        )

        # Calculate 20 minutes before departure
        trigger_time = dep_time - __import__("datetime").timedelta(minutes=20)

        # How many seconds until trigger
        seconds_until_trigger = (trigger_time - now).total_seconds()

        if seconds_until_trigger < 0:
            # Time already passed, don't trigger
            return

        await asyncio.sleep(seconds_until_trigger)

        # Check flight is still in departures list
        if flight_data not in departures:
            return

        # Set live status automatically
        live_flight = {
            "airline": flight_data["airline"],
            "flight": flight_data["flight"],
            "route": flight_data["route"],
            "gate": flight_data["gate"],
            "aircraft": flight_data.get("aircraft", "Unknown"),
            "status": flight_data["status"]
        }

        if live_flight_auto_remove_task:
            live_flight_auto_remove_task.cancel()
            live_flight_auto_remove_task = None

        await update_live_status()
        print(f"Live status auto-set for {flight_data['flight']}")

    except Exception as e:
        print(f"Error scheduling live status: {e}")

async def flight_autocomplete(interaction: discord.Interaction, current: str):
    return [
        discord.app_commands.Choice(
            name=f"{d['flight']} · {d['airline']} · {d['route']}",
            value=d['flight']
        )
        for d in departures
        if current.upper() in d['flight'].upper() or current == ""
    ][:25]

# ═══════════════════════════════════════════
# DEPARTURE COMMANDS
# ═══════════════════════════════════════════


@bot.tree.command(name="depart", description="Add a departure to the RAA board")
@discord.app_commands.describe(
    airline="Airline code e.g. ACA",
    flight="Flight number e.g. AC842",
    origin="Origin airport ICAO e.g. CYYZ",
    dest="Destination airport ICAO e.g. EGLL",
    time="Departure time in UTC e.g. 19:05",
    gate="Gate e.g. B5",
    aircraft="Aircraft type e.g. Boeing 777",
    status="Flight status"
)
@discord.app_commands.choices(status=[
    discord.app_commands.Choice(name="🟢 On Time", value="ontime"),
    discord.app_commands.Choice(name="🟡 Boarding", value="boarding"),
    discord.app_commands.Choice(name="🔵 Delayed", value="delayed"),
    discord.app_commands.Choice(name="🔴 Closed", value="closed"),
])
async def slash_depart(interaction: discord.Interaction, airline: str, flight: str, origin: str, dest: str, time: str, gate: str, aircraft: str, status: str):
    if interaction.channel.id not in ALLOWED_SUBMIT_CHANNELS:
        await interaction.response.send_message("Wrong channel.", ephemeral=True)
        return

    status_map = {
        "ontime": "🟢 ON TIME",
        "boarding": "🟡 BOARDING",
        "delayed": "🔵 DELAYED",
        "closed": "🔴 CLOSED"
    }
    formatted_status = status_map.get(status.lower(), "🟢 ON TIME")
    route = f"{origin.upper()} → {dest.upper()}"

    flight_data = {
        "airline": airline.upper(),
        "flight": flight.upper(),
        "route": route,
        "time": time,
        "gate": gate,
        "aircraft": aircraft,
        "status": formatted_status
    }
    departures.append(flight_data)
    await update_board()
    await interaction.response.send_message(f"✅ Flight {flight.upper()} added.", ephemeral=True)

    if status.lower() == "closed":
        bot.loop.create_task(auto_remove_flight(flight_data))

    # Schedule auto live status 20 minutes before departure
    bot.loop.create_task(schedule_live_status(flight_data, time))

@bot.tree.command(name="editflight", description="Edit an existing flight on the RAA board")
@discord.app_commands.describe(
    flight="Select the flight to edit",
    status="New status (optional)",
    gate="New gate (optional)",
    time="New time (optional)"
)
@discord.app_commands.choices(status=[
    discord.app_commands.Choice(name="🟢 On Time", value="ontime"),
    discord.app_commands.Choice(name="🟡 Boarding", value="boarding"),
    discord.app_commands.Choice(name="🔵 Delayed", value="delayed"),
    discord.app_commands.Choice(name="🔴 Closed", value="closed"),
])
@discord.app_commands.autocomplete(flight=flight_autocomplete)
async def edit_flight(interaction: discord.Interaction, flight: str, status: str = None, gate: str = None, time: str = None):
    if interaction.channel.id not in ALLOWED_SUBMIT_CHANNELS:
        await interaction.response.send_message("Wrong channel.", ephemeral=True)
        return

    target = next((d for d in departures if d['flight'].upper() == flight.upper()), None)

    if not target:
        await interaction.response.send_message(f"❌ Flight {flight.upper()} not found.", ephemeral=True)
        return

    if status:
        status_map = {
            "ontime": "🟢 ON TIME",
            "boarding": "🟡 BOARDING",
            "delayed": "🔵 DELAYED",
            "closed": "🔴 CLOSED"
        }
        target['status'] = status_map.get(status.lower(), target['status'])
        if status.lower() == "closed":
            bot.loop.create_task(auto_remove_flight(target))

    if gate:
        target['gate'] = gate
    if time:
        target['time'] = time

    await update_board()
    await interaction.response.send_message(f"✅ Flight {flight.upper()} updated.", ephemeral=True)

@bot.tree.command(name="removeflight", description="Remove a flight from the RAA board")
@discord.app_commands.describe(flight="Select the flight to remove")
@discord.app_commands.autocomplete(flight=flight_autocomplete)
async def remove_flight(interaction: discord.Interaction, flight: str):
    if interaction.channel.id not in ALLOWED_SUBMIT_CHANNELS:
        await interaction.response.send_message("Wrong channel.", ephemeral=True)
        return

    target = next((d for d in departures if d['flight'].upper() == flight.upper()), None)

    if not target:
        await interaction.response.send_message(f"❌ Flight {flight.upper()} not found.", ephemeral=True)
        return

    departures.remove(target)
    await update_board()
    await interaction.response.send_message(f"✅ Flight {flight.upper()} removed.", ephemeral=True)

# ═══════════════════════════════════════════
# LIVE STATUS COMMANDS
# ═══════════════════════════════════════════




# ═══════════════════════════════════════════
# LIAISON NOTE COMMAND
# ═══════════════════════════════════════════

@bot.tree.command(name="liaisonnote", description="Post a liaison note with an optional private server link")
@discord.app_commands.describe(
    airline="Airline this note is about",
    note="The note or update to post",
    private_link="Optional private server link"
)
async def liaison_note(interaction: discord.Interaction, airline: str, note: str, private_link: str = None):
    staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
    liaison_role = interaction.guild.get_role(LIAISON_ROLE_ID)
    if staff_role not in interaction.user.roles and liaison_role not in interaction.user.roles:
        await interaction.response.send_message("Only staff or liaison members can post liaison notes.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"📝  Liaison Note — {airline.upper()}",
        description=note,
        color=RAA_GOLD
    )
    embed.add_field(name="Posted by", value=interaction.user.mention, inline=True)
    if private_link:
        embed.add_field(
            name="🔗  Private Server Link",
            value=f"[Click to join]({private_link})",
            inline=True
        )
    embed.set_footer(text="Roblox Aviation Alliance  ·  Liaison Notes")
    embed.timestamp = datetime.now(timezone.utc)

    await interaction.channel.send(embed=embed)
    # Update live status to reflect new note
    if live_flight:
        live_flight["note"] = note
        if private_link:
            live_flight["private_link"] = private_link
        await update_live_status()
    await interaction.response.send_message("✅ Note posted.", ephemeral=True)

# ═══════════════════════════════════════════
# BOT EVENTS
# ═══════════════════════════════════════════

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(BoardView())
    bot.loop.create_task(midnight_clear())
    await bot.tree.sync()

async def midnight_clear():
    while True:
        now = datetime.now(timezone.utc)
        seconds_until_midnight = (
            (23 - now.hour) * 3600 +
            (59 - now.minute) * 60 +
            (60 - now.second)
        )
        await asyncio.sleep(seconds_until_midnight)
        departures.clear()
        await update_board()
        print("Board cleared at midnight UTC")

@bot.event
async def on_message(message):
    if message.author.bot:
        await bot.process_commands(message)
        return

    if message.channel.id in WATCHED_ANNOUNCEMENT_CHANNELS:
        target = bot.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
        if not target:
            await bot.process_commands(message)
            return

        header = f"📢  **{message.guild.name}**  ·  [Original Message]({message.jump_url})\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        content = message.content if message.content else ""

        if content:
            await target.send(header + content)
        else:
            await target.send(header)

        for attachment in message.attachments:
            is_gif = attachment.filename.lower().endswith(".gif")
            if is_gif:
                await target.send(attachment.url)
            else:
                await target.send(f"📢  **{message.guild.name}**\n{attachment.url}")

    await bot.process_commands(message)

# ═══════════════════════════════════════════
# MISC COMMANDS
# ═══════════════════════════════════════════

@bot.command()
async def clear(ctx):
    if ctx.channel.id not in ALLOWED_SUBMIT_CHANNELS:
        await ctx.message.delete()
        return
    departures.clear()
    await update_board()
    await ctx.message.delete()

@bot.command()
async def setup(ctx):
    channel = bot.get_channel(BOARD_CHANNEL_ID)
    view = BoardView()
    msg = await channel.send(embed=build_embed(), view=view)
    print(f"Message ID: {msg.id}")

@bot.command()
async def setuplive(ctx):
    channel = bot.get_channel(LIVE_STATUS_CHANNEL_ID)
    msg = await channel.send(embed=build_live_status())
    print(f"Live Status Message ID: {msg.id}")
    await ctx.message.delete()

@bot.command()
async def directory(ctx):
    await ctx.message.delete()
    posted_messages = []

    for airline in AIRLINES:
        embed = discord.Embed(
            title=f"✈  {airline['name']}  ·  {airline['code']}",
            description=(
                f"{airline['description']}\n\n"
                f"**[Join Server]({airline['invite']})**"
            ),
            color=airline['color']
        )
        embed.set_footer(text="Roblox Aviation Alliance  ·  Member Airlines")
        msg = await ctx.channel.send(embed=embed)
        posted_messages.append((airline['name'], msg.jump_url))

    contents_lines = "\n".join(
        f"[{name}]({url})" for name, url in posted_messages
    )
    contents_embed = discord.Embed(
        title="📋  RAA AIRLINE DIRECTORY",
        description=(
            "**Roblox Aviation Alliance — Member Airlines**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Click an airline below to jump directly to their entry.\n\n"
            + contents_lines
        ),
        color=RAA_GOLD
    )
    contents_embed.set_footer(text=f"Roblox Aviation Alliance  ·  {len(AIRLINES)} Member Airlines")
    contents_embed.timestamp = datetime.now(timezone.utc)
    await ctx.channel.send(embed=contents_embed)

@bot.command()
async def postrules(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        description=(
            "**Rules & Regulations**\n\n"
            "**1.** Follow Discord's [Terms of Service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines).\n\n"
            "**2.** No hate speech, discrimination, or harassment of any kind.\n\n"
            "**3.** Respect all members regardless of rank, airline, or experience level.\n\n"
            "**4.** No spamming, excessive pinging, or flooding any channel.\n\n"
            "**5.** Keep conversations in their relevant channels.\n\n"
            "**6.** No advertising other servers without prior approval from RAA staff.\n\n"
            "**7.** Explicit, disturbing, or inappropriate content is strictly prohibited.\n\n"
            "**8.** Do not impersonate other members, airlines, or staff.\n\n"
            "**9.** All alliance decisions made by RAA leadership are final.\n\n"
            "**10.** Staff reserve the right to moderate at their discretion.\n\n"
            "**11.** Respect the rules and regulations of member airlines in their separate servers."
        ),
        color=RAA_GOLD
    )
    embed.set_footer(text="Roblox Aviation Alliance  ·  Last updated May 2026")
    await ctx.channel.send("https://i.imgur.com/RsxnW3c.png")
    await ctx.channel.send(embed=embed)
    await ctx.channel.send("https://i.imgur.com/wIK8BDE.png")

import os

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("No DISCORD_TOKEN found in environment variables")

bot.run(TOKEN)

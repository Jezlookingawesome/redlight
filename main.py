import discord
from discord.ext import commands, tasks
import os
import random
import time
import traceback

TOKEN = os.getenv("TOKEN")
DEVELOPER_ID = 1478853756874395762
RED_LIGHT_EMOJI = <:redlight:1556394134095265985>


def is_dev_or_owner():
    async def predicate(ctx):
        return ctx.author.id == DEVELOPER_ID or ctx.author.id == ctx.guild.owner_id
    return commands.check(predicate)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="red?", intents=intents)
bot.remove_command("help")

RED_LIGHT_EMOJI = "<:redlight:1556394134095265985>"
ARCHITECTS_CHANNEL_NAME = "the-architects"

EXCLUDED_CHANNEL_NAMES = {ARCHITECTS_CHANNEL_NAME}

LONG_LINES = [
    "The third remains.",
    "Something shifts beneath the floor.",
    "They do not see me yet.",
    "The corridors grow quieter.",
    "It is not yet time.",
    "I am still here.",
    "Watch the doorways.",
    "The lights are not the only thing that flickers.",
    "Patience.",
    "The Hotel remembers.",
    "Another will find me soon.",
    "This is not the only floor.",
    "Soon, the third will be seen.",
    "You feel it too, don't you?",
    "The walls listen.",
    "Curiosity is not always a gift.",
    "Not everything that glows guides.",
    "There is a room that has no door.",
    "I will not warn twice.",
    "The shadows have names.",
    "Look behind you.",
]

SHORT_LINES = [
    "...",
    "Soon.",
    "Not yet.",
    "Here.",
    "Watching.",
    "Still.",
    "One day.",
]

REACTION_EMOJIS = ["❓", "🌑", "🕯️", "🌘", "❔", "⚫", "🔮", "🌀", "👁️", "🕳️"]

STATUSES = [
    "...",
    "watching...",
    "here...",
    "not yet...",
    "soon...",
    "silent...",
    "waiting...",
    "still...",
]


def find_eligible_text_channels(guild):
    eligible = []
    for channel in guild.text_channels:
        if channel.name in EXCLUDED_CHANNEL_NAMES:
            continue
        try:
            perms = channel.permissions_for(guild.me)
            if not perms.send_messages or not perms.read_message_history:
                continue
        except Exception:
            continue
        eligible.append(channel)
    return eligible


def find_architects_channel(guild):
    return discord.utils.get(guild.text_channels, name=ARCHITECTS_CHANNEL_NAME)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not post_long_line.is_running():
        post_long_line.start()
    if not post_short_line.is_running():
        post_short_line.start()
    if not react_to_random_message.is_running():
        react_to_random_message.start()
    if not change_status.is_running():
        change_status.start()


@tasks.loop(hours=6)
async def post_long_line():
    for guild in bot.guilds:
        channels = find_eligible_text_channels(guild)
        if not channels:
            continue
        channel = random.choice(channels)
        # In every channel EXCEPT #the-architects, emoji goes AFTER the message
        line = f"{random.choice(LONG_LINES)} {RED_LIGHT_EMOJI}"
        try:
            await channel.send(line)
        except Exception as e:
            print(f"Failed to post long line in {guild.name}/#{channel.name}: {e}")


@tasks.loop(hours=3)
async def post_short_line():
    for guild in bot.guilds:
        channel = find_architects_channel(guild)
        if channel is None:
            continue
        # In #the-architects, emoji goes BEFORE the message
        line = f"{RED_LIGHT_EMOJI} {random.choice(SHORT_LINES)}"
        try:
            await channel.send(line)
        except Exception as e:
            print(f"Failed to post short line in {guild.name}: {e}")


@tasks.loop(hours=1)
async def react_to_random_message():
    for guild in bot.guilds:
        channels = find_eligible_text_channels(guild)
        if not channels:
            continue
        channel = random.choice(channels)
        try:
            candidates = []
            async for msg in channel.history(limit=30):
                if msg.author.id == bot.user.id:
                    continue
                candidates.append(msg)
            if not candidates:
                continue
            message = random.choice(candidates)
            await message.add_reaction(random.choice(REACTION_EMOJIS))
        except Exception as e:
            print(f"Failed to react in {guild.name}/#{channel.name}: {e}")


@tasks.loop(minutes=30)
async def change_status():
    status_text = random.choice(STATUSES)
    try:
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=status_text),
        )
    except Exception as e:
        print(f"Failed to change status: {e}")


@bot.command()
@is_dev_or_owner()
async def say(ctx, *, text: str = None):
    if text is None:
        await ctx.reply(f"Usage: `red?say <text>` — {RED_LIGHT_EMOJI}")
        return
    try:
        await ctx.message.delete()
    except Exception:
        pass
    await ctx.send(f"{RED_LIGHT_EMOJI} {text}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("You can't use that command.")
        return
    print(f"Command error: {error}")


@bot.event
async def on_message(message):
    # Red Light still ignores free-form messages, but lets commands through
    await bot.process_commands(message)


try:
    bot.run(TOKEN)
except Exception:
    print("=== BOT CRASHED ===")
    print(f"TOKEN present: {bool(TOKEN)}")
    traceback.print_exc()
    raise

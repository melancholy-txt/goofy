import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$#!", intents=intents)

async def load_extensions():
    await bot.load_extension("cogs.general")
    await bot.load_extension("cogs.games")
    await bot.load_extension("cogs.reactions")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    await ctx.send("Syncing commands...")
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"Successfully synced {len(synced)} slash command(s) globally!")
    except Exception as e:
        await ctx.send(f"Failed to sync commands: {e}")

@sync.error
async def sync_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("Error: You are not recognized as the bot owner!")
    else:
        await ctx.send(f"An error occurred: {error}")

@bot.command(name="reload")
@commands.is_owner()
async def reload(ctx, cog_name: str):
    await ctx.send(f"Reloading `cogs.{cog_name}`...")
    try:
        await bot.reload_extension(f"cogs.{cog_name}")
        await ctx.send(f"Successfully reloaded `cogs.{cog_name}`!")
    except Exception as e:
        await ctx.send(f"Failed to reload cog: {e}")

@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("Error: You are not recognized as the bot owner!")
    else:
        await ctx.send(f"An error occurred: {error}")

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("Error: DISCORD_TOKEN environment variable not set!")
            print("Please set your Discord bot token as an environment variable.")
            exit(1)
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())

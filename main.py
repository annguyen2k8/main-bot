from discord.ext import commands    
from discord import app_commands
import discord

import os
import asyncio
import logging
from datetime import datetime

from config import *

os.system('cls' if os.name == 'nt' else 'clear')



logger = logging.getLogger('discord') 
logger.setLevel(logging.INFO) 

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        fmt= '\33[90m%(asctime)s \33[0m\33[94m%(levelname)s\33[0m \33[95m%(name)s\33[0m %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    )

logger.addHandler(handler)

bot = commands.Bot(
    command_prefix=command_prefix,
    intents=discord.Intents.all(), 
    help_command=None
    )

@bot.event
async def on_ready():
    global handler
    logger = logging.getLogger('discord.on_ready') 
    logger.info(f'Ping {round(bot.latency * 1000)}ms')
    logger.info(f"Logged bot's {bot.user} (ID: {bot.application.id})")
    await asyncio.gather(
        sync_cmd(), 
        loop_status()
    )

async def sync_cmd() -> None:
    try:
        sync = await bot.tree.sync()
        logger = logging.getLogger('discord.commands') 
        logger.info(f"{len(sync)} commands")
    except Exception as e:
        logger.error(e)

async def loop_status() -> None:
    status = [
        "type in \"!help\" for help.", 
        "{:1.0f} guilds | with {:1.0f} users".format(
            len(bot.guilds),
            sum([guild.member_count for guild in bot.guilds])
            )
        ]
    
    while True:
        for name in status:
            await bot.change_presence(
                status=discord.Status.online, 
                activity=discord.CustomActivity(name=name))
            await asyncio.sleep(30)

@bot.hybrid_command(description='Get ping from host to discord.com')
async def ping(ctx:commands.Context) -> None:
    await ctx.reply(f'**Pong!** {round(bot.latency*1000)}ms')

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if ctx.author.id == bot.application.owner.id:
        await ctx.reply(f'```{error}```')

@commands.hybrid_command(name='reload_extension', description='just owner use.')
async def reload_extension(ctx: commands.Context):
    if ctx.author.id  == bot.application.owner.id:
        return await ctx.reply('No permission!')
    logger = logging.getLogger('discord.cogs') 
    
    for folder in os.listdir('./cogs'):
        await bot.reload_extension(f'cogs.{folder}.main')
        logger.info(f'{folder} is reloaded!')
        
    await ctx.reply('all extensions war reloaded!', ephemeral=True)

async def load_cogs():
    logger = logging.getLogger('discord.cogs') 
    os.makedirs('cogs', exist_ok=True)
    for folder in os.listdir('./cogs'):
        await bot.load_extension(f'cogs.{folder}.main')
        logger.info(f'{folder} is loaded!')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(token=token)

asyncio.run(main()) 
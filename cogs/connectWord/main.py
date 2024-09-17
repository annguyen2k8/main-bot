fr"""
     _______  _______  __    _  __    _  _______  _______  _______ 
    |       ||       ||  |  | ||  |  | ||       ||       ||       |
    |       ||   _   ||   |_| ||   |_| ||    ___||       ||_     _|
    |       ||  | |  ||       ||       ||   |___ |       |  |   |  
    |      _||  |_|  ||  _    ||  _    ||    ___||      _|  |   |  
    |     |_ |       || | |   || | |   ||   |___ |     |_   |   |  
    |_______||_______||_|  |__||_|  |__||_______||_______|  |___|  
     _     _  _______  ______    ______                            
    | | _ | ||       ||    _ |  |      |          Version: 1.0v        
    | || || ||   _   ||   | ||  |  _    |         Author:  Kasakun1901    
    |       ||  | |  ||   |_||_ | | |   |         From: Main's project
    |       ||  |_|  ||    __  || |_|   |         Mode: developing
    |   _   ||       ||   |  | ||       |         
    |__| |__||_______||___|  |_||______|                           
"""

import discord
from discord import app_commands
from discord.ext import commands

import os
import time
import typing
import aiosqlite

from string import ascii_lowercase
from random import choice

class connectWord(commands.Cog):
    folder = os.path.dirname(__file__)
    file_db = 'database/connectword.db'
    os.makedirs('database', exist_ok=True)

    def get_dictionary(self) -> list[str]:
        with open(os.path.join(self.folder, 'dictionary.txt'), 'r') as f:
            return f.read().split('\n')
    
    def randomASCII(self) -> str:
        return choice(ascii_lowercase)
    
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.dictionary = self.get_dictionary()
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        async with aiosqlite.connect(self.file_db) as db:
            async with db.cursor() as cursor:
                await cursor.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS
                    CHANNELS(
                        guildID INT PRIMARY KEY,
                        channelID INT
                    );
                    
                    CREATE TABLE IF NOT EXISTS
                    LAST(
                        guildID INT,
                        userID INT,
                        time DATETIME,
                        letter STR
                    );
                    
                    CREATE TABLE IF NOT EXISTS
                    WORDS_USED(
                        word STR,
                        guildID INT
                    );
                    
                    CREATE TABLE IF NOT EXISTS
                    USERS(
                        userID INT,
                        guildID INT,
                        exp INT,
                        UNIQUE(userID, guildID)
                    );
                    
                    CREATE TRIGGER IF NOT EXISTS after_insert_channels
                    AFTER INSERT ON CHANNELS
                    FOR EACH ROW
                    BEGIN
                        INSERT OR IGNORE INTO LAST(guildID, userID, time, letter)
                        VALUES (NEW.guildID, NULL, NULL, NULL);
                    END;
                    """
                    )
            await db.commit()

    async def set_channel(self, guildID:int, channelID:int) -> None:
        async with aiosqlite.connect(self.file_db) as db:
            async with db.cursor() as cursor:
                data = await self.get_channel(guildID)
                if not data:
                    await cursor.execute(
                        """
                        INSERT INTO CHANNELS VALUES (?, ?)
                        """, (guildID, channelID)
                        )
                else:
                    await cursor.execute(
                        """
                        UPDATE CHANNELS
                        SET channelID = ?
                        WHERE guildID = ?
                        """, (channelID, guildID)
                    )
            await db.commit()
    
    async def get_channel(self, guildID: int) -> int:
        async with aiosqlite.connect(self.file_db) as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT channelID FROM CHANNELS WHERE guildID = ?", (guildID,))
                data = await cursor.fetchone()
                if not data:
                    return None
                return data[0]
    
    async def set_last(
            self, 
            guildID:int,
            userID:int=None, 
            lastTime:float=None, 
            letter:str=None
            ) -> None:
        async with aiosqlite.connect(self.file_db) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    """
                    UPDATE LAST
                    SET userID = ?,
                        time = ?,
                        letter = ?
                    WHERE guildID = ?
                    """, (userID, lastTime, letter, guildID)
                )
            await db.commit()
    
    async def get_last(self, guildID: int) -> tuple[int, float, str]:
        async with aiosqlite.connect(self.file_db) as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT userID, time, letter FROM LAST WHERE guildID = ?", (guildID,))
                data = await cursor.fetchone()
                return data
    
    async def add_wordUsed(self, guildID:int, word:str) -> None:
        async with aiosqlite.connect(self.file_db) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO WORDS_USED VALUES(?, ?)",
                    (guildID, word)
                    )
            await db.commit()
    
    async def get_wordsUsed(self, guildID: int) -> list[str]:
        async with aiosqlite.connect(self.file_db) as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT word FROM WORDS_USED WHERE guildID = ?", (guildID,))
                data = await cursor.fetchone()
                if not data:
                    return []
                return list(map(lambda x: x[0], data))
    
    async def clear_wordsUsed(self, guildID:int) -> None:
        async with aiosqlite.connect(self.file_db) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "DELETE FROM WORDS_USED WHERE guildID = ?", 
                    (guildID,)
                    )
            await db.commit()
    
    async def add_exp(self, guildID:int, userID:int, exp:int=0) -> None:
        async with aiosqlite.connect(self.file_db) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT INTO USERS (guildID, userID, exp)
                    VALUES (?, ?, ?)
                    ON CONFLICT(userID, guildID) DO UPDATE
                    SET exp = exp + ? WHERE guildID = ?;
                    """,
                    (guildID, userID, exp, exp, guildID)
                    )
            
            await db.commit()
    
    async def get_top(self, guidID:int) -> list[tuple[int, int]]:
        ...
    
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message) -> None:
        if message.author.bot:
            return
        
        guildID = message.guild.id
        channelID = await self.get_channel(guildID)
        
        if message.channel.id != channelID:
            return
        
        prefix = self.bot.command_prefix
        if prefix in message.content[0:len(prefix)]:
            return
        
        lastUserID, lastTime, lastLetter = await self.get_last(guildID)
        
        time_gap = (time.time() - lastTime) if lastTime else 0
        
        if (lastUserID == message.author.id and
            time_gap < 3):
            await message.add_reaction('❌')
            await message.reply(f'You must wait for **``{round(time_gap, 2)}s``** or someone answer!', delete_after=10)
            return
        
        word = message.content.split()[0]
        if word[0] != lastLetter:
            await message.add_reaction('❌')
            await message.reply(f'Your word must start with letter {lastLetter}!', delete_after=10)
            return
        
        if word not in self.dictionary:
            await message.add_reaction('❌')
            await message.reply(f'**``{word}``** not in dictionary!', delete_after=10)
            return

        words_used = await self.get_wordsUsed(guildID)

        if word in words_used:
            await message.add_reaction('❌')
            await message.reply(f'**``{word}``** is used!', delete_after=10)
            return
    
        userID = message.author.id
        await self.set_last(guildID, userID, time.time(), word[-1])
        await self.add_exp(guildID, userID, 10)
        
        await message.add_reaction('✅')
    
    @commands.hybrid_command(name='start_connectword', description='Start mini-game connect word')
    @commands.has_permissions(administrator=True)
    async def start(self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]) -> None:
        guildID  = ctx.guild.id
        channelID = ctx.channel.id if not channel else channel
        await self.set_channel(guildID, channelID)
        
        if not ctx.interaction:
            await ctx.message.add_reaction('✅')
        
        letter = self.randomASCII()
        await self.set_last(guildID,letter=letter)
        message = await ctx.reply(f'Game started! The start letter is **``{letter}``**')
        
        await message.add_reaction('🔥')
        await message.add_reaction('🧠')
    
    @commands.hybrid_command(name='top', description='Show top board.')
    async def top(self, ctx: commands.Context) -> None:
        ...

"""
NOTE: PLEASE PUT IT IN TRASH AS SOON AS WELL
"""

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(connectWord(bot))
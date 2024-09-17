import os
import asyncio
import random

import discord 

from discord import app_commands
from discord.ext import commands

from discord import ui
from discord import ButtonStyle

class CogTictactoe(commands.Cog):
    folder = os.path.dirname(__file__)
    file_db = 'database/MinigameCaro.db'
    os.makedirs('database', exist_ok=True)
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.hybrid_command(name='tictactoe', description='Try it.')
    async def tictactoe(self, ctx: commands.Context) -> None:
        queue_view = QueueView(TicTacToe)
        await queue_view.create_queue(ctx)

class TicTacToeButton(ui.Button['TicTacToe']):
    def __init__(self, x:int, y: int) -> None:
        super().__init__(
            style=discord.ButtonStyle.secondary, 
            label='\u200b', 
            row=y
            )
        
        self.x = x
        self.y = y
    
    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return
        
        

class TicTacToe(ui.view):
    childen = list[TicTacToeButton]
    name:str = __qualname__
    limit:int = 2
    O = 1
    X = -1
    Tie = 2
    
    def __init__(self, players:list[int]) -> None:
        super().__init__()
        
        players = random.shuffle(players)
        
        self.players = {
            players[0]:self.O,
            players[1]:self.X
        }
        
        self.turn = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToe(x, y))
    
    def check_status(self) -> int|None:
        for across in self.board:
            i = sum(across)
            if i == 3:
                return self.O
            if i == -3:
                return self.X
        
        for line in range(3):
            i = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if i == 3:
                return self.O
            elif i == -3:
                return self.X
        
        i = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if i == 3:
            return self.O
        elif i == -3:
            return self.X

        i = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if i == 3:
            return self.O
        elif i == -3:
            return self.X
        
        if all(i != 0 for row in self.board for i in row):
            return self.Tie
        
        return None
    
    def get_embed(self) -> None:
        embed = discord.Embed(
            title="Tic Tac Toe!",
            description=f"**<@{self.turn}> turn!**"
        )
        return embed
    
    async def start(self, channel: discord.TextChannel) -> None:
        await channel.send(embed=self.get_embed(), view=self)

class QueueView(ui.View):
    def __init__(self, game, timeout:int=180) -> None:
        super().__init__(timeout=timeout)
        self.players:list[int] = []
        self.game = game
        
        self.isReady = False
    
    async def create_queue(self, ctx: commands.Context) -> None:
        self.append_player(ctx.author)
        self.message = await ctx.send(embed=self.create_embed(), view=self)
    
    def append_player(self, user: discord.User):
        if user.id in self.players:
            return
        self.players.append(user.id)
    
    def create_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f'Queue {self.game.name} ({len(self.players)}/{self.game.limit})'
        )
        
        for i, id in enumerate(self.players, 1):
            embed.add_field(
                name=f'player {i}',
                value=f'<@{id}>'
                )
        return embed

    async def update_buttons(self) -> None:
        if len(self.players) < self.game.limit:
            return
        
        self.join_queue.disabled = True
        self.isReady = True
    
    @ui.button(label='Join', style=ButtonStyle.secondary)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.append_player(interaction.user)
        
        await self.update_buttons()
        await self.message.edit(embed=self.create_embed(), view=self)
        
        if not self.isReady:
            return
        
        await asyncio.sleep(3)
        await self.message.delete()
        
        channel = interaction.channel
        await channel.send(''.join([f'<@{id}>' for id in self.players]))
        
        game = self.game(self.players)
        await game.start(channel)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CogTictactoe(bot))
import os

import disnake

from datetime import datetime as dt

from disnake import ButtonStyle
from loguru import logger
from disnake.ext import commands


class Button(disnake.ui.View):
     def __init__(self):
          super().__init__(timeout=None)
          
     @disnake.ui.button(label='Добавить бота', style=ButtonStyle.link, url=os.environ('LINK'))
     async def button1(self, button: disnake.ui.Button, inter: disnake.CmdInter):
          logger.info(f'{inter.author.name} add bot on new server.')
          self.stop()
          
          

class HelpCog(commands.Cog):
     def __init__(self, bot: commands.Bot):
          self.bot = bot
          
          
     @commands.slash_command(description='Помощь по командам')
     @logger.catch
     async def help_me(self, inter: disnake.CmdInter, command: str = None):
          cmd = ['show', 'mine', 'monitoring']
          
          with open('CommandsHelp', 'r', encoding='utf-8') as file:
               reader = file.read().split('1')
          
          if command:
               if command in cmd:  
                    commands_ = {
                         'mine': reader[1],
                         'show': reader[0],
                         'monitoring': reader[2],
                    }
                         
                    emb = disnake.Embed(
                              description=commands_[command],
                              colour=disnake.Colour.dark_magenta(),
                              timestamp=dt.now()
                    )
                    return await inter.send(embed=emb, ephemeral=True)
               
               else:
                    return await inter.send('Такой команды не существует!', ephemeral=True)
          
          emb = disnake.Embed(
               description=reader[3],
               colour=disnake.Colour.dark_magenta(),
               timestamp=dt.now(),
          )
          view = Button()
          await inter.send(embed=emb, ephemeral=True, view=view)
          
          
          
          
          
          
def setup(bot: commands.Bot):
     bot.add_cog(HelpCog(bot))
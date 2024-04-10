import os

import disnake

from disnake.ext import commands
from loguru import logger


bot = commands.Bot(
    command_prefix = '<', 
    help_command = None, 
    intents = disnake.Intents.all(),
    activity = disnake.Activity(name='CS2')
)


@bot.event
async def on_ready():
     print(f'Bot {bot.user.name} read!')
     
     for file in os.listdir('./Cogs'):
          if file.endswith('.py'):
               bot.load_extension(f'Cogs.{file[:-3]}')
               print(f'[+] {file}')
               
     logger.info(f'{bot.user.name} working success!')

            

if __name__ == '__main__':
    bot.run(os.environ('TOKEN'))
   


import asyncio

import disnake
import aiosqlite

from typing import Optional
from json import loads
from datetime import datetime as dt

from disnake.ext import commands
from numba import prange
from loguru import logger

from Scripts import script_steam as cs
from Vidgets import ButtonsForPage as bt

   
class TaskCog(commands.Cog):
     def __init__(self, bot: commands.Bot):
          self.bot = bot
         
     @logger.catch
     async def get_data(self, author: disnake.Member, guild: disnake.Guild):          
          async with aiosqlite.connect('projectbot.db') as db:
               user_items: dict[str] = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(guild.id), [author.id])
               news = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(guild.id), [author.id])
               
               user_items = await user_items.fetchone()
               user_items = loads(user_items[0])
               
               news = await news.fetchone()
               news = loads(news[0])
               
          request: list[str] = await cs.get_item(user_items, [])
          embeds: list[disnake.Embed] = []
                         
          if request is False:
               return
               
          for data in prange(len(request)):
               emb = disnake.Embed(
                    title=request[data][0],
                    timestamp=dt.now()
               )
               emb.set_thumbnail(url=request[data][2])
               emb.set_footer(text=f'Item {data + 1}/{len(request)}')
               
               emb.add_field(name='Кол-во предмета', value=f'{news[request[data][0]][2]}шт', inline=False)
               emb.add_field(name='Цена за которую вы купили 1шт', value=f'{news[request[data][0]][0]}р', inline=False)
               emb.add_field(name='Цена сейчас на стиме за 1шт', value=f'{request[data][1]}р', inline=False)
               
               value_user = news[request[data][0]][2] * int(news[request[data][0]][0])
               value_steam = news[request[data][0]][2] * request[data][1]
               benefit = round(((int(value_steam) - value_user) / value_user) * 100, 1)
               
               emb.add_field(name='Общая стоимость по ваше цене', value=f'{value_user}р', inline=False)
               emb.add_field(name='Общая стоимость по Steam', value=f'{value_steam}р', inline=False)
               
               if benefit >= 0:
                    emb.colour = disnake.Colour.green()
                    emb.add_field(name='Прибыль', value=f'{benefit}%', inline=False)
               
               elif benefit < 0:
                    emb.colour = disnake.Colour.red()
                    emb.add_field(name='Убыток', value=f'{benefit}%', inline=False)
                              
               embeds.append(emb)
          
          await self.show_data(author, embeds)
          
          
     @logger.catch
     async def show_data(author: disnake.Member, embeds: list[disnake.Embed]):
          view = bt.Button()
          message = await author.send(embed=embeds[0], view=view)
          await view.wait()
        
          page = 0
          while True:
               if view.pagination == 'Right':
                    if page == len(embeds) - 1:
                         page = 0
                                   
                    else:
                         page += 1
                                   
                    view = bt.Button()
                    await message.edit(embed=embeds[page], view=view)
                    await view.wait()
                                   
               if view.pagination == 'Left':
                    if page == 0: 
                         page = len(embeds) - 1
                                   
                    else:
                         page -= 1
                                   
                    view = bt.Button()
                    await message.edit(embed=embeds[page], view=view)
                    await view.wait()
                                   
               if view.pagination == 'Stop':
                    return await message.delete()
          
               
     @logger.catch
     async def wait(self, author: disnake.Member, guild: disnake.Guild, value: str): 
          if value == 'Yes':
               while value != 'No':
                    async with aiosqlite.connect('projectbot.db') as db:
                         value = await db.execute("SELECT mont FROM server{} WHERE id = ?".format(guild.id), [author.id])
                         value = await value.fetchone()
                         value = value[0]
                    
                    await self.get_data(author, guild)
                    await asyncio.sleep(30)
          
     
     @commands.slash_command(description='Вкл/Выкл мониторинг')
     @logger.catch
     async def monitoring(self, inter: disnake.CmdInter):
          async with aiosqlite.connect('projectbot.db') as db:
               flag: Optional[str] = None
               
               
               value = await db.execute("SELECT mont FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
               value = await value.fetchone()
               
               if value[0] == 'No':
                    flag = 'Yes'
                    
               else:
                    flag = 'No'
                    
               await db.execute("UPDATE server{} SET mont = ? WHERE id = ?".format(inter.guild.id), [flag, inter.author.id])
               await db.commit()
               
               if flag == 'Yes':
                    inventory = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
                    inventory = await inventory.fetchone()
                    inventory = loads(inventory[0])
                    
                    if len(inventory) <= 0:
                         return await inter.send(f'Добавьте предмет в инвентарь чтобы получать оповещения о ваших предметах.', ephemeral=True)
          
          await inter.send(f'Вы успешно поменяли значение мониторинга на ``{flag}``.', ephemeral=True)
          await self.wait(inter.author, inter.guild , flag)
          
     
     @commands.slash_command(description='Просмотр цен на ваши предметы')
     @logger.catch
     async def show(self, inter: disnake.CmdInter):
          await inter.response.defer(ephemeral=True)
          await inter.delete_original_response()
          
          async with aiosqlite.connect('projectbot.db') as db:
               inventory = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
               inventory = await inventory.fetchone()
               inventory = loads(inventory[0])
               
          if len(inventory) > 0:
               await self.get_data(inter.author, inter.guild)
               
          else:
               await inter.send('Ваш инвентарь пуст! Добавьте туда предметы.', ephemeral=True)
        
          
          
def setup(bot: commands.Bot):
     bot.add_cog(TaskCog(bot))
     
     
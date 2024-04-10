import json

import disnake
import aiosqlite

from disnake.ext import commands
from loguru import logger


class CogGuildMember(commands.Cog):
     def __init__(self, bot: commands.Bot):
          self.bot = bot
          
     @commands.Cog.listener()
     @logger.catch
     async def on_guild_join(self, guild: disnake.Guild):
          async with aiosqlite.connect('projectbot.db') as db:
               await db.execute("""CREATE TABLE IF NOT EXISTS server{}(
                    id INT,
                    name STR,
                    inv TEXT,
                    mont STR
               )""".format(guild.id))
               await db.commit()
               
               for member in guild.members:
                    if not member.bot:
                         await db.execute("INSERT INTO server{} VALUES(?, ?, ?, ?)".format(guild.id), [member.id, member.name, json.dumps({}), 'No'])
                         await db.commit()
          
          general = disnake.utils.get(guild.text_channels, name='general')
          if general:
               await general.send('Готов вам помогать!')
               
          logger.debug(f'base for {guild.name} created success!')
          
               
     @commands.Cog.listener()
     @logger.catch
     async def on_guild_remove(self, guild: disnake.Guild):
          async with aiosqlite.connect('projectbot.db') as db:
               await db.execute("DROP TABLE IF EXISTS server{}".format(guild.id))
               await db.commit()
          
          logger.debug(f'base for {guild.name} deleted success!')
          
     @commands.Cog.listener()
     @logger.catch
     async def on_member_join(self, member: disnake.Member):
          if not member.bot:
               async with aiosqlite.connect('projectbot.db') as db:
                    await db.execute("INSERT INTO server{} VALUES(?, ?, ?, ?)".format(member.guild.id), [member.id, member.name, json.dumps({}), 'No'])
                    await db.commit()
                    
               logger.debug(f'New data for {member.name} on server {member.guild.name}')
          
          
     @commands.Cog.listener()
     @logger.catch
     async def on_member_remove(self, member: disnake.Member):
          if not member.bot:
               async with aiosqlite.connect('projectbot.db') as db:
                    await db.execute("DELETE FROM server{} WHERE id = ?".format(member.guild.id), [member.id])
                    await db.commit()
                    
               logger.debug(f'Deleted data for {member.name} on server {member.guild.name}')
          
          
def setup(bot: commands.Bot):
     bot.add_cog(CogGuildMember(bot))
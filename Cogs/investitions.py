
import disnake 
import aiosqlite

from json import loads
from datetime import datetime as dt

from disnake.ext import commands
from loguru import logger

from vidgets_investitions import AddItem as add
from vidgets_investitions import DeleteItem as dl
            
            
class InvestCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        
    @commands.slash_command(description='Панель для управления предметами')
    @logger.catch
    async def mine(self, inter: disnake.CmdInter):
        await inter.response.defer(ephemeral=True)
        
        async with aiosqlite.connect('projectbot.db') as db:
            monitoring = await db.execute("SELECT mont FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
            list_portfel = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
            
            list_portfel = await list_portfel.fetchone()
            monitoring = await monitoring.fetchone()
        
        emb = disnake.Embed(
            title='Ваш портфель с предметами',
            colour=disnake.Colour.dark_magenta(),
            timestamp=dt.now()
        )
        emb.add_field(name='Кол-во предметов:', value=len(loads(list_portfel[0])))
        emb.add_field(name='Мониторинг:', value=monitoring[0])
        
        view = add.ButtonsCog()
        await inter.send(embed=emb, ephemeral=True, view=view)
        
        

def setup(bot: commands.Bot):
    bot.add_cog(InvestCog(bot))
    
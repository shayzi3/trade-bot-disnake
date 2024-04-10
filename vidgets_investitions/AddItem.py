
import disnake
import aiosqlite

from typing import Optional
from json import loads, dumps

from disnake import ButtonStyle, SelectOption, TextInputStyle
from disnake.ui import TextInput
from numba import prange
from loguru import logger

from vidgets_investitions import DeleteItem as dl
from Scripts import script_steam as sc

class ButtonsCog(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value: Optional[bool] = None
        
    @disnake.ui.button(label='Добавить предметы', emoji='➕', style=ButtonStyle.blurple)
    async def button1(self, button: disnake.ui.Button, inter: disnake.CmdInter):
        await inter.response.send_modal(ModalCog())
        
    @disnake.ui.button(label='Инвентарь', emoji='📔', style=ButtonStyle.blurple)
    async def button2(self, button: disnake.ui.Button, inter: disnake.CmdInter):
        async with aiosqlite.connect('projectbot.db') as db:
            data = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
            data = await data.fetchone()
            
        view = dl.SelectViewDropdown(loads(data[0]))
        await inter.send(view=view, ephemeral=True)
        
        
class ButtonYesNo(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.option: Optional[bool] = None
        
    @disnake.ui.button(emoji='✅', style=ButtonStyle.blurple)
    async def button1(self, button: disnake.ui.Button, inter: disnake.CmdInter):
        await inter.response.defer()
        self.option = True
        self.stop()
        
        
    @disnake.ui.button(emoji='❌', style=ButtonStyle.blurple)
    async def button2(self, button: disnake.ui.Button, inter: disnake.CmdInter):
        await inter.response.defer()
        await inter.delete_original_response()
        
        
class SelectMenuModal(disnake.ui.Select):
    def __init__(self, data: list[str]):
        self.urls = {}
        for i in data:
            self.urls[i[0]] = [i[1], i[2]]
            
        options = [SelectOption(label=f'{data[item][0]} Price: {data[item][1]}', value=data[item][0]) for item in prange(len(data))]
        super().__init__(placeholder='Выберите предмет', options=options)
        
    @logger.catch
    async def callback(self, inter: disnake.CmdInter):
        await inter.response.defer(ephemeral=True)
        
        values: list[str] = inter.values[0]
        
        async with aiosqlite.connect('projectbot.db') as db:            
            table = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
            table: tuple = await table.fetchone()
            table: dict = loads(table[0])
            
            if len(table) == 25:
                return await inter.send('Невозможно поместить в инвентарь больше 25 предметов!', ephemeral=True)
            
            if values[0] not in table:
                view = ButtonYesNo()
                emb = disnake.Embed(title=f'{values}', description=f'Цена: {self.urls[values][0]}', colour=disnake.Colour.dark_magenta())
                emb.set_image(url=self.urls[values][1])
                
                await inter.send(embed=emb, view=view, ephemeral=True)
                await view.wait()
                
                if view.option:
                    table[values] = [self.urls[values][0], self.urls[values][1], 1]
                    
                    await db.execute("UPDATE server{} SET inv = ? WHERE id = ?".format(inter.guild.id), [dumps(table), inter.author.id])
                    await db.commit()
                    
                    await inter.send(f'Предмет ``{values}`` успешно добавлен!', ephemeral=True)
                    
                    logger.debug(f'New data {values} at {inter.author.name}. Server: {inter.guild.name}.')
                
            else:
                await inter.send(f'Предмет ``{values}`` уже есть в вашем портфеле!', ephemeral=True)
                
                

class SelectViewModal(disnake.ui.View):
    def __init__(self, data: list[str]) -> None:
        super().__init__(timeout=None)
        self.add_item(SelectMenuModal(data))
        
        


class ModalCog(disnake.ui.Modal):
    def __init__(self):
        components = [
            TextInput(
                label='Название предмета',
                custom_id='text',
                style=TextInputStyle.short,
                placeholder='Введите название предмета',
                max_length=50
            )
        ]
        super().__init__(title='Поиск предметов по Steam', components=components)
        
    @logger.catch
    async def callback(self, inter: disnake.CmdInter):
        await inter.response.defer(ephemeral=True)
        
        values: dict = inter.text_values
        search = await sc.get_page(values['text'])
        
        if search is False:
            return await inter.send(f'Предмет ``{values["text"]}`` не найден!', ephemeral=True)
        
        view = SelectViewModal(search)
        await inter.send(view=view, ephemeral=True)
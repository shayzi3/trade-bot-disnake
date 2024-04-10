
import disnake
import aiosqlite

from typing import Optional
from json import loads, dumps

from disnake import ButtonStyle, SelectOption
from disnake import TextInputStyle
from disnake.ui import Button, button, TextInput
from loguru import logger



class ModalButtonChange(disnake.ui.Modal):
    def __init__(self, key_item: str, dict_: str):
        self.key = key_item
        self.dict_ = dict_
        
        components = [
            TextInput(
                label='Цена',
                custom_id='price',
                style=TextInputStyle.short,
                placeholder='Введите желаемую цену',
                max_length=7
            )
        ]
        super().__init__(title='Смена цены предмета', components=components)
        
    @logger.catch
    async def callback(self, inter: disnake.CmdInter):
        values: dict[str, int] = inter.text_values
        
        if values['price'].isdigit():
            async with aiosqlite.connect('projectbot.db') as db:
                items = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
                items: tuple = await items.fetchone()
                items: dict = loads(items[0])
                
                before = items[self.key][0]
                items[self.key] = [values['price'], self.dict_[1], self.dict_[2]]
                
                await db.execute("UPDATE server{} SET inv = ? WHERE id = ?".format(inter.guild.id), [dumps(items), inter.author.id])
                await db.commit()
            
            await inter.send(f'Смена цены прошла успешно! Цена ``{self.key}`` теперь стала ``{values["price"]}``.', ephemeral=True)
            logger.debug(f'Member {inter.author.name} changed price at item {self.key}. Before {before}, after: {values["price"]}. Server: {inter.guild.name}')
            
        else:
            await inter.send(f'``{values["price"]}`` - это не число!', ephemeral=True)
        

class ButtonsSelect(disnake.ui.View):
    def __init__(self, key: str, data_: str):
        self.value: Optional[bool] = None
        self.key = key
        self.data_ = data_
        
        super().__init__(timeout=None)
        
    @button(label='Изменить цену', emoji='✏️', style=ButtonStyle.blurple)
    async def button1(self, button: Button, inter: disnake.CmdInter):
        await inter.response.send_modal(ModalButtonChange(self.key, self.data_))

        
    @button(label='Удалить предмет', emoji='➖', style=ButtonStyle.blurple)
    async def button2(self, button: Button, inter: disnake.CmdInter):
        await inter.response.defer()
        self.value = False
        self.stop()
        
    @button(label='Изменить кол-во', emoji='🔁', style=ButtonStyle.blurple)
    async def button3(self, button: disnake.ui.Button, inter: disnake.CmdInter):
       await inter.response.send_modal(ModalChangeQuantity(self.key, self.data_))
       

class ModalChangeQuantity(disnake.ui.Modal):
    def __init__(self, value: str, data_value: dict):
        self.value = value
        self.data_value = data_value
        
        components = [
            TextInput(
                label='Количество',
                custom_id='quantity',
                style=TextInputStyle.short,
                placeholder='Введите кол-во предмета',
                max_length=5
            )
        ]
        super().__init__(title='Кол-во предмета', components=components)
        
    async def callback(self, inter: disnake.CmdInter):
        values = inter.text_values
        
        if values['quantity'].isdigit():
            if int(values['quantity']) <= 10000:
                async with aiosqlite.connect('projectbot.db') as db:
                    data = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
                    data = await data.fetchone()
                    data = loads(data[0])
                    
                    data[self.value] = [self.data_value[0], self.data_value[1], int(float(values['quantity']))]
                
                    await db.execute("UPDATE server{} SET inv = ? WHERE id = ?".format(inter.guild.id), [dumps(data), inter.author.id])
                    await db.commit()
                
                await inter.send(f'Вы изменили количество предмета ``{self.value}`` на число ``{values["quantity"]}``.', ephemeral=True)
                
            else:
                await inter.send('Максимальное число для ввода - 10 000!', ephemeral=True)
            
        else:
            await inter.send('Введены неправильные данные!', ephemeral=True)  
        

class SelectMenu(disnake.ui.Select):
    def __init__(self, data_cog: dict[str, int]):
        self.data = data_cog
        
        if self.data:
            options: list[SelectOption] = [SelectOption(label=name, value=name) for name in self.data]
        if not self.data:
            options: list[SelectOption] = [SelectOption(label='Пусто', value='clear', emoji='🧹')]
        
        super().__init__(placeholder='Ваши предметы', options=options)
        
    
    @logger.catch
    async def callback(self, inter: disnake.CmdInter):
        await inter.response.defer(ephemeral=True)
        
        values = inter.values[0]
        
        if values == 'clear':
            return
        
        async with aiosqlite.connect('projectbot.db') as db:
            items = await db.execute("SELECT inv FROM server{} WHERE id = ?".format(inter.guild.id), [inter.author.id])
            items = await items.fetchone()
            items = loads(items[0])
            
        if values not in items:
            return await inter.send('Этого предмета нет в вашем инвентаре!', ephemeral=True)
        
        view = ButtonsSelect(values, items[values])
        
        emb = disnake.Embed(title=f'Предмет ``{values}``', colour=disnake.Colour.dark_magenta())
        
        emb.add_field(name='Закупочная цена 1шт', value=f'``{items[values][0]}``', inline=False)
        emb.add_field(name='Кол-во предмета', value=f'``{items[values][2]}``', inline=False)
        emb.add_field(name='Общая цена', value=f'``{int(items[values][0]) * items[values][2]}``', inline=False)
        
        emb.set_image(url=items[values][1])
        
        await inter.send(embed=emb, view=view, ephemeral=True)
        await view.wait()
        
        if view.value is False:
            async with aiosqlite.connect('projectbot.db') as db:
                del items[values]
                        
                await db.execute("UPDATE server{} SET inv = ? WHERE id = ?".format(inter.guild.id), [dumps(items), inter.author.id])
                await db.commit()
                    
                await inter.send(f'Предмет ``{values}`` успешно удалён!', ephemeral=True)
                logger.debug(f'Member {inter.author.name} delete item {values}. Server: {inter.guild.name}')
            
            
        
class SelectViewDropdown(disnake.ui.View):
    def __init__(self, data_cog: dict[str, int]) -> None:
        super().__init__(timeout=None)
        self.add_item(SelectMenu(data_cog))
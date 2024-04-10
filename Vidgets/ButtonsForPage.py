
import disnake
from disnake import ButtonStyle

# Класс с кнопками для переключеня страниц
class Button(disnake.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.pagination = 'Stop'
            
    @disnake.ui.button(emoji='▶️', style=ButtonStyle.blurple)
    async def button1(self, button: disnake.ui.Button, inter: disnake.CmdInter) -> None:
        await inter.response.defer(ephemeral=True)      
        self.pagination = 'Right'
        self.stop()
        
    
    
    @disnake.ui.button(emoji='◀️', style=ButtonStyle.blurple)
    async def button2(self, button: disnake.ui.Button, inter: disnake.CmdInter) -> None:
        await inter.response.defer(ephemeral=True)
        self.pagination = 'Left'
        self.stop()
        
        
    @disnake.ui.button(emoji='⛔', style=ButtonStyle.blurple)
    async def button3(self, button: disnake.ui.Button, inter: disnake.CmdInter) -> None:
        await inter.response.defer(ephemeral=True)
        self.stop()
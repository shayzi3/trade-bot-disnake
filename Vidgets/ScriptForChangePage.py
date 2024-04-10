
import disnake

from Vidgets import ButtonsForPage as bt

async def changer(inter: disnake.CmdInter, embeds: list[disnake.Embed]):
     view = bt.Button()
     await inter.send(embed=embeds[0], ephemeral=True, view=view)
     await view.wait()
        
     page = 0
     while True:
          if view.pagination == 'Right':
               if page == len(embeds) - 1:
                    page = 0
                        
               else:
                    page += 1
                      
               view = bt.Button()
               await inter.edit_original_response(embed=embeds[page], view=view)
               await view.wait()
                         
          if view.pagination == 'Left':
               if page == 0: 
                    page = len(embeds) - 1
                    
               else:
                    page -= 1
                       
               view = bt.Button()
               await inter.edit_original_response(embed=embeds[page], view=view)
               await view.wait()
                    
          if view.pagination == 'Stop':
               return await inter.delete_original_response()
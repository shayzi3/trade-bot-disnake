
import aiohttp

from typing import Union

from bs4 import BeautifulSoup
from numba import prange


async def convert_usd_in_rub(usd: int) -> int:
    usd = float(usd)
    
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json = await response.json()
               
    summ_ = json['rates']['RUB'] * usd
    return round(summ_, 1)

    
async def get_page(item: str) -> bool | list[Union[str, int]]:
    url = f'https://steamcommunity.com/market/search?appid=730&q={item.replace(" ", "+")}'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')   
                
           
    cheaker = {'error': 'There were no items matching your search. Try again with different keywords.'}
    list_with = []
    
    for i in prange(10):
        block = soup.find('div', id=f"result_{i}")
            
        if not block: 
            block = soup.find('div', class_ = 'market_listing_table_message')
            
            if not block:
                break
            
            else:
                if block.text == cheaker['error']:
                    return False
                
                else:
                    return await get_page(item)
            
        image = block.find('img').get('src')
        sale = block.find('span', class_="normal_price").text.split()[2][1:]
        name = block.find('span', id=f"result_{i}_name").text
        
        txt = [name, await convert_usd_in_rub(sale), image]
        list_with.append(txt)
       
    return list_with


async def get_item(items: dict[str], resulter: list[str | None]) -> bool | list[Union[str, int]]:
    keys: list[str] = []
    cheaker = {'error': 'There were no items matching your search. Try again with different keywords.'}
    
    for item in items:
        keys.append(item)
    
    for requests_ in prange(len(keys)):
        url = f'https://steamcommunity.com/market/search?appid=730&q={keys[requests_].replace(" ", "+")}'
            
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')   
            
        block = soup.find('div', id=f"result_{0}")
            
        if not block:
            block = soup.find('div', class_ = 'market_listing_table_message')
                
            if not block:
                break
                
            else:
                if block.text == cheaker['error']:
                    return False
                    
                else:
                    return await get_item(items, resulter)
                    
        else:     
            image = block.find('img').get('src')
            sale = block.find('span', class_="normal_price").text.split()[2][1:]
            name = block.find('span', id=f"result_{0}_name").text

            txt = [name, await convert_usd_in_rub(sale), image]
            resulter.append(txt)
            
            del items[keys[requests_]]
            
    return resulter

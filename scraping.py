import asyncio
from playwright.async_api import async_playwright, Playwright,Page
from bs4 import BeautifulSoup
import pandas as pd

async def parse_html(page:Page):
    html = await page.inner_html('#shop')
    soup = BeautifulSoup(html,'lxml')
    return soup

async def get_data(page:Page,link):
    await page.goto(link)
    soup = await parse_html(page)
    img = []
    ol = soup.find('ol',class_='flex-control-thumbs')
    allimg = ol.find_all('img')
    for i in range(0,len(allimg)):
        img.append(allimg[i]['src'])
    
    label = soup.find('label',class_='m-0')


    if label != None:
        select = soup.find('select')
        options = select.find_all('option')
        size = []
        for o in range(1,len(options)):
            size.append(options[o].text)
    else:
        size = 'no size'

    sold = soup.find('h4',class_='price')
    price = sold.find('ins')
    if price != None:
          status = 'Out of Stock'
    else:
        status = ' in ready'
      

    artikel = {
           'title': soup.find('h3','product_title').text,    
           'issues': soup.find('h3','product_title').findNext('span').text,  
           'price': soup.find('bdi').text,  
           'deskripsi': soup.find('p').text,
           'size': size,
           'img' : img,
           'status': status
           
        } 

    return artikel


async def product(page:Page):
    pages = 1
    data = []
    while True:
        url = f'https://www.maternaldisaster.com/shop/page/{pages}/'
        await page.goto(url)
        parse = await parse_html(page)
        post =  parse.find_all(class_='product')
    
        for g in post:
            link = g.find('a').get('href')
            produk = await get_data(page,link)
            data.append(produk)
            print('complete')
        
        pages+=1

        nextbutton = parse.find('a',class_='next')

        if nextbutton == None:
            break




    return data


async def run(playwright: Playwright):
    webkit = playwright.chromium
    browser = await webkit.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    data = await product(page)
    df = pd.DataFrame(data)
    df.to_csv("produk.csv")

    await browser.close()

   

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
    
asyncio.run(main())

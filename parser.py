import requests
import csv
from bs4 import BeautifulSoup
import re

import asyncio
from pyppeteer import launch

# 1) выяснить кол-во страниц
# 2) сформировать url
# 2) собрать данные

base_url = 'https://www.vseinstrumenti.ru/silovaya-tehnika/generatory-elektrostantsii/benzinovye/10-kvt/'
# base_url = 'https://www.vseinstrumenti.ru/silovaya-tehnika/generatory-elektrostantsii/'


def main():
    html = asyncio.get_event_loop().run_until_complete(get_html(base_url))
    pages = get_total_pages(html)
    page_urls = get_urls(pages)
    pages_in_html = []
    for page in page_urls:
        html = asyncio.get_event_loop().run_until_complete(get_html(page))
        pages_in_html.append(html)

    get_info(pages_in_html)




def get_urls(pages):
    page_urls = [base_url]
    if int(pages) == 1:
        return page_urls
    for n in range(2, int(pages) + 1):
        page_url = base_url + 'page' + str(n) + '/'
        page_urls.append(page_url)
    return page_urls


def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find('div', class_='paging')
    p = div.find_all('a')[-2]

    # ss = re.sub('<[^<]+?>', '', str(p))
    # ss = str(p).split('id="page')[-1].split('"')[0]     # Ппц, но что поделаешь...

    page_qty = p.get('id').strip('page')

    return page_qty


async def get_html(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    # await page.screenshot({'path': 'example.png'})
    html = await page.content()
    await browser.close()
    return html


def get_info(pages):
    data = []
    for page in pages:
        soup = BeautifulSoup(page, 'lxml')
        product = soup.find_all('div', class_='product')
        for p in product:
            try:
                # print(p.find('a', class_='link').get('title'))
                name = p.find('a', class_='link').get('title').strip()
            except AttributeError:
                name = 'X'
                continue

            try:
                price = p.find('div', class_='price-actual').find('span', class_='amount').text.strip()
            except AttributeError:
                price = 'N/A'   # Для отладки
                continue

            # print(name)
            # print(price)

            product_data = {'name': name, 'price': price}
            data.append(product_data)

    if write_csv(data):
        print('DONE')


def write_csv(data):
    with open('vse.csv', 'w') as f:
        writer = csv.writer(f, delimiter=';')
        for product in data:
            writer.writerow((product['name'], product['price']))


if __name__ == '__main__':
    main()

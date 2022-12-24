import re  # Импорт регулярных выражений
import ssl  # Импорт ###обертка для объектов сокетов
from datetime import datetime, timedelta  # Импорт времени

import certifi  # ???
import asyncio  # Импорт библиотеки которая делает код асинхронным
import aiohttp  # Импорт библиотеки которая делает запросы
from bs4 import BeautifulSoup  # С помощью этой библиотеки мы можем извлекать данные из
# файлов HTML и XML, проще говоря навигация по html

jokes_list = list()


async def get_page_info(session, page: int, start_page: int):  # Передача session c помощью которой мы
    # отслеживаем состояние кода
    global jokes_list

    if page == start_page:  # Если наша страница равна начальной страницы, то выводит главную страницу
        url = 'https://anekdotov.net'
    else:  # Если она не равна, то подставляется номер страницы
        url = f'https://anekdotov.net/arc/{page}.html'

    async with session.get(url=url) as response:  # передача session, с помощью которой отслеживаем ошибку
        try:
            response_text = await response.text()

            page_info = BeautifulSoup(response_text, 'html.parser')  # Создание переменной,
            # в которой создаём объект класса BeautifulSoup, передача html парсера

            jokes = page_info.find_all('div', class_='anekdot')  # Cоздание переменной,
            # в которой обращаемся к нашему объекту page_info и с помощью find_all забираем все теги и классы
            for joke in jokes:
                jokes_list.append(joke.text)
        except Exception as ex:
            print(repr(ex))


async def load_page_info():  # Создание асинхронной функции
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.72',
    }

    async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
        async with session.get(url='https://anekdotov.net') as response:
            try:
                response_text = await response.text()
                page_info = BeautifulSoup(response_text, 'html.parser')

                page = page_info.find_all('a', string='Д А Л Е Е!', href=True)
                print(page)
                for href in page:
                    count_of_pages = int(re.sub('[\\D]', '', href['href']))
                    print(count_of_pages)

            except Exception as ex:
                print(repr(ex))

        tasks = []
        past_date = datetime.now() - timedelta(days=15)
        current_date = int(past_date.strftime('%Y%m%d')[2:])

        for page in range(count_of_pages, current_date, -1):
            task = asyncio.create_task(get_page_info(session=session, page=page, start_page=count_of_pages))
            tasks.append(task)

        await asyncio.gather(*tasks)


async def run_tasks():
    global jokes_list
    await load_page_info()
    # print(jokes_list)
    # for joke in jokes_list:
    #     print(joke)
    #     print()
    # print(len(jokes_list))
    return jokes_list


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(run_tasks())


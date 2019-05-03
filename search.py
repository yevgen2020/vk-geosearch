#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
from datetime import datetime

import requests

token = ''
v = 5.92

E, R, G, Y, B = '\033[0m', '\033[31m', '\033[32m', '\033[33m', '\033[34m'
bp = '\n' + B + '-' * 75 + E
banner = B + '''
    ██╗   ██╗██╗  ██╗               ██████╗ ███████╗ ██████╗ ███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
    ██║   ██║██║ ██╔╝              ██╔════╝ ██╔════╝██╔═══██╗██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
    ██║   ██║█████╔╝     █████╗    ██║  ███╗█████╗  ██║   ██║███████╗█████╗  ███████║██████╔╝██║     ███████║
    ╚██╗ ██╔╝██╔═██╗     ╚════╝    ██║   ██║██╔══╝  ██║   ██║╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
     ╚████╔╝ ██║  ██╗              ╚██████╔╝███████╗╚██████╔╝███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
      ╚═══╝  ╚═╝  ╚═╝               ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
                                                                                                         
''' + E


def parse_vk(lat, long, start_time, end_time, radius, pr):
    result = []
    if pr == 'y':
        proxies = {'http': 'http://127.0.0.1:8888',
                   'https': 'http://127.0.0.1:8888'}
    else:
        proxies = None

    params = {
            'lat': lat,
            'long': long,
            'start_time': start_time,
            'end_time': end_time,
            'radius': radius,
            'sort': 0,
            'count': 1000,
            'access_token': token,
            'v': v
    }

    r = requests.get('https://api.vk.com/method/photos.search', params=params, proxies=proxies).json()

    count = r['response']['count']
    print(B + 'Всего: ' + E + str(count))
    for i in r['response']['items']:
        photo = ''
        for s in i['sizes']:
            if s['type'] == 'w':
                photo = i['sizes'][-4]['url']

        if not photo:
            photo = i['sizes'][-1]['url']

        date = i['date']
        if i['owner_id'] > 0:
            result.append([photo, date, i['owner_id']])
        else:
            continue

    return str(len(result)), result


if __name__ == '__main__':
    try:
        proxy_run = None
        print(banner)
        input_proxy = input('Использовать прокси? (y/n): ')
        if input_proxy == 'y':
            #os.environ['PYTHONHTTPSVERIFY'] = '0'
            proxy_run = subprocess.Popen('./proxy.py')

        print(bp + '\nКоординаты в формате ДОЛГОТА, ШИРОТА Пример: ' + Y + '55.753215, 37.622504' + bp)
        coordinates = input('Координаты: ')
        place = 'Координаты: ' + coordinates
        coordinates = coordinates.split(', ')
        print(bp + '\nФормат ДД/ММ/ГГГГ ЧЧ:ММ Пример: ' + Y + '01/03/2019 08:05' + bp)
        input_end_date = input('Конечные дата-время или [Enter] - текущие: ')
        if not input_end_date:
            end_date = int(time.time())
        else:
            end_date = int(time.mktime(datetime.strptime(input_end_date, '%d/%m/%Y %H:%M').timetuple()))
        input_start_date = input('Начальные дата-время: ')
        start_date = int(time.mktime(datetime.strptime(input_start_date, '%d/%m/%Y %H:%M').timetuple()))
        radius = input('Радиус поиска в метрах [10, 100, 800, 6000, 50000]: ')
        print(bp + B + '\nПарсинг...')
        items, res = parse_vk(*coordinates, start_date, end_date, radius, input_proxy)
        print(B + 'Отфильтрованых результатов: ' + E + items)
        place = place + '<br>Результатов: ' + items
        filename = str(time.time()).split('.')[0] + '.html'
        print(B + 'Файл: ' + E + os.getcwd() + '/' + filename + bp)
        file = open(filename, 'w')

        header = '<html>\n\t<head>\n\t\t<style type="text/css">' \
                 '\n\t\t\t.container {display: grid; grid-gap: 20px; grid-template-columns: 400px 400px 400px;' \
                 ' text-align: center;}' \
                 '\n\t\t\ta {text-decoration: none; color: black;}' \
                 '\n\t\t\timg {max-width: 400px; max-height: 300px; object-fit: cover;}' \
                 '\n\t\t</style>\n\t</head>\n\t<body>' \
                 '\n\t\t<h2 style="text-align: center">' + place + '</h2>\n\t\t<div class="container">'

        file.write(header)
        for i in res:
            txt = datetime.utcfromtimestamp(int(i[1])).strftime('%d-%m-%Y %H:%M')
            link = 'https://vk.com/id' + str(i[2])
            to_write = f'\n\t\t\t<a target="_blank" rel="noopener" href="{link}"><img src="{i[0]}" alt=""><br>{txt}</a>'
            file.write(to_write)

        file.write('\n\t\t</div>\n\t</body>\n</html>')
        file.close()
        if proxy_run:
            proxy_run.kill()

    except Exception as err:
        print(err)
        if proxy_run:
            proxy_run.kill()
        exit(1)

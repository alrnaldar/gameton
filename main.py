import requests

import json, os

from dotenv import load_dotenv


load_dotenv()
token = os.getenv("TOKEN")

# URL сервера

server_url = 'https://games-test.datsteam.dev/play/snake3d'


# API-метод

api = '/player/move'

url = f"{server_url}{api}"


# Данные для отправки

data = {

    'snakes': []

}

# Заголовки запроса

headers = {

    'X-Auth-Token': token,

    'Content-Type': 'application/json'

}


# Выполнение POST-запроса

response = requests.post(url, headers=headers, json=data)


# Сохранение ответа в файл

with open('example_response.json', 'w') as file:

    file.write(response.text)
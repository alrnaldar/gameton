import pygame
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

token = '62d0cb56-2c5e-4dde-82c5-7f55cb208f26'
server_url = 'https://games-test.datsteam.dev/play/snake3d'
api = '/player/move'
url = f"{server_url}{api}"
headers = {
    'X-Auth-Token': token,
    'Content-Type': 'application/json'
}

WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 0)
SNAKE_COLOR = (255, 255, 255)
FOOD_COLOR = (255, 0, 0)
SCALE = 5  # Масштабированиt


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('3D Snake Game')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

last_move_times = {}

def get_game_state():
    logger.debug(f'Отправка запроса на: {url} с заголовками: {headers}')
    response = requests.post(url, headers=headers, json={'snakes': []})
    # logger.debug(f'Получен ответ: {response.json()}')
    response.raise_for_status()
    return response.json()

def send_move_command(snake_id, direction):
    data = {
        "snakes": [
            {
                "id": snake_id,
                "direction": direction
            }
        ]
    }
    logger.debug(f'Отправка команды перемещения с данными: {data}')
    response = requests.post(url, headers=headers, json=data)
    # logger.debug(f'Получен ответ на команду перемещения: {response.json()}')
    response.raise_for_status()
    return response.json()

def find_closest_food(head_pos, food_items):
    min_distance = float('inf')
    closest_food = None
    for food in food_items:
        food_pos = food['c']
        distance = sum(abs(a - b) for a, b in zip(head_pos, food_pos))  # Манхэттенское расстояние
        if distance < min_distance:
            min_distance = distance
            closest_food = food_pos
    return closest_food

running = True
while running:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game_state = get_game_state()

        screen.fill(BACKGROUND_COLOR)

        food_items = game_state.get('food', [])
        if food_items:
            for food in food_items:
                food_pos = food['c']
                pygame.draw.circle(screen, FOOD_COLOR, (food_pos[0]*SCALE, food_pos[1]*SCALE), 5)

        all_snakes = game_state.get('snakes', [])
        for snake_index, snake_data in enumerate(all_snakes):
            snake_geometry = snake_data['geometry']
            snake_id = snake_data['id']
            snake_length = len(snake_geometry)
            snake_status = snake_data['status']
            if snake_geometry:
                for point in snake_geometry:
                    pygame.draw.rect(screen, SNAKE_COLOR, (point[0]*SCALE, point[1]*SCALE, 10, 10))

                head_pos = snake_geometry[0]
                closest_food = find_closest_food(head_pos, food_items) if food_items else None
                if closest_food and closest_food != head_pos:
                    direction = [0, 0, 0]

                    if head_pos[0] < closest_food[0]:
                        direction[0] = 1
                    elif head_pos[0] > closest_food[0]:
                        direction[0] = -1

                    elif head_pos[1] < closest_food[1]:
                        direction[1] = 1
                    elif head_pos[1] > closest_food[1]:
                        direction[1] = -1

                    elif head_pos[2] < closest_food[2]:
                        direction[2] = 1
                    elif head_pos[2] > closest_food[2]:
                        direction[2] = -1

                    send_move_command(snake_id, direction)

                    last_move_times[snake_id] = datetime.now().strftime("%H:%M:%S")

            last_move_time = last_move_times.get(snake_id, "неизвестно")
            snake_info_text = font.render(
                f'Snake ID: {snake_id[:6]} Len: {snake_length} Status: {snake_status}', True, (255, 255, 255))
            snake_coords_text = font.render(
                f'Coords: {head_pos} Closest Food: {closest_food} Last Move: {last_move_time}', True, (255, 255, 255))
            screen.blit(snake_info_text, (10, 70 + snake_index* 40))
            screen.blit(snake_coords_text, (10, 90 + snake_index*40))

        score = game_state.get('points', 0)
        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

        clock.tick(1)

    except requests.exceptions.RequestException as e:
        logger.error(f'HTTP запрос не удался: {e}')

pygame.quit()

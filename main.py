import pygame
import math

# inicializamos pygame

pygame.init()

# creamos variables para el juego

fps = 60

# creamos un timmer para el juego con pygame

timer = pygame.time.Clock()

# creamos una variable que tendra el tipo de font que usaremos en el juego
# puedes descargar la font que quieres , podemos buscar en dafont

font = pygame.font.Font('assets/fonts/Lemony.ttf', 32)

# definir constantes para el tamaño de la pantalla

WIDTH = 900
HEIGHT = 800

# usamos el tamaño de pantalla con pygame

screen = pygame.display.set_mode([WIDTH, HEIGHT])

# creamos unas listas vacias para los backgrounds y banners

backgrounds = []
banners = []
# lista de Targets
target_images = [[], [], []]

# diccionario para saber cuantos targets habran en cada nivel

targets = {
    1: [10, 5, 3],
    2: [13, 8, 6],
    3: [15, 12, 8, 3]
}

# variable para nivel

level = 1
points = 0
shot = False
total_shots = 0
mode = 0
ammo = 0
time_passed = 0
time_remmaining = 0
counter = 1
menu = True
game_over = False
pause = False
menu_img = (pygame.image.load(f'assets/menus/mainMenu.png'))
game_over_img = (pygame.image.load(f'assets/menus/gameOver.png'))
pause_image = (pygame.image.load(f'assets/menus/pause.png'))
best_freeplay = 0
best_time = 0
best_ammo = 0
clicked = False
write_values = False

# el juego es un arcade , en mi caso sera un taller que arreglara vehiculos
# usaremos una llave como utensilio
# tendremos una llave para cada nivel

wrenchs = []

# usare un bucle for para recorrer los backgrounds etc
# 1, 4 empezara en uno y temrinara en 3 los ciclos for de python incluyen el inicio , pero no el final

for i in range(1, 4):
    # agregamos los backgrounds a la lista cargando la imagen con pygame
    backgrounds.append(pygame.image.load(f'assets/background/{i}.jpg'))
    banners.append(pygame.image.load(f'assets/banners/{i}.png'))
    wrenchs.append(pygame.transform.scale(pygame.image.load(f'assets/wrenchs/{i}.png'), (150, 150)))
    if i < 3:
        for j in range(1, 4):
            target_images[i - 1].append(
                pygame.transform.scale(pygame.image.load(f'assets/targets/{i}/{j}.png'),
                                       (120 - (j * 18), 80 - (j * 12))))
    else:
        for j in range(1, 5):
            target_images[i - 1].append(
                pygame.transform.scale(pygame.image.load(f'assets/targets/{i}/{j}.png'),
                                       (120 - (j * 18), 80 - (j * 12))))


def draw_score():
    global mode_text
    point_text = font.render(f'Points: {points}', True, 'black')
    screen.blit(point_text, (320, 660))
    shot_text = font.render(f'Total Shots: {total_shots}', True, 'black')
    screen.blit(shot_text, (320, 687))
    time_text = font.render(f'Time Elapsed: {time_passed}', True, 'black')
    screen.blit(time_text, (320, 714))
    if mode == 0:
        mode_text = font.render(f'Freeplay Mode', True, 'black')
    if mode == 1:
        mode_text = font.render(f'Ammo Remaining : {ammo}', True, 'black')
    if mode == 2:
        mode_text = font.render(f'Time Remaining: {time_remmaining}', True, 'black')
    screen.blit(mode_text, (320, 741))



def draw_wrench():
    mouse_pos = pygame.mouse.get_pos()
    wrench_point = (WIDTH / 2, HEIGHT - 200)
    lasers = ['red', 'purple', 'green']
    clicks = pygame.mouse.get_pressed()
    if mouse_pos[0] != wrench_point[0]:
        slope = (mouse_pos[1] - wrench_point[1]) / (mouse_pos[0] - wrench_point[0])
    else:
        slope = -100000
    angle = math.atan(slope)
    rotation = math.degrees(angle)
    if mouse_pos[0] < WIDTH / 2:
        wrench = pygame.transform.flip(wrenchs[level - 1], True, False)
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(wrench, 90 - rotation), (WIDTH / 2 - 90, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
    else:
        wrench = wrenchs[level - 1]
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(wrench, 270 - rotation), (WIDTH / 2 - 30, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)


# esta funcion dibuja las enemigos en los diferentes niveles
def draw_level(coords):
    if level == 1 or level == 2:
        target_rects = [[], [], []]
    else:
        target_rects = [[], [], [], []]

    for i in range(len(coords)):
        for j in range(len(coords[i])):
            target_rects[i].append(
                pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]), (60 - i * 12, 60 - i * 12)))
            screen.blit(target_images[level - 1][i], coords[i][j])
    return target_rects


# moviemiento a los niveles

def move_level(coords):
    if level == 1 or level == 2:
        max_value = 3
    else:
        max_value = 4
    for i in range(max_value):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            if my_coords[0] < -150:
                coords[i][j] = (WIDTH, my_coords[1])
            else:
                coords[i][j] = (my_coords[0] - 2 ** i, my_coords[1])
    return coords


def check_shot(targets, coords):
    global points
    mouse_pos = pygame.mouse.get_pos()
    for i in range(len(targets)):
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                coords[i].pop(j)
                points += 10 + 10 * (i ** 2)
    return coords


def draw_menu():
    global game_over, pause, mode, level, menu, time_passed, total_shots, points, ammo, time_remmaining
    global best_ammo, best_time, best_freeplay, best_time, write_values
    game_over = False
    pause = False
    screen.blit(menu_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    freeplay_button = pygame.rect.Rect((170, 524), (260, 100))
    screen.blit(font.render(f'{best_freeplay}', True, 'black'), (340, 580))
    ammo_button = pygame.rect.Rect((475, 524), (260, 100))
    screen.blit(font.render(f'{best_ammo}', True, 'black'), (650, 580))
    timed_button = pygame.rect.Rect((170, 661), (260, 100))
    screen.blit(font.render(f'{best_time}', True, 'black'), (350, 710))
    reset_button = pygame.rect.Rect((475, 661), (260, 100))

    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0
        level = 1
        menu = False
        time_passed = 0
        total_shots = 0
        points = 0

    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1
        menu = False
        time_passed = 0
        ammo = 81
        total_shots = 0
        points = 0

    if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2
        level = 1
        menu = False
        time_remmaining = 30
        time_passed = 0
        total_shots = 0
        points = 0
    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        best_freeplay = 0
        best_time = 0
        best_ammo = 0
        write_values = True






def draw_game_over():
    pass

def draw_pause():
    pass


# posiciones iniciales coordenades

one_coords = [[], [], []]
two_coords = [[], [], []]
three_coords = [[], [], [], []]

for i in range(3):
    my_list = targets[1]
    for j in range(my_list[i]):
        one_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))

for i in range(3):
    my_list = targets[2]
    for j in range(my_list[i]):
        two_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))

for i in range(4):
    my_list = targets[3]
    for j in range(my_list[i]):
        three_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 100) + 30 * (j % 2)))

# realizando pruebas

run = True

while run:
    timer.tick(fps)
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            time_passed += 1
            if mode == 2:
                time_remmaining -= 1

    # llenado la pantalla

    screen.fill('black')
    screen.blit(backgrounds[level - 1], (0, 0))
    # cargamos los banners
    screen.blit(banners[level - 1], (0, HEIGHT - 200))
    # cargando mas graficas
    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        draw_game_over()
    if pause:
        level = 0
        draw_pause()





    if level == 1:
        target_boxes = draw_level(one_coords)
        one_coords = move_level(one_coords)
        if shot:
            one_coords = check_shot(target_boxes, one_coords)
            shot = False
    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_level(two_coords)
        if shot:
            two_coords = check_shot(target_boxes, two_coords)
            shot = False

    elif level == 3:
        target_boxes = draw_level(three_coords)
        three_coords = move_level(three_coords)
        if shot:
            three_coords = check_shot(target_boxes, three_coords)
            shot = False

    # dibujando la llave con una funcion
    if level > 0:
        draw_wrench()
        draw_score()
    # evitando un loop infinito por medio de un evento de pygame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT - 200):
                shot = True
                total_shots += 1
                if mode == 1:
                    ammo -= 1

    if level > 0:
        if target_boxes == [[], [], []] and level < 3:
            level += 1

    pygame.display.flip()  # este comando dice que llevemos all a la pantalla y lo mostremos
pygame.quit()

import pygame
import Objects
import ScreenEngine
import Logic
import Service
from GameSettings import *


class MyHeroFactory(Objects.AbstractHeroFactory):
    # Фабрика по созданию героев
    def create(self):
        sprite = Service.ObjectsLib.textures["hero"]["sprite"]
        return Objects.Hero(BASE_STATS, sprite)


def repaint(game_display, pygame_obj, drawer_obj):
    # Обновляем изображение на экране
    game_display.blit(drawer_obj, (0, 0))
    drawer_obj.draw(gameDisplay)
    pygame_obj.display.update()


def quit_game(pygame_obj):
    # Выходим из игры
    pygame_obj.display.quit()
    pygame_obj.quit()
    exit(0)


def create_game(sprite_size, pygame_obj):
    # Описываем структуру каталогов с текстурами
    dict_dirs = {"objects": OBJECT_TEXTURE, "ally": ALLY_TEXTURE,
                 "enemies": ENEMY_TEXTURE, "textures": OTHER_TEXTURE}

    # Хранилище описаний объектов
    Service.ObjectsLib.set_generators(Service.GraphicalLib(pygame_obj, sprite_size, dict_dirs),
                                      Service.ActionLib())
    # Загрузка текстур
    Service.ObjectsLib.load(MAP_TEXTURES)
    with open("objects.yml", "r") as file:
        Service.ObjectsLib.append(file.read())

    # Генератор уровней: карты, объекты, мобы
    Service.LevelGenerator.set_libs(Service.ObjectsLib)
    # Конфигурационный файл уровней
    Service.LevelGenerator.load("levels.yml")
    # Финальный уровень
    Service.LevelGenerator.levels.append({'map': Service.EndMapSurface("EndMap"),
                                          'obj': Service.EmptyMapSpawn("EndMap")})

    # Основная геймплейная логика
    engine_obj = Logic.GameEngine()
    engine_obj.sprite_size = sprite_size

    # Генератор героя
    engine_obj.hero_generator = MyHeroFactory()
    # Генератор уровней
    engine_obj.level_generator = Service.LevelGenerator
    # Подписываемся на события
    engine_obj.subscribe(Service.ObjectsLib)
    # Загружаем начальный уровень
    engine_obj.start()

    return engine_obj


if not KEYBOARD_CONTROL:
    print("Only keyboard control")
    exit(0)

pygame.init()
gameDisplay = pygame.display.set_mode(SCREEN_DIM)
pygame.display.set_caption("MyRPG")
# Добавляем возможность обрабатывать длительные нажатия клавиши
pygame.key.set_repeat(15, 200)

engine = create_game(BASE_SPRITE_SIZE, pygame)

drawer = ScreenEngine.Screen_Handle((0, 0))
drawer = ScreenEngine.HelpWindow((700, 500), pygame.SRCALPHA, (0, 0), drawer)
drawer = ScreenEngine.MiniMap((164, 164), pygame.SRCALPHA, (50, 50), drawer)
drawer = ScreenEngine.InfoWindow((160, 600), (490, 14), drawer)
drawer = ScreenEngine.ProgressBar((640, 120), (640, 0), drawer)
drawer = ScreenEngine.GameSurface((640, 480), pygame.SRCALPHA, (0, 480), drawer)

drawer.connect_engine(engine)

# Основной рабочий цикл
while engine.working:
    for event in pygame.event.get():
        # Обрабатываем нажатие клавиш
        if event.type == pygame.QUIT:
            engine.working = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                # Окно с горячими клавишами
                engine.show_help = not engine.show_help
                repaint(gameDisplay, pygame, drawer)
                break
            if event.key == pygame.K_m:
                # Окно миникарты
                engine.show_minimap = not engine.show_minimap
                repaint(gameDisplay, pygame, drawer)
                break
            if event.key == pygame.K_F12:
                # Маленький "не документированный" чит
                engine.level_next()
            if event.key == pygame.K_KP_PLUS or event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                # Приближаем карту
                engine.zoom_in()
            if event.key == pygame.K_KP_MINUS or event.key == pygame.K_MINUS:
                # Отдаляем карту
                engine.zoom_out()
            if event.key == pygame.K_r:
                # Перезапуск игры
                engine.sprite_size = BASE_SPRITE_SIZE
                engine.start()
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Сброс уровня
                engine.level_reset()
            if event.key == pygame.K_ESCAPE:
                # Выходим из игры
                engine.working = False
            if engine.game_process:
                if event.key == pygame.K_UP:
                    # Движение вверх
                    engine.move_up()
                elif event.key == pygame.K_DOWN:
                    # Движение вниз
                    engine.move_down()
                elif event.key == pygame.K_LEFT:
                    # Движение влево
                    engine.move_left()
                elif event.key == pygame.K_RIGHT:
                    # Движение вправо
                    engine.move_right()

        repaint(gameDisplay, pygame, drawer)

quit_game(pygame)

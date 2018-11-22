from random import randint
from GameSettings import *
from MazeAlgorithms import MazeGenerator


class Tali:
    # Тайл карты
    def __init__(self, passable, sprite=None, state=0):
        # Состояние ячейки, в зависимости от него отображается спрайт
        self.state = state
        # Проходимость
        self._passable = bool(passable)
        # Список спрайтов
        self._sprite = sprite if isinstance(sprite, list) else [list]

    @property
    def passable(self):
        return self._passable

    @property
    def sprite(self):
        return self._sprite[self.state]

    @sprite.setter
    def sprite(self, value):
        self._sprite = value if isinstance(value, list) else [value]


class GameMap:
    # Класс описывающий карту
    def __init__(self, _map):
        self.config = []
        self._map = _map

    def __len__(self):
        return int(len(self._map[0]) * len(self._map))

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            raise TypeError
        elif 0 <= key[0] < len(self._map[0]) and \
                0 <= key[1] < len(self._map) and \
                len(key) == 2:
            return self._map[key[1]][key[0]]
        else:
            raise IndexError

    @property
    def size(self):
        return len(self._map[0]), len(self._map)


class GeneratorHelper:
    # Генератор случайных позиций на карте, с учетом проходимости тайла
    @staticmethod
    def random_coord(_map, coord_list):
        size = _map.size
        size = (size[0] - 1, size[1] - 1)
        while True:
            coord = randint(1, size[0]), randint(1, size[1])
            if coord not in coord_list and _map[coord].passable:
                return coord


class MapSurface:
    # Базовый класс поверхность карты
    def __init__(self, type_map):
        # Переменная не используется, оставлена на будущее
        self.type_map = type_map

    def get(self, maps_obj):
        return []


class EmptyMapSurface(MapSurface):
    # Пустая поверхность
    def get(self, maps_obj):
        wall = maps_obj[WALL]
        floor = maps_obj[FLOOR]

        _map = [[floor[randint(0, len(floor) - 1)] for _ in range(41)] for _ in range(41)]
        for i in range(41):
            _map[0][i] = wall
            _map[40][i] = wall
            _map[i][0] = wall
            _map[i][40] = wall

        return _map


class EndMapSurface(MapSurface):
    # Финал игры
    def get(self, maps_obj):
        wall = maps_obj[WALL]
        floor = maps_obj[FLOOR]

        _map = [list('000000000000000000000000000000000000000'),
                list('0                                     0'),
                list('0                                     0'),
                list('0  0   0   000   0   0  00000  0   0  0'),
                list('0  0  0   0   0  0   0  0      0   0  0'),
                list('0  000    0   0  00000  0000   0   0  0'),
                list('0  0  0   0   0  0   0  0      0   0  0'),
                list('0  0   0   000   0   0  00000  00000  0'),
                list('0                                   0 0'),
                list('0                                     0'),
                list('000000000000000000000000000000000000000')
                ]
        for i in range(len(_map)):
            for j in range(len(_map[0])):
                _map[i][j] = wall if _map[i][j] == '0' else floor[randint(0, len(floor) - 1)]

        return _map


class RandomMapSurface(EmptyMapSurface):
    # Случайногенерируемая карта карта
    def get(self, maps_obj):
        _map = super().get(maps_obj)
        wall = maps_obj[WALL]
        i = 350
        while i > 0:
            coord = randint(1, 40), randint(1, 40)
            if _map[coord[1]][coord[0]] != wall:
                _map[coord[1]][coord[0]] = wall
                i -= 1

        return _map


class EllersMapGenerator(EmptyMapSurface):
    # Генерация карты на основе алгоритма Эллера
    def get(self, maps_obj):
        _map = super().get(maps_obj)
        map_creator = MazeGenerator.get("Eller")
        wall = maps_obj[WALL]
        size = 3
        rows = 40 // size
        num_y = -1
        for r_walls, b_walls in map_creator(rows):
            num_y += 1
            for num_x in range(rows):
                x = (1 + num_x) * size
                y = (1 + num_y) * size
                for shift in range(size):
                    # Нижняя граница
                    _map[y][x - shift] = wall if b_walls[num_x] else _map[y][x - shift]
                    # Правая граница
                    _map[y - shift][x] = wall if r_walls[num_x] else _map[y - shift][x]
                y -= size
                x -= size
                if _map[y + 1][x] == wall and _map[y][x + 1] == wall:
                    _map[y][x] = wall
        return _map


class ObjSpawn:
    # Базовый класс генератора объектов на карте
    def __init__(self, type_map):
        self.type_map = type_map
        self.enemy_list = dict()

    def get(self, _map):
        return {}


class EmptyMapSpawn(ObjSpawn):
    def get(self, _map):
        # Размещаем героя
        return {(1, 1): "hero"}


class RandomSpawn(ObjSpawn):
    def get(self, _map):
        def spiral():
            step = 1
            while step < 10:
                for y_shift in map(lambda x: (step, 1 + x), range(step)):
                    yield y_shift
                for x_shift in map(lambda x: (x, step), range(step - 1, 0, -1)):
                    yield x_shift
                step += 1

        # При случайной геренрайции лабиринта, позиция героя может отличаться от (1, 1)
        coord = (1, 1)
        for i in filter(lambda x: _map[x].passable, spiral()):
            # Поиск свободной позиции по спирали от точки (1, 1)
            coord = i
            break
        result = {coord: "hero"}

        # Размещаем врагов
        for name, count in self.enemy_list.items():
            for _ in range(count):
                # Доступные координаты
                coord = GeneratorHelper.random_coord(_map, result)
                # Сохраняем позицию
                result[coord] = name

        return result



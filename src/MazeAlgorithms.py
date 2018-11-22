import random


class MazeGenerator:
    """
    Класс " генераторов лабиринтов подземелий
    """
    @classmethod
    def get(cls, name):
        if name == "Eller":
            return cls.Eller

    class Eller:
        @classmethod
        def rnd(cls):
            """
            Отдельная функция генерации псевдослучайных чисел
            Алгоритм реализован так, что увеличивая частоту появления одно из значений, мы изменяем
            направленность лабиринта.
                True - вертикальная направленности поземелья (превалируют корридоры вниз)
                False - горизонтальная направленности поземелья (превалируют корридоры вправо)
            """
            return random.randint(0, 2) == 1

        def __init__(self, size):
            self.line_num = 0
            self.size = size
            self.groups = {str(i) for i in range(size)}
            self.line = list(self.groups)
            self.right_walls = []
            self.bottom_walls = []

        def join_set(self, absorb_set, greed_set):
            for i in filter(lambda x: self.line[x] == absorb_set, range(self.size)):
                self.line[i] = greed_set

        def get_lines(self):
            return [False for _ in range(self.size)]

        def right_wall(self):
            walls = self.get_lines()

            for i, j in map(lambda x: (x - 1, x), range(1, self.size)):
                if self.line[i] == self.line[j] or self.rnd():
                    # Вертикальная стена: между элементами 1 множества или разделитель 2х множеств
                    walls[i] = True
                else:
                    # Объединение 2х множеств
                    self.join_set(self.line[j], self.line[i])
            return walls

        def bottom_wall(self):
            groups = self.line.copy()
            walls = self.get_lines()

            for i in filter(lambda x: not self.rnd() and groups.count(groups[x]) > 1, range(self.size)):
                # Создание нижней границы + обнуление элемента из начального списка
                walls[i] = True
                groups[i] = " "

            return walls

        def next_line(self):
            groups = self.groups - set(self.line)
            self.line_num += 1
            return [groups.pop() if self.bottom_walls[i] else self.line[i] for i in range(self.size)]

        def __iter__(self):
            return self

        def __next__(self):
            if self.line_num == self.size:
                raise StopIteration('Last line of Maze')
            elif self.line_num == self.size - 1:
                # Последняя линия
                self.right_walls = self.get_lines()
                for i in range(1, self.size):
                    if self.line[i - 1] == self.line[i]:
                        self.right_walls[i - 1] = True
                    else:
                        self.join_set(self.line[i], self.line[i - 1])
                self.bottom_walls = self.get_lines()
                self.line_num += 1
            else:
                self.right_walls = self.right_wall()
                self.bottom_walls = self.bottom_wall()
                self.line = self.next_line()
            return self.right_walls, self.bottom_walls

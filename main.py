from random import randint


# Исключения
class GameException(Exception):
    pass


class MissException(GameException):
    def __str__(self):
        return "Выстрел за пределами карты!"


class RepeatException(GameException):
    def __str__(self):
        return "Вы уже сюда стреляли!"


class PlaceShipsException(GameException):
    pass


class Ship:  # Класс кораблей
    def __init__(self, start, length, direction):
        self.length = length
        self.start = start
        self.durability = length
        self.direction = direction

    def shot(self, target):
        return target in self.coordinates

    @property
    def coordinates(self):
        ship_coordinates = []
        for i in range(self.length):
            x_now = self.start.x
            y_now = self.start.y

            if self.direction == 0:
                x_now += i
            elif self.direction == 1:
                y_now += i
            ship_coordinates.append(Cell(x_now, y_now))
        return ship_coordinates


class GameBoard:  # Класс игрового поля
    def __init__(self, fog_of_war=False, size=6):
        self.size = size
        self.fog = fog_of_war
        self.board = [["o"] * size for _ in range(size)]
        self.ships = []
        self.busy = []
        self.count = 0

    def __str__(self):
        row_str = " \nX | 0 | 1 | 2 | 3 | 4 | 5 |\n"
        for i, row in enumerate(self.board):
            row_str += f"{i} | " + " | ".join(row) + " |\n"
        if self.fog:  # Прячем корабли на поле противника
            row_str = row_str.replace("■", "o")
        return row_str

    def check_coords(self, z):  # Проверка координат
        return (-1 < z.x < self.size) and (-1 < z.y < self.size)

    def add_ships(self, ship):  # Добавляем корабли на поле
        for i in ship.coordinates:
            if i in self.busy or not self.check_coords(i):
                raise PlaceShipsException(Exception)
        for i in ship.coordinates:
            self.board[i.x][i.y] = "■"
            self.busy.append(i)

        self.ships.append(ship)  # добавляем в список кораблей
        self.around_busy(ship)  # добавляем в список занятых координат

    def around_busy(self, ship, game=False):  # Занятая территория
        around = [(0, 0), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        for i in ship.coordinates:
            for i_x, i_y in around:
                place = Cell(i.x + i_x, i.y + i_y)
                if place not in self.busy and (self.check_coords(place)):
                    if game:
                        self.board[place.x][place.y] = '.'
                    self.busy.append(place)

    def shot(self, z):
        if not self.check_coords(z):
            raise MissException()

        if z in self.busy:
            raise RepeatException()

        self.busy.append(z)

        for ship in self.ships:
            if z in ship.coordinates:
                ship.durability -= 1
                self.board[z.x][z.y] = 'X'
                if ship.durability == 0:
                    self.count += 1
                    self.around_busy(ship, game=True)
                    print("Потопил!")
                    return False
                else:
                    print("Попал!")
                    return True
        self.board[z.x][z.y] = "T"
        print("Промах!")
        return False

    def begin(self):
        self.busy = []


class Cell:  # Выстрел
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Player:
    def __init__(self, board, board_ai):
        self.board = board
        self.board_ai = board_ai

    def request(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.request()
                repeat = self.board_ai.shot(target)
                return repeat
            except GameException as i:
                print(i)


class AI(Player):
    def request(self):
        s = Cell(randint(0, 5), randint(0, 5))
        print(f"Противник бьет по: {s.x + 1} {s.y + 1}")
        return s


class User(Player):
    def request(self):
        while True:
            target = input("Введите координаты 'x y' : ").split()
            if len(target) != 2:
                print("Введите 2 цифры от 0 до 5!")
                continue
            x, y = target
            if not (x.isdigit()) or not (y.isdigit()):
                print("Ошибка ввода! ")
                continue
            x, y = int(x), int(y)
            return Cell(x, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        one = self.random_board()
        two = self.random_board()
        two.fog = True

        self.map_ai = two
        self.map_user = one

        self.user = User(one, two)
        self.ai = AI(two, one)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_ships()
        return board

    def random_ships(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = GameBoard()
        count = 0
        for i in lens:
            while True:
                count += 1
                if count > 2000:
                    return None
                ship = Ship(Cell(randint(0, 5), randint(0, 5)), i, randint(0, 1))
                try:
                    board.add_ships(ship)
                    break
                except PlaceShipsException:
                    pass
        board.begin()
        return board

    def print_map(self):  # Вывод игрового поля

        map_user_list = list(self.map_user.__str__().split("\n"))
        map_ai_list = list(self.map_ai.__str__().split("\n"))

        done = [" Ваша поле: \t\t\t\t\t Поле соперника:"]
        i = 0

        while i < len(map_user_list):
            done.append(map_user_list[i])
            done.append('\t')
            done.append(map_ai_list[i])
            done.append('\n')
            i += 1

        print(' '.join(done))
        return

    def output(self):
        num = 0
        while True:
            print()
            g.print_map()
            print('Игра началась!')
            if num % 2 == 0:
                print("Ваш ход!")
                repeat = self.user.move()
            else:
                print("Ход противника!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print("Победа!")
                break
            if self.user.board.count == 7:
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.output()


g = Game()
g.start()

from random import randint


class GameException(Exception):
    pass


class MissException(GameException):
    def __str__(self):
        return "Выстрел вне координат."


class RepeatException(GameException):
    def __str__(self):
        return "Вы уже сюда стреляли!"


class ShipsException(GameException):
    def __str__(self):
        return "T_T"


class PlayingField:
    def __init__(self, fog_of_war=False, size=6):
        self.size = size
        self.list = list
        self.fog = fog_of_war
        self.field = [["o"] * size for i in range(size)]
        self.ships = []
        self.busy = []
        self.count = 0

    def show(self):
        print()
        print("    | 0 | 1 | 2 | 3 | 4 | 5 | ")
        for i, row in enumerate(self.field):
            row_str = f"  {i} | {' | '.join(row)} | "
            if self.fog:
                row_str = row_str.replace("■", "o")
            print(row_str)
        print()

    def check_coords(self, z):
        return (0 <= z.x < self.size) and (0 <= z.y < self.size)

    def add_ships(self, ship):
        for i in ship.coordinates:
            if i in self.busy or not self.check_coords(i):
                raise ShipsException(Exception)
        for i in ship.coordinates:
            self.field[i.x][i.y] = "■"
            self.busy.append(i)

        self.ships.append(ship)
        self.around_busy(ship)

    def around_busy(self, ship):
        around = [(0, 0), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        for i in ship.coordinates:
            for ix, iy in around:
                place = Cell(i.x + ix, i.y + iy)
                if place not in self.busy and (self.check_coords(place)):
                    self.busy.append(place)

    def shot(self, z):
        if not self.check_coords(z):
            raise MissException()

        if z in self.busy:
            raise RepeatException()

        self.busy.append(z)

        for ship in self.ships:
            if ship.shot(z) :
                ship.durability -= 1
                self.field[z.x][z.y] = 'X'
                if ship.durability == 0:
                    self.count += 1
                    print("Потопил!")
                    return False
                else:
                    print("Попал!")
                    return True
        self.field[z.x][z.y] = "T"
        print("Промах!")
        return False

    # def begin(self):
    #     self.busy = []


class Ship:
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


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Fighter:
    def __init__(self, field, field_ai):
        self.field = field
        self.field_ai = field_ai

    def request(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.request()
                repeat = self.field_ai.shot(target)
                return repeat
            except GameException as i:
                print(i)


class AI(Fighter):
    def request(self):
        s = Cell(randint(0, 5), randint(0, 5))
        print(f"Противник бъет по: {s.x + 1} {s.y + 1}")
        return s


class Player(Fighter):
    def request(self):
        while True:
            print("В атаку!")
            x = int(input("Введите номер строки: "))
            if 0 > x > 5:
                print("Введите 1 цифру от 0 до 5!")
                continue
            y = int(input("Введите номер столбца: "))
            if 0 > y > 5:
                print("Введите 1 цифру от 0 до 5!")

            return Cell(x, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_field()
        ai = self.random_field()
        ai.fog = True

        self.ai = AI(ai, player)
        self.player = Player(player, ai)

    def random_field(self):
        field = None
        while field is None:
            field = self.random_ships()
        return field

    def random_ships(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        field = PlayingField()
        count = 0
        for i in lens:
            while True:
                count += 1
                if count > 2000:
                    return None
                ship = Ship(Cell(randint(0, 5), randint(0, 5)), i, randint(0, 1))

                try:
                    field.add_ships(ship)
                    break
                except ShipsException:
                    pass
        # field.begin()
        return field


    def output(self):
        num = 0
        while True:
            print()
            print("Ваше поле:")
            print(self.player.field)
            print()
            print("Поле противника:")
            print(self.ai.field)
            print()
            if num % 2 == 0:
                print("Ваш ход!")
                repeat = self.player.move()
            else:
                print("Ход противника!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.field.count == 7:
                print("Победа!")
                break

            if self.player.field.count == 7:
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.output()


g = Game()
g.start()
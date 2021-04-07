import os
import time
from random import randint

ERROR = '[\033[31mERROR\033[0m]'


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return f"{ERROR} Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return f"{ERROR} Вы уже стреляли в эту клетку!"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "\033[31m.\033[34m"
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "***********\033[34m""   | A | B | C | D | E | F |""\033[0m***********"
        for i, row in enumerate(self.field):
            res += f"\n*********** \033[34m{i + 1} | " + " | ".join(row) + " |\033[0m***********"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "\033[33mX\033[34m"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    clear_screen()
                    print("Корабль уничтожен!")
                    return True
                else:
                    clear_screen()
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "\033[31m.\033[34m"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    letters = ["A", "B", "C", "D", "E", "F"]
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        blacklist = self.enemy.busy
        d = Dot(randint(0, 5), randint(0, 5))
        while d in blacklist:
            d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {Player.letters[d.y]} {d.x + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(ERROR + " Введите 2 координаты! ")
                continue

            y, x = cords

            if not (isinstance(y, str)) or (y.upper()) not in Player.letters:
                print(ERROR + " Введите корректную строку! ")
                continue
            if not (x.isdigit()):
                print(ERROR + " Введите число! ")
                continue
            y = int(Player.letters.index(y.upper())) + 1
            x = int(x)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        clear_screen()
        print('{:*^50}'.format(""))
        print('{:*^50}'.format("-------------------"))
        print('{:*^50}'.format("  Приветсвуем вас  "))
        print('{:*^50}'.format("      в игре       "))
        print('{:*^50}'.format("    морской бой    "))
        print('{:*^50}'.format("-------------------"))
        print('{:*^50}'.format(" формат ввода: x y "))
        print('{:*^50}'.format(" x - номер столбца  "))
        print('{:*^50}'.format(" y - номер строки "))
        print('{:*^50}'.format(""))
        time.sleep(3)
        clear_screen()

    def print_boards(self):
        print("*" * 50)
        print('{:*^50}'.format("Доска пользователя:"))
        print(self.us.board)
        print("*" * 50)
        print('{:*^50}'.format("Доска компьютера:"))
        print(self.ai.board)
        print("*" * 50)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("*" * 50)
                print('{:*^50}'.format("Ходит пользователь!"))
                repeat = self.us.move()
            else:
                clear_screen()
                print("*" * 50)
                print('{:*^50}'.format("Ходит компьютер!"))
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                self.print_boards()
                print('{:*^50}'.format("Пользователь выиграл!"))
                break

            if self.us.board.count == 7:
                self.print_boards()
                print('{:*^50}'.format("Компьютер выиграл!"))
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
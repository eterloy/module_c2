from random import randint
from time import sleep


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Введенные координаты находятся вне поля игры"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту точку"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"Dot({self.x},{self.y})"

class Ship:
    def __init__(self, stem, deck, direction):
        self.stem = stem
        self.deck = deck
        self.direction = direction
        self.hp = deck

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.deck):
            cur_x = self.stem.x
            cur_y = self.stem.y

            if self.direction == 0:
                cur_x += i

            elif self.direction == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def hit(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["~"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += " | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1}| " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("█", "~")
        return res

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "█"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb = False):
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

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
                ship.hp -= 1
                self.field[d.x][d.y] = "X"
                if ship.hp == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Вы уничтожили корабль противника!")
                    sleep(2)
                    return False
                else:
                    print("Вы повредили корабль противника!")
                    sleep(2)
                    return True

        self.field[d.x][d.y] = "."
        print("Промах!")
        sleep(1)
        return False

    def begin(self):
        self.busy = []

class Player:
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
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты")
                continue

            x, y = cords

            if not (x.isdigit() and y.isdigit()):
                print("Введите числа")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

class Game:
    def __init__(self, size=6):
        self.size = size
        user_board = self.random_board()
        ai_board = self.random_board()
        ai_board.hid = True

        self.user = User(user_board, ai_board)
        self.ai = AI(ai_board, user_board)

    def create_board(self):
        ship_types = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for i in ship_types:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.create_board()
        return board

    def greet(self):
        print("___________________")
        print(" Приветствуем Вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("___________________")
        print(" формат ввода: х у ")
        print(" х - номер строки  ")
        print(" у - номер столбца ")

    def loop(self):
        step = 0
        while True:
            print("____________________")
            print("Доска пользователя: ")
            print(self.user.board)
            print("____________________")
            print("Доска компьютера: ")
            print(self.ai.board)
            print("____________________")
            if step % 2 == 0:
                print("Ход пользователя!")
                repeat = self.user.move()
            else:
                print("Ход компьютера!")
                repeat = self.ai.move()
            if repeat:
                step -= 1

            if self.ai.board.count == 7:
                print("____________________")
                print("Вы выиграли!!!")
                break

            if self.user.board.count == 7:
                print("____________________")
                print("   Вы проиграли :(  ")
                print(" компьютер выиграл  ")
                break

            step += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
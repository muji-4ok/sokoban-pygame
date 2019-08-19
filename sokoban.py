import pygame as p


class Tile:
    key = ''

    def __repr__(self):
        return self.key

    def __str__(self):
        return repr(self)


class Moveable(Tile):
    pass


class Immovable(Tile):
    pass


class Wall(Immovable):
    key = '#'


class Floor(Moveable):
    key = ' '


class Storage(Moveable):
    key = '.'


class Man(Moveable):
    pass


class Crate(Moveable):
    pass


class ManFloor(Floor, Man):
    key = '@'


class ManStorage(Storage, Man):
    key = '+'


class CrateFloor(Floor, Crate):
    key = 'o'


class CrateStorage(Storage, Crate):
    key = '*'


class Board:
    def __init__(self, filename):
        self.flat = []
        translation = {
            '#': Wall,
            ' ': Floor,
            '@': ManFloor,
            '+': ManStorage,
            'o': CrateFloor,
            '*': CrateStorage,
            '.': Storage
        }

        with open(filename, 'r') as f:
            lines = f.read().split('\n')
            for line in lines:
                objects = []

                for c in line:
                    obj = translation[c]()
                    objects.append(obj)

                self.flat.append(objects)

        self.width = len(self.flat[0])
        self.height = len(self.flat)

    def __getitem__(self, key):
        x, y = key
        return self.flat[y][x]

    def __setitem__(self, key, value):
        x, y = key
        self.flat[y][x] = value

    def __repr__(self):
        return '\n'.join([''.join(map(str, line)) for line in self.flat])

    def __str__(self):
        return repr(self)

    def move(self, x, y, direction):
        dx, dy = direction
        nx, ny = x + dx, y + dy
        cls_name = self[x, y].__class__.__bases__[1].__name__ + self[nx, ny].__class__.__name__
        cls_new = eval(f'{cls_name}')

        self[nx, ny], self[x, y] = cls_new(), self[x, y].__class__.__base__()

    def can_move(self, x, y, direction):
        dx, dy = direction
        nx, ny = x + dx, y + dy

        if isinstance(self[nx, ny], Immovable):
            return False

        if isinstance(self[nx, ny], CrateFloor) or isinstance(self[nx, ny], CrateStorage):
            nnx, nny = nx + dx, ny + dy

            if not (type(self[nnx, nny]) == Floor or type(self[nnx, nny]) == Storage):
                return False

        return True


class Game:
    s = None

    def __init__(self, filename):
        self.b = Board(filename)
        self.h, self.w = self.b.height, self.b.width
        self.man_x, self.man_y = self.find_man()

    def find_man(self):
        for x in range(self.w):
            for y in range(self.h):
                if isinstance(self.b[x, y], Man):
                    return x, y

    def won(self):
        for x in range(self.w):
            for y in range(self.h):
                if type(self.b[x, y]) == CrateFloor:
                    return False

        return True

    def move(self, direction):
        x, y = self.man_x, self.man_y
        dx, dy = direction
        nx, ny = x + dx, y + dy

        if self.b.can_move(x, y, direction):
            if isinstance(self.b[nx, ny], Crate):
                self.b.move(nx, ny, direction)

            self.b.move(x, y, direction)
            self.man_x, self.man_y = nx, ny

    def update(self, key):
        translation = {
            p.K_UP: UP,
            p.K_DOWN: DOWN,
            p.K_LEFT: LEFT,
            p.K_RIGHT: RIGHT
        }
        direction = translation[key]
        self.move(direction)

    def draw(self):
        for x in range(self.w):
            for y in range(self.h):
                self.s.blit(IMAGES[type(self.b[x, y])], (x * TILE_SIZE, y * TILE_SIZE))

    def __repr__(self):
        return repr(self.b)

    def __str__(self):
        return repr(self)


if __name__ == '__main__':
    UP = 0, -1
    DOWN = 0, 1
    RIGHT = 1, 0
    LEFT = -1, 0
    TILE_SIZE = 20
    g = Game('game.txt')
    WIDTH = g.w * TILE_SIZE
    HEIGHT = g.h * TILE_SIZE
    SIZE = WIDTH, HEIGHT

    p.init()
    IMAGES = {
        Wall: p.image.load('wall.png'),
        Floor: p.image.load('floor.png'),
        Storage: p.image.load('storage.png'),
        ManFloor: p.image.load('man_floor.png'),
        ManStorage: p.image.load('man_storage.png'),
        CrateFloor: p.image.load('crate_floor.png'),
        CrateStorage: p.image.load('crate_storage.png')
    }
    screen = p.display.set_mode(SIZE)
    g.s = screen

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                exit()
            elif event.type == p.KEYDOWN:
                g.update(event.key)

        g.draw()
        p.display.update()

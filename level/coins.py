from settings import *
from level.generic import Animated
from support import math, coin_amount, coin_setup

class Coin(Animated):
    def __init__(self, pos, level, speed, pack = None, pos_center=False):
        super().__init__(pos, level.assets["coin"], [level.visible, level.updates, level.coins], level, pos_center)
        self.pack = pack if pack is not None else [None]
        if pack is not None: self.pack.append(self)
        self.add_mover()
        self.add_oscillator(oscillate_speed=speed)

    def collected(self):
        if self in self.pack: self.pack.remove(self)
        if len(self.pack) <= 0:
            self.level.player.pack_completed()
            del self.pack

    def update(self, dt):
        self.mover.move(dt)
        self.oscillator.oscillate()

class CoinBuilder:
    def __init__(self, level):
        self.level = level
        self.start_x = WIDTH+50
        self.size = level.assets["coin"][0].get_width()

    def spawn_coins(self, formation):
        func = None
        match formation:
            case "rect": func = self.rect
            case "line": func = self.line
            case "wave": func = self.wave
            case "area": func = self.area
            case "chess": func = self.chess
            case "circle": func = self.circle
            case "diagonal": func = self.diagonal
        func()

    def line(self):
        direction = choice(["h", "v"])
        amount = coin_amount("line")
        y, speed, pack = coin_setup()
        for i in range(amount):
            if direction == "h": pos = (self.start_x+i*self.size,y)
            else: pos = (self.start_x, y+i*self.size)
            Coin(pos, self.level, speed, pack)

    def diagonal(self):
        amount = coin_amount("diagonal")
        y, speed, pack = coin_setup()
        increase_dir = 1 if y < H_HEIGHT else -1
        offset = 0
        for i in range(amount):
            offset += increase_dir
            Coin((self.start_x+offset*self.size,y+offset*self.size),self.level,speed, pack)

    def wave(self):
        y, speed, pack = coin_setup()
        direction = choice(["h", "v"])
        amount = coin_amount("wave")
        offset = 0
        offset_dir = 1
        for i in range(amount):
            if direction == "h": pos = (self.start_x+i*self.size, y+offset*self.size)
            else: pos = (self.start_x+offset*self.size, y+i*self.size)
            offset += offset_dir
            if offset_dir == 1:
                if offset >= 2:
                    offset = 2
                    offset_dir = -1
            else:
                if offset <= 0:
                    offset = 0
                    offset_dir = 1
            Coin(pos, self.level, speed, pack)

    def rect(self):
        x_amount = coin_amount("rect")
        y_amount = coin_amount("rect")
        y, speed, pack = coin_setup()
        for r in range(x_amount):
            for c in range(y_amount):
                if (r==0 or r== x_amount-1) or (c==0 or c== y_amount-1):
                    Coin((self.start_x+r*self.size,y+c*self.size), self.level, speed, pack)

    def area(self):
        x_amount = coin_amount("area")
        y_amount = coin_amount("area")
        y, speed, pack = coin_setup()
        for r in range(x_amount):
            for c in range(y_amount):
                Coin((self.start_x+r*self.size,y+c*self.size), self.level, speed, pack)

    def chess(self):
        x_amount = coin_amount("chess")
        y_amount = coin_amount("chess")
        y, speed, pack = coin_setup()
        for r in range(x_amount):
            for c in range(y_amount):
                if (r+c)%2 == 0:
                    Coin((self.start_x+r*self.size,y+c*self.size), self.level, speed, pack)

    def circle(self):
        x_amount = coin_amount("circle")
        y_amount = coin_amount("circle")
        x_center = x_amount // 2
        y_center = y_amount // 2
        radius = min(x_amount, y_amount) // 3
        sy, speed, pack = coin_setup()
        for y in range(y_amount):
            for x in range(x_amount):
                distance = math.sqrt((x - x_center)**2 + (y - y_center)**2)
                if distance <= radius:
                    Coin((self.start_x+x*self.size,sy+y*self.size), self.level, speed, pack)
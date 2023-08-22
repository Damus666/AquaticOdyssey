from settings import *
from level.sprites import Tile, Island, AngledTile, Prop, Mine, Fish, BombFish, Powerup, BallIsland, Bubble
from support import next_time, weighted_choice, rand_offset, confined_y, chance, chance_g
from level.coins import CoinBuilder

class Spawner:
    def __init__(self, level):
        self.level = level
        self.level.spawners.append(self)

    def spawn(self):...
    def reset(self):...
    def resume(self):...
    def init_spawn(self):...

class BubbleGenerator:
    def __init__(self, spawner):
        self.spawner = spawner
        self.level = spawner.level
        self.pos_x = WIDTH*2
        self.pos_y = HEIGHT-TOP_H//2

        self.last_spawn = 0
        self.next_spawn_time = next_time("bubble-g")

    def update(self, dt):
        self.pos_x -= self.level.speed*dt
        if self.pos_x <= 0: self.spawner.generators.remove(self)

        if pygame.time.get_ticks()-self.last_spawn >= self.next_spawn_time:
            self.last_spawn = pygame.time.get_ticks()
            self.next_spawn_time = next_time("bubble-g")
            Bubble((self.pos_x+rand_offset(BUBBLE_OFFSET),self.pos_y), choice(self.level.assets["fx"]["bubble-list"]), self.level)

class BubbleSpawner(Spawner):
    def __init__(self, level):
        super().__init__(level)

        self.last_spawn = 0
        self.next_spawn_time = next_time("bubble-s")

        self.generators = []

    def spawn(self):
        if pygame.time.get_ticks()-self.last_spawn >= self.next_spawn_time:
            self.last_spawn = pygame.time.get_ticks()
            self.next_spawn_time = next_time("bubble-s")
            self.generators.append(BubbleGenerator(self))

    def update(self, dt):
        for generator in self.generators.copy(): generator.update(dt)

    def reset(self): self.last_spawn = 0
    def resume(self): self.last_spawn = pygame.time.get_ticks()

class FishSpawner(Spawner):
    def __init__(self, level):
        super().__init__(level)

        self.last_normal_spawn = 0
        self.last_dart_spawn = 0
        self.last_bomb_spawn = 0

        self.next_normal_time = next_time("fish-normal")
        self.next_dart_time = next_time("fish-dart")
        self.next_bomb_time = next_time("fish-bomb")

        self.normal_enabled = False
        self.dart_enabled = False
        self.bomb_enabled = False

    def reset(self):
        self.normal_enabled = False
        self.dart_enabled = False
        self.bomb_enabled = False

    def resume(self):
        self.last_normal_spawn = pygame.time.get_ticks()
        self.last_dart_spawn = pygame.time.get_ticks()
        self.last_bomb_spawn = pygame.time.get_ticks()

    def spawn(self):
        ticks = pygame.time.get_ticks()

        if self.normal_enabled and ticks-self.last_normal_spawn >= self.next_normal_time:
            self.last_normal_spawn = ticks
            self.next_normal_time = next_time("fish-normal")
            pos = (WIDTH+200, confined_y())
            last = Fish(pos, "fish", self.level, FISH_SPEED["normal"])
            if chance("second-normal-fish"):
                Fish((last.rect.right+last.rect.w//2,pos[1]), "fish", self.level, FISH_SPEED["normal"])
            self.level.ui.warn(pos[1])

        if self.dart_enabled and ticks-self.last_dart_spawn >= self.next_dart_time:
            self.last_dart_spawn = ticks
            self.next_dart_time = next_time("fish-dart")
            amount = randint(*DART_AMOUNT_RANGE)
            y = confined_y(2,3)
            for i in range(amount):
                fish = Fish((WIDTH+200, y), "fish-dart", self.level, FISH_SPEED["dart"])
                self.level.ui.warn(y)
                y += 5+fish.rect.h

        if self.bomb_enabled and ticks-self.last_bomb_spawn >= self.next_bomb_time:
            self.last_bomb_spawn = ticks
            self.next_bomb_time = next_time("fish-bomb")
            pos = (WIDTH+200, confined_y())
            BombFish(pos, self.level, FISH_SPEED["bomb"])
            self.level.ui.warn(pos[1])

        if not self.normal_enabled:
            if self.level.player.score >= FISH_ENABLE_SCORE["normal"]: self.normal_enabled = True
        if not self.dart_enabled:
            if self.level.player.score >= FISH_ENABLE_SCORE["dart"]: self.dart_enabled = True
        if not self.bomb_enabled:
            if self.level.player.score >= FISH_ENABLE_SCORE["bomb"]: self.bomb_enabled = True

class CoinSpawner(Spawner):
    def __init__(self, level):
        super().__init__(level)

        self.last_spawn = 0
        self.next_spawn_time = next_time("coin")
        
        self.builder = CoinBuilder(self.level)

    def spawn(self):
        if pygame.time.get_ticks()-self.last_spawn >= self.next_spawn_time:
            self.next_spawn_time = next_time("coin")
            self.last_spawn = pygame.time.get_ticks()
            self.builder.spawn_coins(choice(list(COINS_FORMATIONS.keys())))

    def reset(self):  self.last_spawn = 0
    def resume(self): self.last_spawn = pygame.time.get_ticks()

class PowerupSpawner(Spawner):
    def __init__(self, level):
        super().__init__(level)

        self.last_spawn = 0
        self.next_spawn_time = next_time("powerup")

    def spawn(self):
        if pygame.time.get_ticks()-self.last_spawn >= self.next_spawn_time:
            self.next_spawn_time = next_time("powerup")-self.level.player.score*POWERUP_SPAWN_MUL
            self.last_spawn = pygame.time.get_ticks()
            Powerup((WIDTH, confined_y()),weighted_choice(list(POWERUP_TYPES.keys()), POWERUP_WEIGHTS), self.level)

    def reset(self): self.last_spawn = 0
    def resume(self): self.last_spawn = pygame.time.get_ticks()

class MineSpawner(Spawner):
    def __init__(self, level):
        super().__init__(level)

        self.last_spawn = 0
        self.next_spawn_time = 0
        self.last_mine = None
        self.amount_level = 0

    def reset(self):
        self.last_spawn = 0
        self.amount_level = 0
    
    def resume(self): self.last_spawn = pygame.time.get_ticks()

    def spawn(self):
        if pygame.time.get_ticks()-self.last_spawn>=self.next_spawn_time:
            self.next_spawn_time = next_time("mine")
            self.last_spawn = pygame.time.get_ticks()
            y = confined_y()
            x = WIDTH + 200
            amount = weighted_choice(MINE_AMOUNTS,MINE_AMOUNT_WEIGHTS[self.amount_level])
            for i in range(amount):
                size = choice(["big","normal","small"])
                mine = Mine((x,y), self.level, size)
                self.level.ui.warn(y)
                x += mine.rect.w*1.2+10

        if self.amount_level == 0 and self.level.player.score >= 100: self.amount_level += 1
        if self.amount_level == 1 and self.level.player.score >= 300: self.amount_level += 1
        if self.amount_level == 2 and self.level.player.score >= 1000: self.amount_level += 1
        if self.amount_level == 3 and self.level.player.score >= 5000: self.amount_level += 1

class PropSpawner(Spawner):
    def __init__(self, level):
        super().__init__(level)

        self.last_big_spawn = 0
        self.big_next_spawn_time = 0
        self.last_small_spawn = 0
        self.small_next_spawn_time = 0
        self.last_big_prop = None

    def reset(self):
        self.last_big_spawn = 0
        self.last_small_spawn = 0

    def resume(self):
        self.last_big_spawn = pygame.time.get_ticks()
        self.last_small_spawn = pygame.time.get_ticks()

    def spawn(self):
        if pygame.time.get_ticks()-self.last_big_spawn >= self.big_next_spawn_time:
            chosen = choice(["arc", "temple", "totem", "spike"])
            direction = "bottom"
            if chosen != "temple" and chosen != "totem":
                if chance("direction-flip"): direction = "top"
            if chosen == "totem": chosen = choice(["totem-n", "totem-r"])
            if chosen == "arc": chosen = choice(["arc-l", "arc-r"])
            if chosen == "spike": chosen = choice(["spike-l","spike-r"])
            x = max(self.last_big_prop.rect.right if self.last_big_prop else WIDTH+100, WIDTH+100)
            self.last_big_prop = Prop(self.level, chosen, direction, x)
            self.big_next_spawn_time = next_time("prop-big")
            self.last_big_spawn = pygame.time.get_ticks()
            if "spike" in chosen or "arc" in chosen:
                self.level.ui.warn(self.last_big_prop.rect.centery)

        if pygame.time.get_ticks()-self.last_small_spawn >= self.small_next_spawn_time:
            chosen = choice(["algee","coral-y","coral-r"])
            direction = choice(["top","bottom"])
            Prop(self.level, chosen, direction, WIDTH)
            self.small_next_spawn_time = next_time("prop-small")
            self.last_small_spawn = pygame.time.get_ticks()

class IslandSpawner(Spawner):
    def __init__(self, level):
        super().__init__(level)

        self.last_spawn = 0
        self.scale_range = ISLAND_SCALES["normal"]
        self.ball_scale = ISLAND_SCALES["ball"]
        self.next_spawn_time = 2000

    def spawn(self):
        if pygame.time.get_ticks()-self.last_spawn >= self.next_spawn_time:
            self.next_spawn_time = next_time("island")
            if chance_g("normal-island-g"):
                Island(self.level, uniform(self.scale_range.x,self.scale_range.y), randint(int(TOP_H), int(HEIGHT-BOTTOM_H*2)))
            else:
                island = BallIsland(self.level, uniform(self.ball_scale.x,self.ball_scale.y), randint(int(TOP_H), int(HEIGHT-BOTTOM_H*2)))
                self.level.ui.warn(island.rect.centery)
            self.last_spawn = pygame.time.get_ticks()

    def reset(self): self.last_spawn = 0
    def resume(self): self.last_spawn = pygame.time.get_ticks()

class TileSpawner(Spawner):
    def __init__(self, level):
        super().__init__(level)
        self.last_tile = None

        self.last_angled = 0
        self.next_angled_time = next_time("angled-tile")

    def reset(self): self.last_angled = 0
    def resume(self): self.last_angled = pygame.time.get_ticks()

    def init_spawn(self):
        self.last_tile = None
        for i in range(int(WIDTH//TILE_W)+1):
            top = Tile(self.level, "top", self.last_tile.rect.right if self.last_tile else 0)
            Tile(self.level, "bottom", self.last_tile.rect.right if self.last_tile else 0)
            self.last_tile = top

    def spawn(self):
        if not self.last_tile or self.last_tile.rect.left < WIDTH-TILE_W:
            top = Tile(self.level, "top", self.last_tile.rect.right)
            Tile(self.level, "bottom", self.last_tile.rect.right)
            self.last_tile = top

            if pygame.time.get_ticks()-self.last_angled >= self.next_angled_time:
                self.last_angled = pygame.time.get_ticks()
                self.next_angled_time = next_time("angled-tile")
                direction = choice(["top", "bottom"])
                left = AngledTile(self.level, direction, "right", self.last_tile.rect.right)
                AngledTile(self.level, direction, "left", left.rect.right)
from settings import *
import json, os
from support import quit_all, get_window, next_time
from level.ui import UI
from level.bg import BG
from level.player import Player
from level.spawners import TileSpawner, IslandSpawner, PropSpawner, MineSpawner, PowerupSpawner, CoinSpawner, FishSpawner, Spawner, BubbleSpawner
from level.transition import Transition
from menu.pausemenu import PauseMenu
from menu.deathmenu import DeathMenu

class Level:
    def __init__(self, main):
        self.main = main
        self.audio = self.main.audio
        self.assets = self.main.asset_loader
        self.display_surface = get_window()

        self.visible = pygame.sprite.Group()
        self.visible_top = pygame.sprite.Group()
        self.visible_behind = pygame.sprite.Group()
        self.visible_tiles = pygame.sprite.Group()
        self.all = pygame.sprite.Group()
        self.updates = pygame.sprite.Group()
        self.islands = pygame.sprite.Group()
        self.fishes = pygame.sprite.Group()
        self.mines = pygame.sprite.Group()
        self.collidable = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.paused = False
        self.speed = LEVEL_SPEED
        self.bg = BG(self)
        self.ui = UI(self)
        self.player = Player(self)
        self.transition = Transition(self)
        self.spawners:list[Spawner] = []
        self.tile_spawner = TileSpawner(self)
        self.island_spawner = IslandSpawner(self)
        self.prop_spawner = PropSpawner(self)
        self.mine_spawner = MineSpawner(self)
        self.powerup_spawner = PowerupSpawner(self)
        self.coin_spawner = CoinSpawner(self)
        self.fish_spawner = FishSpawner(self)
        self.bubble_spawner = BubbleSpawner(self)

        self.pause_menu = PauseMenu(self)
        self.death_menu = DeathMenu(self)

        self.last_wave = 0
        self.next_wave_time = next_time("wave")
        self.load_data()

    def post_menu(self):
        self.player.post_menu()

    def died(self):
        self.transition.start("x", -1, "Game Over")
        self.audio.pause_music()

    def retry(self):
        self.reset()
        self.start()

    def pause(self):
        self.paused = True
        self.audio.pause_music()
        self.transition.start("x", -1, "Pause")

    def resume(self):
        self.paused = False
        self.audio.resume_music()
        for spawner in self.spawners: spawner.resume()
        self.transition.start("x", 1, "Level")

    def reset(self):
        self.save_data()
        self.bg.empty_lights()
        for sprite in self.all:
            if not sprite.is_player: sprite.kill()
        for spawner in self.spawners: spawner.reset()
        self.audio.stop_fx("ambience")
        self.speed = LEVEL_SPEED
        self.paused = False

    def start(self):
        self.load_data()
        self.player.reset()
        for spawner in self.spawners: spawner.init_spawn()
        self.bg.init_lights()
        self.audio.play_music("level","ogg")
        self.audio.play_fx("ambience", -1)
        self.transition.start("x", 1, "Level")

    def load_data(self):
        if not os.path.exists("data/level.save"): self.save_data()
        with open("data/level.save","rb") as file:
            encoded_data = file.read()
            string_data = self.main.fernet.decrypt(encoded_data)
            data = json.loads(string_data)
            self.player.high_score = data["high-score"]
            self.player.coins = data["coins"]

    def save_data(self):
        with open("data/level.save","wb") as file:
            data = {
                "high-score":self.player.high_score,
                "coins":self.player.coins
            }
            string_data = json.dumps(data)
            encoded_data = self.main.fernet.encrypt(string_data.encode())
            file.write(encoded_data)
            
        self.audio.save_data()
    
    def quit(self):
        self.save_data()
        quit_all()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not self.player.dead:
                    if self.paused: self.resume()
                    else: self.pause()

    def update_wave(self):
        if pygame.time.get_ticks()-self.last_wave >= self.next_wave_time:
            self.last_wave = pygame.time.get_ticks()
            self.next_wave_time = next_time("wave")
            self.audio.play_fx("wave")

    def update_speed(self, dt):
        self.speed += SPEED_INCREASE*dt
        self.speed = min(self.speed, 900)

    def update(self, dt):
        self.transition.update(dt)
        if self.paused:
            self.pause_menu.update(dt)
            return
        if self.player.dead:
            self.death_menu.update(dt)
            return

        self.bg.update(dt)
        self.updates.update(dt)
        self.ui.update(dt)

        self.update_speed(dt)
        self.update_wave()
        
        for spawner in self.spawners: spawner.spawn()
        self.bubble_spawner.update(dt)

    def draw(self):
        self.bg.draw()

        self.visible_behind.draw(self.display_surface)
        self.visible.draw(self.display_surface)

        self.bg.draw_lights()

        self.visible_tiles.draw(self.display_surface)
        self.visible_top.draw(self.display_surface)

        if not self.paused and not self.player.dead: self.ui.draw()
        if self.paused and self.transition.midway: self.pause_menu.draw()
        if self.player.dead and self.transition.midway: self.death_menu.draw()
        self.transition.draw()
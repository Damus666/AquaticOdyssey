from settings import *
import json, webbrowser, os
from support import quit_all, get_window, build_menu, os_range_ui, math, main_font
from level.bg import BG
from menu.menuplayer import MenuPlayer
from menu.elements import MineButton, ButtonOscillating
from menu.shop import Shop

class Menu:
    def __init__(self, main):
        self.main = main
        self.level = self.main.level
        self.audio = self.main.audio
        self.assets = main.asset_loader
        self.display_surface = get_window()

        self.sprites = pygame.sprite.Group()
        self.mines = pygame.sprite.Group()
        self.inventory = DEFAULT_DATA.copy()
        self.bg = BG(self.main.level, True)

        self.menu_img, self.inner_rect = build_menu(self.assets["menu"], WIDTH//2, HEIGHT//10, h_plus1=False)
        self.menu_rect = self.menu_img.get_rect(center=(H_WIDTH, H_HEIGHT-H_HEIGHT//2-H_HEIGHT//10))
        self.static_menu_rect = self.menu_rect.copy()
        self.inner_rect.center = self.menu_rect.center
        self.menu_start_y = self.menu_rect.centery
        self.menu_o_offset = 15
        self.menu_pos_y = self.menu_start_y
        self.menu_o_speed = os_range_ui()
        
        self.title_font = main_font(55)
        self.title_surf = self.title_font.render(WINDOW_TITLE, False, "white")
        self.title_rect = self.title_surf.get_rect(center=self.inner_rect.center)
        self.font = main_font(20)

        islandimg = pygame.transform.scale_by(self.assets["menu"]["island"], 0.8)
        self.cc_art_btn = ButtonOscillating(islandimg, self.font.render("Art Credits", False, "white"), 
                                            midleft=(0, HEIGHT), text_offset = (0, -islandimg.get_height()//4))
        self.cc_art_rect = self.cc_art_btn.hitbox.copy()
        self.cc_music_btn = ButtonOscillating(islandimg, self.font.render("Music Credits", False, "white"), 
                                            midright=(WIDTH, HEIGHT), text_offset = (0, -islandimg.get_height()//4))
        self.cc_music_rect = self.cc_music_btn.hitbox.copy()

        self.shop = Shop(self)
        self.in_shop = False
        self.back()

    def back_from_shop(self):
        self.in_shop = False
        self.refresh_sprites()

    def load_data(self):
        if not os.path.exists("data/menu.save"): self.save_data()
        with open("data/menu.save", "rb") as file:
            encoded_data = file.read()
            data = self.main.fernet.decrypt(encoded_data)
            self.inventory = json.loads(data)

    def save_data(self):
        with open("data/menu.save", "wb") as file:
            data = json.dumps(self.inventory)
            encoded_data = self.main.fernet.encrypt(data.encode())
            file.write(encoded_data)

    def on_play_click(self):
        self.main.start_level()

    def on_quit_click(self):
        self.quit()

    def on_shop_click(self):
        if not self.main.in_level: self.main.back_to_menu()
        self.in_shop = True

    def quit(self):
        self.save_data()
        quit_all()

    def make_high_score(self):
        self.high_score_surf = self.font.render(f"High Score: {self.level.player.high_score}", False, "white")
        self.high_score_rect = self.high_score_surf.get_rect(midbottom=(H_WIDTH, HEIGHT))

    def back(self):
        self.load_data()
        self.refresh_sprites()
        self.make_high_score()
        self.shop.build_shop()
        self.shop.refresh_coins()
        self.audio.play_music("menu")

    def refresh_sprites(self):
        self.bg.empty_lights()
        for sprite in self.sprites: sprite.kill()
        self.menu_player = MenuPlayer(self)
        
        self.play_mine = MineButton(self, (H_WIDTH, H_HEIGHT+H_HEIGHT//1.7), "big", 1.5, 
                                    self.font.render("Play", False, "white"), self.on_play_click)
        self.quit_mine = MineButton(self, (H_WIDTH+H_WIDTH//3, H_HEIGHT+H_HEIGHT//2), "big", 1,
                                    self.font.render("Quit", False, "white"), self.on_quit_click)
        self.shop_mine = MineButton(self, (H_WIDTH-H_WIDTH//3, H_HEIGHT+H_HEIGHT//2), "big", 1,
                                    self.font.render("Shop", False, "white"), self.on_shop_click)
        
        self.bg.init_lights()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()

    def update_menu(self):
        self.menu_pos_y = self.menu_start_y + math.sin(pygame.time.get_ticks()*self.menu_o_speed)*self.menu_o_offset
        self.menu_rect.centery = round(self.menu_pos_y)
        self.inner_rect.centery = self.menu_rect.centery
        self.title_rect.center = self.inner_rect.center

    def update(self, dt):
        self.bg.update(dt)

        if self.in_shop:
            self.shop.update(dt)
            return
        
        self.update_menu()
        self.sprites.update(dt)

        if self.cc_art_btn.check():
            webbrowser.open_new_tab("https://opengameart.org/content/underwater-diving-pack")
            webbrowser.open_new_tab("https://www.patreon.com/ansimuz")
        if self.cc_music_btn.check():
            webbrowser.open_new_tab("pacethemusician@hotmail.com")
            webbrowser.open_new_tab("https://soundcloud.com/pascalbelisle")

    def draw(self):
        self.bg.draw()
        
        if self.in_shop: self.shop.draw()
        else:
            self.sprites.draw(self.display_surface)

            self.display_surface.blit(self.menu_img, self.menu_rect)
            self.display_surface.blit(self.title_surf, self.title_rect)

            self.cc_art_btn.draw()
            self.cc_music_btn.draw()

            self.display_surface.blit(self.high_score_surf, self.high_score_rect)

        self.bg.draw_lights()
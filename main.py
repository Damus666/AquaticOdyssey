from settings import *
from level.level import Level
from menu.menu import Menu
from assetloader import AssetLoader
from audio import Audio
from cryptography.fernet import Fernet

class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode(WINDOW_SIZES, pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(WINDOW_TITLE)

        self.fernet = Fernet(MENU_RATIO)
        self.asset_loader = AssetLoader()
        self.audio = Audio(self)
        self.level = Level(self)
        self.menu = Menu(self)
        self.level.post_menu()
        self.in_level = False

    def start_level(self):
        self.level.start()
        self.in_level = True

    def back_to_menu(self):
        self.level.reset()
        self.menu.back()
        self.in_level = False

    def run(self):
        while True:
            dt = self.clock.tick(WINDOW_FPS)*0.001
            if self.in_level:
                self.level.event_loop()
                self.level.update(dt)
                self.level.draw()
            else:
                self.menu.event_loop()
                self.menu.update(dt)
                self.menu.draw()
            pygame.display.update()

if __name__ == "__main__": Main().run()
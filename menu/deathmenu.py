from settings import *
from support import center_menu_chains, get_window, main_font, quit_all
from menu.elements import ButtonOscillating

class DeathMenu:
    def __init__(self, level):
        self.level = level
        self.assets = self.level.assets
        self.menu_assets = self.assets["menu"]
        self.display_surface = get_window()

        self.menu_img, self.menu_rect, self.inner_rect, self.chain_rects_v, self.chain_rects_h = \
            center_menu_chains(self.menu_assets, 1.8, 1.7, 0, 2)
        self.overlay_img = pygame.Surface(WINDOW_SIZES, pygame.SRCALPHA)
        self.overlay_img.fill("black")
        self.overlay_img.set_alpha(200)

        self.title_font = main_font(55)
        self.title_img = self.title_font.render("Game Over", False, "white")
        self.title_rect = self.title_img.get_rect(midtop=self.inner_rect.midtop)

        self.font = main_font(20)
        self.retry_button = ButtonOscillating(self.menu_assets["mine-big"], self.font.render("Retry [R]", False, "white"), midtop=(self.title_rect.midbottom))
        self.menu_button = ButtonOscillating(self.menu_assets["mine-big"], self.font.render("Menu", False, "white"), midright=(self.retry_button.hitbox.midleft))
        self.quit_button = ButtonOscillating(self.menu_assets["mine-big"], self.font.render("Quit", False, "white"), midleft=(self.retry_button.hitbox.midright))

    def update(self, dt):
        if self.retry_button.check(self.level.audio) or pygame.key.get_pressed()[pygame.K_r]:self.level.retry()
        if self.menu_button.check(self.level.audio):
            self.level.save_data()
            self.level.main.back_to_menu()
        if self.quit_button.check(self.level.audio): self.level.quit()

        new_high_score = " (New High Score)" if self.level.player.new_high_score else ""
        self.info_surf = self.font.render(f"Final Score: {self.level.player.score}{new_high_score}, Coins: {self.level.player.coins}", False, "white")
        self.info_rect = self.info_surf.get_rect(midtop=(self.inner_rect.centerx, 
                            self.retry_button.start_y+self.retry_button.hitbox.h//2+self.retry_button.o_offset+UI_SPACING))

    def draw(self):
        self.display_surface.blit(self.overlay_img, (0,0))
        for chain_rect in self.chain_rects_v: self.display_surface.blit(self.menu_assets["chain"], chain_rect)
        for chain_rect in self.chain_rects_h: self.display_surface.blit(self.menu_assets["chain-rot"], chain_rect)
        self.display_surface.blit(self.menu_img, self.menu_rect)

        self.display_surface.blit(self.title_img, self.title_rect)
        self.retry_button.draw()
        self.quit_button.draw()
        self.menu_button.draw()

        self.display_surface.blit(self.info_surf,self.info_rect)
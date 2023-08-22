from settings import *
from support import center_menu_chains, get_window, main_font, quit_all
from menu.elements import ButtonOscillating

class PauseMenu:
    def __init__(self, level):
        self.level = level
        self.audio = self.level.audio
        self.assets = self.level.assets
        self.menu_assets = self.assets["menu"]
        self.display_surface = get_window()

        self.menu_img, self.menu_rect, self.inner_rect, self.chain_rects_v, self.chain_rects_h = \
            center_menu_chains(self.menu_assets, 1.8, 1.4, 3, 0)
        self.overlay_img = pygame.Surface(WINDOW_SIZES, pygame.SRCALPHA)
        self.overlay_img.fill("black")
        self.overlay_img.set_alpha(200)

        self.title_font = main_font(55)
        self.title_img = self.title_font.render("Paused", False, "white")
        self.title_rect = self.title_img.get_rect(midtop=self.inner_rect.midtop)

        self.font = main_font(20)
        self.resume_button = ButtonOscillating(self.menu_assets["mine-big"], self.font.render("Resume", False, "white"), midtop=(self.title_rect.midbottom))
        self.menu_button = ButtonOscillating(self.menu_assets["mine-big"], self.font.render("Menu", False, "white"), midright=(self.resume_button.hitbox.midleft))
        self.quit_button = ButtonOscillating(self.menu_assets["mine-big"], self.font.render("Quit", False, "white"), midleft=(self.resume_button.hitbox.midright))

        self.vol_font = main_font(25)
        self.fx_vol_y = self.resume_button.hitbox.bottom+self.resume_button.o_offset+self.resume_button.hitbox.w//4
        self.music_vol_y = self.fx_vol_y+self.resume_button.hitbox.w//3+UI_SPACING
        vol_w = self.vol_font.size("Music Volume: Full")[0]+UI_SPACING
        self.fx_minus = ButtonOscillating(self.menu_assets["mine-small"], self.font.render("-", False, "white"),
                                          midright=(self.inner_rect.centerx-vol_w//2, self.fx_vol_y), o_offset=5)
        self.fx_plus = ButtonOscillating(self.menu_assets["mine-small"], self.font.render("+", False, "white"),
                                          midleft=(self.inner_rect.centerx+vol_w//2, self.fx_vol_y), o_offset=5)
        self.music_minus = ButtonOscillating(self.menu_assets["mine-small"], self.font.render("-", False, "white"),
                                          midright=(self.inner_rect.centerx-vol_w//2, self.music_vol_y), o_offset=5)
        self.music_plus = ButtonOscillating(self.menu_assets["mine-small"], self.font.render("+", False, "white"),
                                          midleft=(self.inner_rect.centerx+vol_w//2, self.music_vol_y), o_offset=5)

    def update(self, dt):
        # main
        if self.resume_button.check(self.level.audio): self.level.resume()
        if self.menu_button.check(self.level.audio):
            self.level.save_data()
            self.level.main.back_to_menu()
        if self.quit_button.check(self.level.audio): self.level.quit()

        # fx volume str
        vol = round(self.audio.fx_volume,1)
        string = f"Sound Volume: {vol}"
        if vol == 0: string = "Sound Volume: Off"
        elif vol == 1: string = "Sound Volume: Full"
        self.fx_vol_surf = self.vol_font.render(string,True,"white")
        self.fx_vol_rect = self.fx_vol_surf.get_rect(center=(self.inner_rect.centerx, self.fx_vol_y))
        # music volume str
        vol = round(self.audio.music_volume,1)
        string = f"Music Volume: {vol}"
        if vol == 0: string = "Music Volume: Off"
        elif vol == 1: string = "Music Volume: Full"
        self.music_vol_surf = self.vol_font.render(string,True,"white")
        self.music_vol_rect = self.music_vol_surf.get_rect(center=(self.inner_rect.centerx, self.music_vol_y))
        
        # volume + -
        if self.fx_minus.check(): self.audio.step_fx_volume(-1)
        if self.fx_plus.check(): self.audio.step_fx_volume(1)
        if self.music_minus.check(): self.audio.step_music_volume(-1)
        if self.music_plus.check(): self.audio.step_music_volume(1)

    def draw(self):
        # bg
        self.display_surface.blit(self.overlay_img, (0,0))
        for chain_rect in self.chain_rects_v: self.display_surface.blit(self.menu_assets["chain"], chain_rect)
        for chain_rect in self.chain_rects_h: self.display_surface.blit(self.menu_assets["chain-rot"], chain_rect)
        self.display_surface.blit(self.menu_img, self.menu_rect)
        # main
        self.display_surface.blit(self.title_img, self.title_rect)
        self.resume_button.draw()
        self.quit_button.draw()
        self.menu_button.draw()
        # volume strs
        self.display_surface.blit(self.fx_vol_surf,self.fx_vol_rect)
        self.display_surface.blit(self.music_vol_surf,self.music_vol_rect)
        # volume + -
        self.fx_minus.draw()
        self.fx_plus.draw()
        self.music_minus.draw()
        self.music_plus.draw()
from settings import *
from support import get_window, main_font, center_menu_chains
from menu.elements import ButtonOscillating

class Settings:
    def __init__(self, menu):
        self.menu = menu
        self.assets = self.menu.assets
        self.display_surface = get_window()
        self.font = self.menu.font
        self.shop_font = main_font(24)

        self.menu_img, self.menu_rect, self.inner_rect, self.chain_rects_v, self.chain_rects_h = \
            center_menu_chains(self.assets["menu"], 1.7, 1.5, 3, 2, True,)
        
        self.title_surf = self.menu.title_font.render("Settings", False, "white")
        self.title_rect = self.title_surf.get_rect(midtop=self.inner_rect.midtop)

        self.back_button = ButtonOscillating(self.assets["enemies"]["mine"]["normal"],
                            self.font.render("Back", False, "white"), topleft=self.menu_rect.topleft)
        
        self.fps_label = self.font.render(f"Show FPS: ", False, "white")
        self.lights_label = self.font.render(f"Enable Lights: ", False, "white")
        self.fps_label_rect = self.fps_label.get_rect(midright=(self.inner_rect.centerx, self.inner_rect.centery-self.inner_rect.h//10))
        self.lights_label_rect = self.lights_label.get_rect(midright=(self.inner_rect.centerx, self.inner_rect.centery+self.inner_rect.h/6))

        self.fps_button = ButtonOscillating(self.assets["enemies"]["mine"]["normal"],
                            self.font.render(f"Yes" if self.menu.show_fps else f"No", False, "white"), midleft=self.fps_label_rect.midright)
        self.lights_button = ButtonOscillating(self.assets["enemies"]["mine"]["normal"],
                            self.font.render(f"Yes" if self.menu.enable_lights else f"No", False, "white"), midleft=self.lights_label_rect.midright)
    
    def toggle_fps(self):
        self.menu.show_fps = not self.menu.show_fps
        self.fps_button.refresh_text(self.font.render(f"Yes" if self.menu.show_fps else f"No", False, "white"))

    def toggle_lights(self):
        self.menu.enable_lights = not self.menu.enable_lights
        self.lights_button.refresh_text(self.font.render(f"Yes" if self.menu.enable_lights else f"No", False, "white"))

    def refresh(self):
        self.fps_button.refresh_text(self.font.render(f"Yes" if self.menu.show_fps else f"No", False, "white"))
        self.lights_button.refresh_text(self.font.render(f"Yes" if self.menu.enable_lights else f"No", False, "white"))

    def update(self, dt):
        if self.back_button.check(self.menu.audio):
            self.menu.back_from_settings()
        if self.fps_button.check(self.menu.audio):
            self.toggle_fps()
        if self.lights_button.check(self.menu.audio):
            self.toggle_lights()

    def draw(self):
        for chain_rect in self.chain_rects_v: self.display_surface.blit(self.assets["menu"]["chain"], chain_rect)
        for chain_rect in self.chain_rects_h: self.display_surface.blit(self.assets["menu"]["chain-rot"], chain_rect)
        self.display_surface.blit(self.menu_img, self.menu_rect)
        self.display_surface.blit(self.title_surf, self.title_rect)
        self.back_button.draw()
        self.display_surface.blit(self.fps_label, self.fps_label_rect)
        self.display_surface.blit(self.lights_label, self.lights_label_rect)
        self.fps_button.draw()
        self.lights_button.draw()

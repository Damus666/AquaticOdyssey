from settings import *
from level.sprites import Warning
from support import main_font, get_window, radial_image

class UI:
    def __init__(self, level):
        self.level = level
        self.assets = level.assets
        self.display_surface = get_window()

        self.ui_font = main_font(28)
        self.coin_img, self.heart_img, self.heart_empty_img = pygame.transform.scale_by(self.assets["ui"]["coin"],1.2*BG_SCALE),\
              pygame.transform.scale_by(self.assets["ui"]["heart"], 2*BG_SCALE), pygame.transform.scale_by(self.assets["ui"]["heart-empty"], 2*BG_SCALE)

        self.coin_rect = self.coin_img.get_rect(topleft=(UI_SPACING,10))
        self.heart_rect = self.heart_img.get_rect(topleft=(UI_SPACING,self.coin_rect.bottom+UI_SPACING))

        self.ui_font_s = main_font(18)
        self.new_high_score_img = self.ui_font_s.render("NEW HIGH SCORE!", False, "white")
        self.new_high_score_rect = self.new_high_score_img.get_rect(center=(H_WIDTH,0))

        self.warning_img = pygame.transform.flip(pygame.transform.scale_by(self.assets["ui"]["emark"],2.5*BG_SCALE), True, False)
        self.warnings = pygame.sprite.Group()

        self.powerups_imgs ={
            "energy": pygame.transform.scale_by(self.assets["ui"]["energy"], POWERUP_TYPES["energy"][1]*0.8),
            "magnet": pygame.transform.scale_by(self.assets["ui"]["magnet"], POWERUP_TYPES["magnet"][1]*0.8),
        }
        self.powerup_lowalpha = {
            "energy": self.powerups_imgs["energy"].copy(),
            "magnet": self.powerups_imgs["magnet"].copy(),
        }
        for img in self.powerup_lowalpha.values(): img.set_alpha(50)

    def warn(self, centery):
        Warning((WIDTH-10-self.warning_img.get_width()//2, centery),self.warning_img, [self.warnings], self.level)

    def update(self, dt):
        self.coins_txt_img = self.ui_font.render(f"{self.level.player.coins}", False, "white")
        self.lives_txt_img = self.ui_font.render(f"{self.level.player.lives}", False, "white")
        self.score_txt_img = self.ui_font.render(f"SCORE: {self.level.player.score}", False, "white")
        self.high_score_img = self.ui_font_s.render(f"HIGH SCORE: {self.level.player.high_score}", False, "white")

        self.coins_txt_rect = self.coins_txt_img.get_rect(midleft = (self.coin_rect.right+UI_SPACING,self.coin_rect.centery))
        self.lives_txt_rect = self.lives_txt_img.get_rect(midleft = (self.coin_rect.right+UI_SPACING,self.heart_rect.centery))
        self.score_txt_rect = self.score_txt_img.get_rect(midtop = (H_WIDTH,18*BG_SCALE))
        self.high_score_rect = self.high_score_img.get_rect(midtop = (H_WIDTH, self.score_txt_rect.bottom+UI_SPACING//2))
        self.new_high_score_rect.center = self.high_score_rect.center

        self.warnings.update(dt)

    def draw(self):
        # coins, lives
        self.display_surface.blit(self.coin_img, self.coin_rect)
        self.display_surface.blit(self.heart_img if self.level.player.lives >= 1 else self.heart_empty_img, self.heart_rect)
        # coin, lives, score TXT
        self.display_surface.blit(self.coins_txt_img, self.coins_txt_rect)
        self.display_surface.blit(self.lives_txt_img, self.lives_txt_rect)
        self.display_surface.blit(self.score_txt_img, self.score_txt_rect)
        # high score
        if self.level.player.new_high_score: self.display_surface.blit(self.new_high_score_img,self.new_high_score_rect)
        else: self.display_surface.blit(self.high_score_img,self.high_score_rect)
        # powerups
        for i, (name, powerup) in enumerate(self.level.player.powerups.items()):
            img = self.powerup_lowalpha[name]
            rect = img.get_rect(topright = (WIDTH-UI_SPACING-i*(img.get_width()+UI_SPACING),UI_SPACING))
            self.display_surface.blit(img, rect)
            time_passed = (pygame.time.get_ticks()-powerup["born"])
            angle = (360*time_passed)/powerup["lifetime"]
            erased_surf = radial_image(self.powerups_imgs[name], angle)
            self.display_surface.blit(erased_surf, rect)
        # warnings
        self.warnings.draw(self.display_surface)
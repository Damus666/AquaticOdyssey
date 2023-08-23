from settings import *
from level.generic import AnimatedStatus
from support import rect_circle, main_font, get_window

class MenuPlayer(AnimatedStatus):
    def __init__(self, menu):
        super().__init__((menu.assets["player"]["idle"][0].get_width()//2, H_HEIGHT), menu.assets["player"], "idle", [menu.sprites], menu.level, True)
        self.hitbox = self.rect.inflate(-self.rect.w//2.5,-65*SCALE)
        self.menu = menu
        self.orientation = "right"
        self.direction = vec()
        self.collidable = [self.menu.static_menu_rect, self.menu.cc_art_rect, self.menu.cc_music_rect]
        self.display_surface = get_window()

        self.helper_font = main_font(16)
        self.helper_keys_txt = self.helper_font.render(f"WASD/Arrows to move", False, "white")
        self.helper_bomb_txt = self.helper_font.render(f"Touch the bombs", False, "white")
        self.helper_keys_rect = self.helper_keys_txt.get_rect()
        self.helper_bomb_rect = self.helper_bomb_txt.get_rect()
        self.need_help = True

        self.normal_animations = self.animations.copy()
        self.flipped_animations = {status:[pygame.transform.flip(img, True, False) for img in frames] for status, frames in self.animations.items()}

    def movement(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.orientation = "right"
            self.animations = self.normal_animations
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.orientation = "left"
            self.animations = self.flipped_animations
        else: self.direction.x = 0

        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.direction.y = 1
        elif keys[pygame.K_w] or keys[pygame.K_UP]: self.direction.y = -1
        else: self.direction.y = 0

        if self.direction.length() != 0:
            self.direction.normalize_ip()
            self.set_status("swim")
            self.need_help = False
        else: self.set_status("idle")

        self.pos.x += self.direction.x*MENU_PLAYER_SPEED*dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx
        self.collider_collisions("h")

        self.pos.y += self.direction.y*MENU_PLAYER_SPEED*dt
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery = self.rect.centery
        self.collider_collisions("v")

    def window_collisions(self):
        if self.hitbox.left < 0:
            self.hitbox.left = 0
            self.rect.centerx = self.hitbox.centerx 
            self.pos.x = self.rect.centerx
        if self.hitbox.right > WIDTH:
            self.hitbox.right = WIDTH
            self.rect.centerx = self.hitbox.centerx 
            self.pos.x = self.rect.centerx

        if self.hitbox.top < 0:
            self.hitbox.top = 0
            self.rect.centery = self.hitbox.centery
            self.pos.y = self.rect.centery
        if self.hitbox.bottom > HEIGHT:
            self.hitbox.bottom = HEIGHT
            self.rect.centery = self.hitbox.centery
            self.pos.y = self.rect.centery

    def collider_collisions(self, direction):
        for collider in self.collidable:
            if collider.colliderect(self.hitbox):
                if direction == "h":
                    self.hitbox.right = collider.left if self.direction.x > 0 else self.hitbox.right
                    self.hitbox.left = collider.right if self.direction.x < 0 else self.hitbox.left
                    self.rect.centerx, self.pos.x = self.hitbox.centerx, self.hitbox.centerx
                    self.direction.x = 0
                else:
                    self.hitbox.top = collider.bottom if self.direction.y < 0 else self.hitbox.top
                    self.hitbox.bottom = collider.top if self.direction.y > 0 else self.hitbox.bottom
                    self.rect.centery, self.pos.y = self.hitbox.centery, self.hitbox.centery
                    self.direction.y = 0

    def mine_collisions(self):
        for mine in self.menu.mines:
            if rect_circle(self.hitbox, mine.rect.center, mine.radius):
                mine.collided()

    def helpers(self):
        if not self.need_help: return
        self.helper_bomb_rect.midbottom = self.rect.midtop
        self.helper_keys_rect.midbottom = self.helper_bomb_rect.midtop

    def draw_helpers(self):
        if not self.need_help: return
        self.display_surface.blit(self.helper_keys_txt, self.helper_keys_rect)
        self.display_surface.blit(self.helper_bomb_txt, self.helper_bomb_rect)

    def update(self, dt):
        self.animate(dt)
        self.movement(dt)
        self.helpers()

        self.window_collisions()
        self.mine_collisions()
        
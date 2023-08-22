from settings import *
from support import get_window, os_range_ui, math, chance
from level.sprites import FxParticle, Chain, Generic

class MenuChain(Generic):
    def __init__(self, topleft, img, level, oscillate_speed, groups, oscillate_offset):
        super().__init__(topleft, img, groups, level, False)
        self.add_oscillator(oscillate_speed=oscillate_speed, oscillate_offset=oscillate_offset)

    def update(self, dt):
        self.oscillator.oscillate()

class MineButton(pygame.sprite.Sprite):
    def __init__(self, menu, pos, size, scale, text_img, on_particle_end):
        super().__init__([menu.sprites, menu.mines])
        self.menu = menu
        surf = pygame.transform.scale_by(menu.assets["enemies"]["mine"][size], scale)
        text_rect = text_img.get_rect(center=(surf.get_width()//2, surf.get_height()//2))
        surf.blit(text_img, text_rect)
        self.on_particle_end = on_particle_end
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.start_y = self.rect.y
        self.o_offset = 12
        self.o_speed = os_range_ui()
        self.pos_y = self.start_y
        self.radius = self.rect.w//2
        chainimg = self.menu.assets["level"]["chain"]
        self.chain = MenuChain((self.rect.centerx-chainimg.get_width()//2, self.rect.centery-self.radius//2), chainimg, self.menu.level, self.o_speed, [menu.sprites], self.o_offset)
        menu.sprites.remove(self)
        menu.sprites.add(self)

    def update(self, dt):
        self.pos_y = self.start_y+ math.sin(pygame.time.get_ticks()*self.o_speed)*self.o_offset
        self.rect.centery = round(self.pos_y)

    def collided(self):
        p = FxParticle(self.rect.center, self.menu.level, "explosion", 2.5, "big", [self.menu.sprites])
        p.on_end_func = self.on_particle_end
        self.menu.main.audio.play_fx("explosion")
        self.chain.kill()
        self.kill()

class ButtonIT:
    def __init__(self, image, text_img, topleft=None, center=None, topright=None, midtop=None, midleft=None, midright=None, text_offset=(0,0)):
        self.display_surface = get_window()
        self.image = image
        self.text_img = text_img
        self.hitbox = self.image.get_rect()
        if topleft: self.hitbox.topleft = topleft
        if topright: self.hitbox.topright = topright
        if center: self.hitbox.center = center
        if midtop: self.hitbox.midtop = midtop
        if midleft: self.hitbox.midleft = midleft
        if midright: self.hitbox.midright = midright
        self.text_rect = self.text_img.get_rect(center=(self.hitbox.centerx+text_offset[0], self.hitbox.centery+text_offset[1]))
        self.logic = ButtonLogic()
        self.text_offset = text_offset

        self.hover_image = self.image.copy()
        white_surf = pygame.Surface(self.image.get_size())
        white_surf.fill((30,30,30))
        self.hover_image.blit(white_surf,(0,0),special_flags=pygame.BLEND_RGB_ADD)

    def check(self, audio, btn=0):
        action= self.logic.check(self.hitbox, btn)
        if action and audio: audio.play_fx("explosion")
        return action
    
    def draw(self):
        self.display_surface.blit(self.image, self.hitbox) if not self.logic.hovering else \
            self.display_surface.blit(self.hover_image, self.hitbox)
        self.display_surface.blit(self.text_img, self.text_rect)

class ButtonOscillating(ButtonIT):
    def __init__(self, image, text_img, topleft=None, center=None, topright=None, midtop=None, midleft=None, midright=None, o_offset=12, o_range=None, text_offset=(0,0)):
        super().__init__(image, text_img, topleft, center, topright, midtop, midleft, midright, text_offset)

        self.o_offset = o_offset
        self.o_speed = os_range_ui() if not o_range else uniform(o_range[0], o_range[1])
        self.hitbox.centery += o_offset
        self.pos_y = float(self.hitbox.centery)
        self.start_y = self.hitbox.centery

    def check(self, audio=None, btn=0):
        self.pos_y = self.start_y + math.sin(pygame.time.get_ticks()*self.o_speed)*self.o_offset
        self.hitbox.centery = round(self.pos_y)
        self.text_rect.centery = self.hitbox.centery+self.text_offset[1]
        action= self.logic.check(self.hitbox, btn)
        if action and audio: audio.play_fx("explosion")
        return action

class ButtonLogic:
    def __init__(self):
        self.clicked = False
        self.hovering = False
        self.can = True

    def check(self, hitbox, btn=0):
        action = False
        self.hovering = self.can and hitbox.collidepoint(pygame.mouse.get_pos())
        if pygame.mouse.get_pressed()[btn]:
            if self.hovering and not self.clicked:
                self.clicked = True
                action = True
        else:
            self.clicked = False
        return action
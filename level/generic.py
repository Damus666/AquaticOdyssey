from settings import *
from support import math

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, level, pos_center=False):
        super().__init__([level.all]+groups)
        self.level = level
        self.image = surf
        if pos_center: self.rect:pygame.Rect = self.image.get_rect(center=pos)
        else: self.rect:pygame.Rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.collision_type = "rect"
        self.collided = False
        self.pos = vec(self.rect.center)
        self.is_player = False

    def add_mover(self, speed=1):
        self.mover = Mover(self, speed)

    def add_oscillator(self,  oscillate_range=OS_RANGE, oscillate_speed=None, use_center=True, oscillate_offset=20):
        self.oscillator = Oscillator(self, oscillate_range, oscillate_speed, use_center, oscillate_offset)

class Mover:
    def __init__(self, parent, speed=1):
        self.parent = parent
        self.speed = speed

    def move(self, dt):
        self.parent.pos.x -= self.parent.level.speed*dt*self.speed
        self.parent.rect.centerx = round(self.parent.pos.x)
        self.parent.hitbox.centerx = self.parent.rect.centerx
        if self.parent.rect.right < 0: self.parent.kill()

class Oscillator:
    def __init__(self, parent, oscillate_range=OS_RANGE, oscillate_speed=None, use_center=True, oscillate_offset=20):
        self.parent = parent

        self.oscillate_speed = uniform(oscillate_range[0],oscillate_range[1]) if not oscillate_speed else oscillate_speed
        self.start_y = self.parent.rect.centery
        self.oscillate_offset = oscillate_offset
        self.use_center = use_center

    def oscillate(self):
        self.parent.pos.y = self.start_y + math.sin(pygame.time.get_ticks()*self.oscillate_speed)*self.oscillate_offset
        self.parent.rect.centery = round(self.parent.pos.y)
        if self.use_center: self.parent.hitbox.center = self.parent.rect.center
        else: self.parent.hitbox.midtop = self.parent.rect.midtop
        
class Animated(Generic):
    def __init__(self, pos, frames, groups, level, pos_center=False, speed_mul=1):
        self.frames = frames
        self.frame_index = uniform(0.0,0.5)
        self.animation_speed = ANIMATION_SPEED*speed_mul
        self.on_end_func = None
        self.can_animate = True
        super().__init__(pos,self.frames[int(self.frame_index)],groups,level,pos_center)
    
    def animate(self, dt):
        old_frame = int(self.frame_index)
        self.frame_index += self.animation_speed*dt
        if self.frame_index >= len(self.frames):
            if not self.on_end_func:
                self.frame_index = 0
            else:
                self.can_animate = False
                self.frame_index = 0
                self.on_end_func()
        if old_frame != int(self.frame_index) and self.can_animate:
            self.image = self.frames[int(self.frame_index)]
            self.rect = self.image.get_rect(center=self.rect.center)
    
    def update(self, dt): self.animate(dt)
        
class AnimatedStatus(Animated):
    def __init__(self, pos, animations, status, groups,level, pos_center=False, speed_mul=1):
        self.animations = animations
        self.status = status
        super().__init__(pos,self.animations[self.status],groups,level,pos_center,speed_mul)
    
    def set_status(self,status,force=False):
        self.frames = self.animations[self.status]
        if self.status != status or force:
            self.status = status
            self.frames = self.animations[self.status]
            if self.frame_index >= len(self.frames): self.frame_index = len(self.frames)-1
            self.image = self.frames[int(self.frame_index)]

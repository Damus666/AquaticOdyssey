from settings import *
from level.generic import Animated, Generic
from support import chance, prop_attr

class Bubble(Generic):
    def __init__(self, pos, img, level):
        super().__init__(pos, img, [level.updates, level.visible], level, True)
        self.y_speed = randint(100,200)
        self.x_speed = randint(10,30)
        self.add_mover()

    def update(self, dt):
        self.pos.x += self.x_speed*dt
        self.mover.move(dt)
        self.pos.y -= self.y_speed*dt
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery = self.rect.centery
        if self.rect.bottom <= 0: self.kill()

class Powerup(Generic):
    def __init__(self, pos, p_type, level):
        data = POWERUP_TYPES[p_type]
        surf = pygame.transform.scale_by(level.assets["ui"][data[0]], data[1])
        super().__init__(pos, surf, [level.visible,level.updates,level.powerups], level, True)
        self.p_type = p_type
        self.add_mover()
        self.add_oscillator()

    def update(self, dt):
        self.mover.move(dt)
        self.oscillator.oscillate()

class Fish(Animated):
    def __init__(self, pos, f_type, level, speed):
        super().__init__(pos, level.assets["enemies"][f_type], [level.updates, level.visible, level.fishes], level)
        self.f_type = f_type
        self.hitbox = self.hitbox.inflate(0,-self.rect.h//4)
        self.add_mover(speed)
        self.add_oscillator()

    def update(self, dt):
        self.animate(dt)
        self.mover.move(dt)
        self.oscillator.oscillate()

class BombFish(Fish):
    def __init__(self, pos, level, speed):
        super().__init__(pos, "fish-big", level, speed)

    def update(self, dt):
        self.mover.move(dt)
        self.oscillator.oscillate()
        self.animate(dt)
        if self.rect.left < self.level.player.hitbox.right:
            FxParticleMoving(self.pos, self.level, "explosion", 1, "big")
            Collider(self.pos, (80*SCALE, 80*SCALE), self.level, "circle")
            self.level.audio.play_fx("explosion")
            self.kill()

class Collider(Generic):
    def __init__(self, pos, size, level, collision_type="rect"):
        super().__init__(pos, pygame.Surface(size), [level.updates, level.collidable], level, True)
        self.collision_type = collision_type
        self.add_mover()

    def update(self, dt): self.mover.move(dt)

class Warning(Generic):
    def __init__(self, pos, surf, groups, level, start_fade_cooldown=500, fade_speed=300):
        super().__init__(pos, surf, groups, level, True)
        self.image = self.image.copy()
        self.start_fade_cooldown = start_fade_cooldown
        self.fading = False
        self.born_time = pygame.time.get_ticks()
        self.fade_speed = fade_speed
        self.alpha = 255

    def update(self, dt):
        if not self.fading:
            if pygame.time.get_ticks()-self.born_time >= self.start_fade_cooldown: self.fading = True
        else:
            self.alpha -= self.fade_speed*dt
            if self.alpha <= 0:
                self.alpha = 0
                self.kill()
            self.image.set_alpha(int(self.alpha))

class InfoMsg(Warning):
    def __init__(self, pos, text, color, font, groups, level):
        super().__init__(pos, font.render(text,False,color), groups, level, 800,400)
        self.pos = vec(self.rect.center)
        self.speed = 1

    def move(self, dt):
        self.pos.x -= self.level.speed*dt*self.speed
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx
        if self.rect.right < 0: self.kill()

    def update(self, dt): self.move(dt)

class Mine(Generic):
    def __init__(self, pos, level, size):
        speed = uniform(*MINE_SPEED)
        super().__init__(pos, level.assets["enemies"]["mine"][size], [level.updates,level.visible_top,level.mines],level,True)
        self.size = size
        self.has_chain = False
        self.radius = self.image.get_width()//2-self.image.get_width()//4
        self.rotate_speed = randint(*MINE_ROTATE_SPEED)
        self.angle = 0
        self.original_img = self.image
        self.add_oscillator()

        if chance("first-chain"):
            self.has_chain = True
            speed = 1
            chain_img = level.assets["level"]["chain"]
            chain1 = Chain((self.rect.centerx-chain_img.get_width()//2,self.rect.centery+self.image.get_height()//4),
                                     chain_img,level,self.oscillator.oscillate_speed)
            if chance("second-chain"):
                Chain((self.rect.centerx-chain_img.get_width()//2,chain1.rect.bottom),chain_img, level,self.oscillator.oscillate_speed)
                
        self.add_mover(speed)
        
    def rotate(self, dt):
        self.angle += self.rotate_speed*dt
        self.image = pygame.transform.rotate(self.original_img, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, dt):
        self.mover.move(dt)
        self.oscillator.oscillate()
        if not self.has_chain: self.rotate(dt)

class Chain(Generic):
    def __init__(self, topleft, img, level, oscillate_speed, groups=None):
        super().__init__(topleft, img, [level.updates, level.visible_top] if groups is None else groups, level, False)
        self.add_mover()
        self.add_oscillator(oscillate_speed=oscillate_speed)

    def update(self, dt):
        self.mover.move(dt)
        self.oscillator.oscillate()

class FxParticle(Animated):
    def __init__(self, pos, level, fx_type, speed_mul=1, sub_fx=None, groups = None):
        super().__init__(pos, level.assets["fx"][fx_type] if not sub_fx else level.assets["fx"][fx_type][sub_fx] ,[level.visible_top,level.updates] if groups is None else groups,level,True,speed_mul)
        self.on_end_func = self.on_end
        self.fx_type = fx_type

    def on_end(self):
        self.kill()

class FxParticleMoving(FxParticle):
    def __init__(self, pos, level, fx_type, speed_mul=1, sub_fx=None):
        super().__init__(pos, level, fx_type, speed_mul, sub_fx)
        self.pos = vec(pos)
        self.add_mover()

    def update(self, dt):
        self.animate(dt)
        self.mover.move(dt)

class Prop(Generic):
    def __init__(self, level, p_type, direction, x):
        surf = level.assets["level"]["props"][p_type]
        # scale
        if "arc" not in p_type: surf = pygame.transform.scale_by(surf, uniform(*prop_attr("scale")))
        else: surf = pygame.transform.scale_by(surf, uniform(*prop_attr("arc-scale")))
        # flip y
        if direction == "top": surf = pygame.transform.flip(surf, False, True)
        # pos
        if "arc" in p_type or "spike" in p_type: pos = (x, 0 if direction == "top" else HEIGHT-surf.get_height())
        else: pos = (x, TOP_H//1.5 if direction == "top" else HEIGHT-BOTTOM_H//1.5-surf.get_height())
        # shade
        speed = 1
        if "totem" in p_type or "temple" in p_type: speed = prop_attr("parallax-speed")
        # flip x
        if "temple" in p_type:
            if chance("temple-flip"): surf = pygame.transform.flip(surf, True, False)
        # groups
        groups = [level.visible_behind, level.updates]
        if "spike" in p_type or "arc" in p_type: groups = [level.visible_behind, level.updates,level.collidable]
        super().__init__(pos, surf, groups, level, False)
        self.p_type = p_type
        self.has_bubble = "totem" in p_type or "coral" in p_type or "algee" in p_type
        self.last_bubble = pygame.time.get_ticks()
        self.bubble_cooldown = randint(*prop_attr("bubble-cooldown"))
        self.hitbox = self.hitbox.inflate(-self.hitbox.w//4,-self.hitbox.h//4)
        self.add_mover(speed)

    def update(self, dt):
        self.mover.move(dt)
        if self.has_bubble and pygame.time.get_ticks()-self.last_bubble >= self.bubble_cooldown:
            self.last_bubble = pygame.time.get_ticks()
            FxParticleMoving(self.rect.center,self.level,"bubbles",1)
            self.has_bubble = False

class Island(Generic):
    def __init__(self, level, scale, y):
        surf = pygame.transform.scale_by(level.assets["level"]["tiles"]["island"], scale)
        super().__init__((WIDTH, y), surf, [level.visible, level.updates, level.islands], level, False)
        self.hitbox = self.rect.inflate(-self.rect.w//4,-self.rect.h//2-self.rect.h//8)
        self.add_mover()
        self.add_oscillator(use_center=False)

    def update(self, dt):
        self.mover.move(dt)
        self.oscillator.oscillate()

class BallIsland(Generic):
    def __init__(self, level, scale, y):
        tiles = level.assets["level"]["tiles"]
        surf = pygame.transform.scale_by(choice([tiles["ball1"],tiles["ball2"]]), scale)
        super().__init__((WIDTH, y), surf, [level.visible_top, level.updates, level.collidable], level, False)
        self.collision_type = "circle"
        self.radius = self.rect.w//2-self.rect.w//8
        self.add_mover()

    def update(self, dt): self.mover.move(dt)

class Tile(Generic):
    def __init__(self, level, ttype, x, long=False):
        tiles = level.assets["level"]["tiles"]
        if ttype == "top":
            surf = choice([tiles["top1"],tiles["top2"]]) if not long else tiles["long"]
            y = 0
        elif ttype == "bottom":
            surf = choice([tiles["bottom1"],tiles["bottom2"]]) if not long else tiles["long"]
            y = HEIGHT-surf.get_height()
        visible_group = level.visible_tiles if not long else level.visible_top
        if long and ttype == "top": surf = pygame.transform.flip(surf, True, True)
        super().__init__((x, y), surf, [visible_group, level.updates], level, False)
        self.image = pygame.transform.scale(self.image, (self.image.get_width()+2,self.image.get_height()))
        self.add_mover()

    def update(self, dt): self.mover.move(dt)

class AngledTile(Generic):
    def __init__(self, level, direction, side, x):
        tiles = level.assets["level"]["tiles"]
        surf = tiles["angled-l"] if side == "left" else tiles["angled-r"]
        if direction == "top": surf = pygame.transform.flip(surf, False, True)
        pos = (x, 0 if direction == "top" else HEIGHT-surf.get_height())
        super().__init__(pos, surf, [level.visible_top, level.updates], level, False)
        self.add_mover()

    def update(self, dt): self.mover.move(dt)
    
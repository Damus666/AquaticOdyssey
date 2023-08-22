from settings import *
from level.generic import AnimatedStatus
from level.sprites import FxParticle, FxParticleMoving, InfoMsg
from support import lerp, rect_circle, main_font, menu_inventory

class Player(AnimatedStatus):
    def __init__(self, level):
        super().__init__((0,H_HEIGHT),level.assets["player"],"swim",[level.visible_top, level.updates], level, True)
        self.hitbox = self.rect.inflate(-self.rect.w//2.5,-65*SCALE)
        self.msg_font = main_font(30)
        self.is_player = True
        self.audio = self.level.audio

        self.pos = vec(self.rect.center)
        self.speed = self.action_dir = 0
        self.dead = False
        self.lives = 1
        self.score = self.high_score= 0
        self.coins = 0
        self.delta_x = 0
        self.new_high_score = False
        self.powerups = {}

        self.last_bubble = 0
        self.bubble_cooldown = 3000
        self.bubble = None

    def post_menu(self):
        self.menu = self.level.main.menu
        self.lives = menu_inventory(self.menu, "extra-life")

    def reset(self):
        self.bubble = None
        self.last_bubble = 0
        self.lives = menu_inventory(self.menu, "extra-life")
        self.score = self.delta_x = 0
        self.speed = self.action_dir = 0
        self.new_high_score = False
        self.rect.center = (0,H_HEIGHT)
        self.pos = vec(self.rect.center)
        self.hitbox = self.rect.inflate(-self.rect.w//2.5,-65*SCALE)
        self.dead = False

    def add_powerup(self, name):
        if name == "extra-life":
            self.lives +=1
            return
        if not name in self.powerups: self.powerups[name] = {"born":pygame.time.get_ticks(),
                                                             "lifetime":menu_inventory(self.menu, f"{name}-lifetime")}
        else: self.powerups[name]["born"] = pygame.time.get_ticks()

    def pack_completed(self):
        self.coins += 10
        self.audio.play_fx("coin-bonus")
        InfoMsg(self.hitbox.topright, f"Perfect! +10", "gold", self.msg_font, [self.level.visible_top, self.level.updates], self.level)
    
    # DEATH
    def die(self, particles=True):
        if not self.on_end_func:
            self.set_status("hurt")
            self.frame_index = 0
            self.on_end_func = self.finish_death
            if particles: FxParticle(self.rect.center, self.level, "enemy-death", 1)
            self.lives -= 1

    def finish_death(self):
        if self.lives <= 0:
            self.lives = 0
            self.dead = True
            self.level.died()
        else:
            self.on_end_func = None
            self.can_animate = True

    # UPDATE
    def update_bubble(self):
        if pygame.time.get_ticks()-self.last_bubble >= self.bubble_cooldown:
            self.last_bubble = pygame.time.get_ticks()
            self.bubble = FxParticle((self.rect.right-self.rect.w//4,self.hitbox.top),self.level,"bubbles", 1.2)
            self.audio.play_fx_single("bubbles-short")
        if self.bubble:
            self.bubble.rect.midbottom = (self.rect.right-self.rect.w//4,self.hitbox.top)

    def update_score(self, dt):
        self.delta_x += self.level.speed*dt
        if self.delta_x >= SCORE_INCREASE:
            self.score += 1
            self.delta_x = 0
        if self.score > self.high_score:
            self.high_score = self.score
            self.new_high_score = True

    def update_powerups(self):
        for name,powerup in list(self.powerups.items()):
            if pygame.time.get_ticks()-powerup["born"] >= powerup["lifetime"]:
                del self.powerups[name]

    def update(self, dt):
        if self.dead: pass

        self.animate(dt)
        self.input()
        self.move(dt)
        self.update_bubble()
        self.update_score(dt)
        self.update_powerups()

        self.tile_collisions()
        self.island_collisions()
        self.fish_collisions()
        self.collidable_collisions()
        self.mine_collisions()
        self.powerups_collisions()
        self.coin_collisions()

    # RUNTIME
    def input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        self.action_dir = 0
        if keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE] or mouse[0]: self.action_dir = -SWIM_ACCELLERATION
        if keys[pygame.K_s] or keys[pygame.K_DOWN] or keys[pygame.K_LSHIFT] or mouse[2]: self.action_dir = SWIM_ACCELLERATION

    def move(self, dt):
        status = "fast"
        action_dir = self.action_dir if not "energy" in self.powerups else self.action_dir*4
        deceleration_mul = DECELERATION_MUL if not "energy" in self.powerups else DECELERATION_MUL*3
        autodive_speed = AUTODIVE_SPEED if not "energy" in self.powerups else AUTODIVE_SPEED*0.2
        if self.action_dir != 0:
            self.speed += action_dir*dt
            self.speed = min(SWIM_MAX_SPEED, self.speed)
            status = "fast"
        else:
            self.speed = lerp(self.speed, autodive_speed, dt*deceleration_mul)
            if self.speed >= autodive_speed-10: status = "swim"
        if self.dead or self.on_end_func: status = "hurt"
        self.set_status(status)

        self.rect.left = PLAYER_LEFT_OFFSET
        self.hitbox.centerx = self.rect.centerx
        self.pos.x = self.rect.centerx

        self.pos.y += self.speed*dt
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery = self.rect.centery

    # COLLISIONS
    def tile_collisions(self):
        if self.hitbox.top < TOP_H:
            self.hitbox.top = TOP_H+1
            self.rect.centery = self.hitbox.centery
            self.pos.y = self.rect.centery
            self.speed = 0
        if self.hitbox.bottom > HEIGHT-BOTTOM_H:
            self.hitbox.bottom = HEIGHT-BOTTOM_H-1
            self.rect.centery = self.hitbox.centery
            self.pos.y = self.rect.centery
            self.speed = 0

    def island_collisions(self):
        for island in self.level.islands:
            if island.hitbox.colliderect(self.hitbox):
                if self.hitbox.bottom > island.hitbox.top and self.hitbox.centery < island.hitbox.top:
                    self.hitbox.bottom = island.hitbox.top
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.rect.centery
                elif not island.collided:
                    island.collided = True
                    self.audio.play_fx("impact")
                    self.die()

    def fish_collisions(self):
        for fish in self.level.fishes:
            if fish.hitbox.colliderect(self.hitbox):
                self.audio.play_fx("impact")
                FxParticleMoving(fish.pos, self.level, "enemy-death")
                fish.kill()
                self.die()

    def collidable_collisions(self):
        for collidable in self.level.collidable:
            if collidable.collision_type == "rect":
                if not collidable.collided and collidable.hitbox.colliderect(self.hitbox):
                    collidable.collided = True
                    self.audio.play_fx("impact")
                    self.die()
            else:
                if not collidable.collided and rect_circle(self.hitbox, collidable.hitbox.center, collidable.radius):
                    collidable.collided = True
                    self.audio.play_fx("impact")
                    self.die()

    def mine_collisions(self):
        for mine in self.level.mines:
            if rect_circle(self.hitbox, mine.pos, mine.radius):
                FxParticleMoving(mine.pos, self.level, "explosion", 2.5, mine.size)
                self.die(False)
                mine.kill()
                self.audio.play_fx("explosion")
    
    def powerups_collisions(self):
        for powerup in self.level.powerups:
            if powerup.hitbox.colliderect(self.hitbox):
                self.add_powerup(powerup.p_type)
                powerup.kill()
                self.audio.play_fx("powerup")
                FxParticleMoving(powerup.pos,self.level, "coin-particle", 1)

    def coin_collisions(self):
        for coin in self.level.coins:
            magnet_mul = menu_inventory(self.menu, "magnet-power")
            hitbox = self.hitbox if not "magnet" in self.powerups else self.hitbox.inflate(self.hitbox.w*magnet_mul,self.hitbox.h*magnet_mul)
            if coin.hitbox.colliderect(hitbox):
                self.coins += 1
                coin.collected()
                coin.kill()
                self.audio.stop_fx("coin-collect")
                self.audio.play_fx("coin-collect")
                FxParticleMoving(coin.pos,self.level, "coin-particle", 1)
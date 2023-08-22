from settings import *
from support import get_window, next_time, bg_attr

class LightEffect:
    def __init__(self, bg, offset, angle_range, force_x = None, ismenu=False):
        self.bg = bg
        self.speed_mul = uniform(*bg_attr("speed-mul"))
        self.pos_x = WIDTH*1.2+offset if not force_x else force_x
        self.image = self.bg.level.assets["fx"]["light"]
        self.image = pygame.transform.scale_by(self.image, (uniform(*bg_attr("x-scale")), 1))
        self.image = pygame.transform.scale(self.image, (self.image.get_width(), HEIGHT*(bg_attr("y-mul") if not ismenu else bg_attr("y-mul")*2)))
        self.image = pygame.transform.rotate(self.image, randint(*bg_attr("neg-angles")) if angle_range == -1 else randint(*bg_attr("pos-angles")))
        self.image.set_alpha(randint(*bg_attr("alpha")))
        self.rect = self.image.get_rect(topleft = (self.pos_x, 0))
        if ismenu: self.rect.y -= HEIGHT//7

    def update(self, dt):
        self.pos_x -= self.bg.level.speed*dt*self.speed_mul
        self.rect.centerx = round(self.pos_x)
        if self.rect.right < 0: self.bg.lights.remove(self)

    def draw(self):
        self.bg.display_surface.blit(self.image, self.rect)

class BG:
    def __init__(self, level, ismenu=False):
        self.level = level
        self.ismenu = ismenu
        self.display_surface = get_window()
        # surfs
        self.bg_surf = self.level.assets["level"]["bg"]
        self.midbg_surf = pygame.transform.scale(self.level.assets["level"]["mid-bg"], WINDOW_SIZES)
        # sizes
        self.bg_w, self.bg_h = self.bg_surf.get_size()
        self.midbg_w = self.midbg_surf.get_width()
        # amounts
        self.bg_h_amount = (HEIGHT//self.bg_h)+2
        self.bg_w_amount = (WIDTH//self.bg_w)+2
        # pos
        self.bg_x = self.midbg_x = 0
        # lights
        self.lights:list[LightEffect] = []
        self.last_light = 0
        self.next_light_time = next_time("light")

    def init_lights(self):
        for i in range(randint(2,3)):
            x = randint(0,WIDTH)
            angle_range = choice([1,-1])
            for i in range(randint(*bg_attr("spawn-amount"))):
                self.lights.append(LightEffect(self, randint(-50,50), angle_range, x, self.ismenu))

    def empty_lights(self):
        for light in self.lights.copy():
            self.lights.remove(light)
            del light

    def update(self, dt):
        self.bg_x -= self.level.speed*BG_SPEED_MUL*dt
        self.midbg_x -= self.level.speed*MIDBG_SPEED_MUL*dt
        if self.bg_x <= -self.bg_w: self.bg_x = 0
        if self.midbg_x <= -self.midbg_w: self.midbg_x = 0

        #lights
        if pygame.time.get_ticks()-self.last_light >= self.next_light_time:
            self.last_light = pygame.time.get_ticks()
            self.next_light_time = next_time("light")
            angle_range = choice([1,-1])
            for i in range(randint(*bg_attr("spawn-amount"))):
                self.lights.append(LightEffect(self, randint(-50,50), angle_range, ismenu=self.ismenu))

        for light in self.lights.copy(): light.update(dt)

    def draw(self):
        self.display_surface.fill("black")
        
        for w in range(self.bg_w_amount):
            for h in range(self.bg_h_amount):
                x = self.bg_x+w*self.bg_w
                y = h*self.bg_h
                self.display_surface.blit(self.bg_surf,(x,y))

        self.display_surface.blit(self.midbg_surf, (self.midbg_x, 0))
        self.display_surface.blit(self.midbg_surf, (self.midbg_x+self.midbg_w, 0))

    def draw_lights(self):
        for light in self.lights: light.draw()
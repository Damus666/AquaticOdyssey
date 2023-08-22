from settings import *
import math, os, sys
from spritesheet import SingleSpritesheet

# resources
def main_font(size, scale=BG_SCALE):
    return pygame.font.Font("assets/fonts/main.ttf",int(size*scale))

def load_audio(name, volume=1, ext="mp3"):
    sound = pygame.mixer.Sound(f"assets/audio/fx/{name}.{ext}")
    sound.set_volume(volume)
    return {
        "sound":sound,
        "volume":volume
    }

# math
def angle_to_vec(angle):
    return vec(math.cos(math.radians(angle)),-math.sin(math.radians(angle)))

def weighted_choice(sequence,weights):
    weightssum = sum(weights)
    chosen = randint(0,weightssum)
    cweight = 0; i = 0
    for w in weights:
        if inside_range(chosen,cweight,cweight+w): return sequence[i]
        cweight += w; i += 1
        
def weighted_choice_combined(sequence_and_weights):
    sequence = [s_a_w[0] for s_a_w in sequence_and_weights]
    weights = [saw[1] for saw in sequence_and_weights]
    weightssum = sum(weights)
    chosen = randint(0,weightssum)
    cweight = 0; i = 0
    for w in weights:
        if inside_range(chosen,cweight,cweight+w): return sequence[i]
        cweight += w; i += 1
        
def lerp(start, end, t): return start * (1 - t) + end * t
            
def inside_range(number:float|int,rangeStart:float|int,rangeEnd:float|int)->bool:
    return number >= min(rangeStart,rangeEnd) and number <= max(rangeStart,rangeEnd)

def point_circle(point, center, radius):
    distance = (point - center).length()
    return distance <= radius

def rect_circle(rect, center, radius):
    corners = [rect.topleft, rect.bottomleft, rect.topright, rect.bottomright]
    for corner in corners:
        if point_circle(vec(corner), center, radius): return True
    return False

# utils
def menu_inventory(menu, item_name):
    return MENU_STAGES[item_name]["values"][menu.inventory[item_name]]

def center_menu_chains(assets, w_div, h_div, w_chains=3, h_chains = 1, down_chains=True):
    menu, inner_rect = build_menu(assets, int(WIDTH//w_div), int(HEIGHT//h_div))
    menu_rect = menu.get_rect(center=WINDOW_CENTER)
    inner_rect.center = menu_rect.center
    chain_img = assets["chain"]
    chain_rot = assets["chain-rot"]
    chain_h, offset = chain_img.get_height(), assets["side-t"].get_height()//2
    chain_rects_v = []
    chain_rects_h = []
    last_pos = menu_rect.top+offset
    for _ in range(h_chains):
        chain_rects_v.append(chain_img.get_rect(midbottom= (menu_rect.left+menu_rect.w//4, last_pos)))
        chain_rects_v.append(chain_img.get_rect(midbottom= (menu_rect.right-menu_rect.w//4, last_pos)))
        last_pos -= chain_h
    last_pos = menu_rect.bottom-offset
    if down_chains:
        for _ in range(h_chains):
            chain_rects_v.append(chain_img.get_rect(midtop= (menu_rect.left+menu_rect.w//4, last_pos)))
            chain_rects_v.append(chain_img.get_rect(midtop= (menu_rect.right-menu_rect.w//4, last_pos)))
            last_pos += chain_h
    last_pos = menu_rect.left+offset
    for _ in range(w_chains):
        chain_rects_h.append(chain_rot.get_rect(midright= (last_pos, menu_rect.top+menu_rect.h//4)))
        chain_rects_h.append(chain_rot.get_rect(midbottom= (last_pos, menu_rect.bottom-menu_rect.h//4)))
        last_pos -= chain_h
    last_pos = menu_rect.right-offset
    for _ in range(w_chains):
        chain_rects_h.append(chain_rot.get_rect(midright= (last_pos, menu_rect.top+menu_rect.h//4)))
        chain_rects_h.append(chain_rot.get_rect(midbottom= (last_pos, menu_rect.bottom-menu_rect.h//4)))
        last_pos += chain_h
    return menu, menu_rect, inner_rect, chain_rects_v,chain_rects_h

def build_menu(assets, w, h, w_plus1=True, h_plus1=True):
    w_diff = assets["corner-tl"].get_width()-assets["side-l"].get_width()
    h_diff = assets["corner-tl"].get_height()-assets["side-t"].get_height()

    sides_w = assets["corner-tl"].get_width()*2
    inner_w = max(w-sides_w, assets["side-t"].get_width())
    side_t_amount = inner_w//assets["side-t"].get_width()+(1 if w_plus1 else 0)
    inner_rw = side_t_amount*assets["side-t"].get_width()
    width = sides_w+inner_rw

    sides_h = assets["corner-tl"].get_height()*2
    inner_h = max(h-sides_h, assets["side-l"].get_height())
    side_l_amount = inner_h//assets["side-l"].get_height()+(1 if h_plus1 else 0)
    inner_rh = side_l_amount*assets["side-l"].get_height()
    height = sides_h+inner_rh

    menu_surf = pygame.Surface((width,height), pygame.SRCALPHA)
    menu_surf.fill(0)

    inner_surf = pygame.Surface((inner_rw+w_diff*2,inner_rh+h_diff*2))
    inner_surf.fill(FILL_COLOR)
    menu_surf.blit(inner_surf, (assets["corner-tl"].get_width()-w_diff,assets["corner-tl"].get_height()-h_diff))

    menu_surf.blit(assets["corner-tl"], (w_diff,h_diff))
    menu_surf.blit(assets["corner-bl"], (w_diff,height-assets["corner-bl"].get_height()-h_diff))
    menu_surf.blit(assets["corner-tr"], (width-assets["corner-tr"].get_width()-w_diff,0))
    menu_surf.blit(assets["corner-br"], (width-assets["corner-br"].get_width()-w_diff,height-assets["corner-br"].get_height()-h_diff))
    
    for i in range(side_t_amount):
        menu_surf.blit(assets["side-t"], (assets["corner-tl"].get_width()+i*assets["side-t"].get_width(), 0))
        menu_surf.blit(assets["side-b"], (assets["corner-tl"].get_width()+i*assets["side-b"].get_width(), height-assets["side-b"].get_height()))

    for i in range(side_l_amount):
        menu_surf.blit(assets["side-l"], (0, assets["corner-tl"].get_height()+i*assets["side-l"].get_height()))
        menu_surf.blit(assets["side-r"], (width-assets["side-r"].get_width(), assets["corner-tl"].get_height()+i*assets["side-r"].get_height()))

    return menu_surf, inner_surf.get_rect()


def coin_setup(): return confined_y(), os_range(), []

def coin_amount(name): return randint(*COINS_FORMATIONS[name])

def bg_attr(name): return BG_ATTRS[name]

def prop_attr(name): return PROP_ATTRS[name]

def chance(name): return randint(0,100) <= CHANCES[name]

def chance_g(name): return randint(0,100) >= CHANCES[name]

def confined_y(mult=2, mulb=2): return randint(int(TOP_H*mult), int(HEIGHT-BOTTOM_H*mulb))

def next_time(name:str): return randint(int(SPAWN_TIME_RANGE[name].x), int(SPAWN_TIME_RANGE[name].y))

def next_time_raw(spawn_time_range:vec): return randint(int(spawn_time_range.x), int(spawn_time_range.y))

def rand_offset(offset): return randint(-offset,offset)

def list_remove_cond(iterable, condition):
    toremove = [el for el in iterable if condition(el)]
    for e in toremove: iterable.remove(e)

def quit_all():
    pygame.quit()
    sys.exit()

def get_window():
    return pygame.display.get_surface()

def os_range():
    return uniform(OS_RANGE[0], OS_RANGE[1])

def os_range_ui():
    return uniform(OS_RANGE_UI[0], OS_RANGE_UI[1])

# graphics
def load(path, convert_alpha, scale=1, ext="png"):
    image = pygame.image.load(f"assets/graphics/{path}.{ext}").convert_alpha() \
        if convert_alpha else pygame.image.load(f"assets/graphics/{path}.{ext}").convert()
    if scale != 1: return pygame.transform.scale_by(image, scale)
    return image

def load_list(path, convert_alpha, scale=1, ext="png"):
    images = []
    for _, _, image_names in os.walk(f"assets/graphics/{path}"):
        for image_name in image_names:
            full_path = f"{path}/{image_name.split('.')[0]}"
            image = pygame.image.load(f"assets/graphics/{full_path}.{ext}").convert_alpha() \
                if convert_alpha else pygame.image.load(f"assets/graphics/{full_path}.{ext}").convert()
            if scale != 1: image = pygame.transform.scale_by(image, scale)
            images.append(image)
        break
    return images

def load_dict(path, convert_alpha, scale=1, ext="png"):
    images = {}
    for _, _, image_names in os.walk(f"assets/graphics/{path}"):
        for image_name in image_names:
            dict_name = image_name.split(".")[0]
            full_path = f"{path}/{dict_name}"
            image = pygame.image.load(f"assets/graphics/{full_path}.{ext}").convert_alpha() \
                if convert_alpha else pygame.image.load(f"assets/graphics/{full_path}.{ext}").convert()
            if scale != 1: image = pygame.transform.scale_by(image, scale)
            images[dict_name] = image
        break
    return images

def empty_surf(sizes, color, flags=0):
    surf = pygame.Surface(sizes,flags)
    surf.fill(color)
    return surf

def only_sprites_from_tuple(sprites): return {name:sprite for name, (sprite,_) in sprites.items()}

def radial_image(surface:pygame.Surface, erase_angle):
    erase_angle -= 180
    surface = surface.copy()
    w,h = surface.get_size()
    cx, cy = w//2, h//2
    center = vec(cx,cy)
    for x in range(w):
        for y in range(h):
            if surface.get_at((x,y)).a == 0: continue
            direction = vec(x,y)-center
            if math.degrees(math.atan2(direction.x, -direction.y)) < erase_angle: surface.set_at((x,y), (0,0,0,0))
    return surface

def single_sheet(path, convert_alpha, scale=1, ext="png", w=None, flip=False):
    return [pygame.transform.scale_by(frame, scale) for frame in 
            SingleSpritesheet(pygame.transform.flip(load(path, convert_alpha, 1, ext), flip, False), w).frames()]

# text
def create_outline(
    surface: pygame.Surface,
    radius: int,
    color: pygame.Color | list[int] | tuple[int, ...] = (0, 0, 0, 255),
    rounded: bool = False,
    border_inflate_x: int = 0,
    border_inflate_y: int = 0,
    mask_threshold=127,
    sharpness_passes: int = 4,
) -> pygame.Surface:
    surf_size = surface.get_size()
    backdrop_surf_size = (
        surf_size[0] + radius + border_inflate_x,
        surf_size[1] + radius + border_inflate_y,
    )

    silhouette = pygame.mask.from_surface(surface, threshold=mask_threshold).to_surface(
        setcolor=color, unsetcolor=(0, 0, 0, 0)
    )
    backdrop = pygame.Surface((backdrop_surf_size), pygame.SRCALPHA)
    blit_topleft = (
        backdrop_surf_size[0] / 2 - surf_size[0] / 2,
        backdrop_surf_size[1] / 2 - surf_size[1] / 2,
    )
    backdrop.blit(silhouette, blit_topleft)
    backdrop_blurred = (
        pygame.transform.gaussian_blur(backdrop, radius=radius)
        if rounded
        else pygame.transform.box_blur(backdrop, radius=radius)
    )
    for _ in range(sharpness_passes):
        backdrop_blurred.blit(
            backdrop_blurred, (0, 0), special_flags=pygame.BLEND_RGBA_ADD
        )

    backdrop_blurred.blit(surface, blit_topleft)
    return backdrop_blurred

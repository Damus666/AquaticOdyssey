from settings import *
from support import load, load_list, load_dict, single_sheet

class AssetLoader:
    def __init__(self):
        self.assets = {}
        self.load()

    def load(self):
        self.assets["enemies"] = {
            "fish-big": single_sheet("enemies/fish-big", True, SCALE, flip=True, w=54),
            "fish-dart": single_sheet("enemies/fish-dart", True, SCALE, flip=True, w=39),
            "fish": single_sheet("enemies/fish", True, SCALE, flip=True),
            "mine": {
                "big": load("enemies/mine-big", True, SCALE),
                "small": load("enemies/mine-small", True, SCALE),
                "normal": load("enemies/mine", True, SCALE),
            }
        }
        self.assets["fx"] = {
            "bubbles": single_sheet("fx/bubbles", True, SCALE, w=23),
            "bubble-list": load_list("fx/bubbles", True, SCALE),
            "enemy-death": single_sheet("fx/enemy-death", True, SCALE),
            "coin-particle": load_list("coin/particle",True,BG_SCALE),
            "light": load("fx/light", True, 1),
            "explosion": {
                "big": single_sheet("fx/explosion-big", True, SCALE, w=78),
                "small": single_sheet("fx/explosion-small", True, SCALE, w=44),
                "normal": single_sheet("fx/explosion", True, SCALE, w=60),
            }
        }
        self.assets["player"] = {
            "fast": single_sheet("player/player-fast", True, SCALE),
            "hurt": single_sheet("player/player-hurt", True, SCALE),
            "idle": single_sheet("player/player-idle", True, SCALE),
            "rush": single_sheet("player/player-rush", True, SCALE),
            "swim": single_sheet("player/player-swiming", True, SCALE),
        }
        self.assets["level"] = {
            "bg": load("level/background", False, BG_SCALE),
            "mid-bg": load("level/midground", True, BG_SCALE),
            "props": load_dict("level/props", True, BG_SCALE),
            "tiles": load_dict("level/tiles", True, BG_SCALE),
            "chain": load("level/chain", True, BG_SCALE),
        }
        self.assets["coin"] = load_list("coin/animation",True,BG_SCALE)
        self.assets["ui"] = load_dict("ui", True)
        menu = load_dict("ui/menu", True, BG_SCALE)
        self.assets["shop"] = {
            "plus": pygame.transform.scale(self.assets["ui"]["plus"], (SHOPITEM_IMG_SIZE//2, SHOPITEM_IMG_SIZE//2)),
            "clock": pygame.transform.scale(self.assets["ui"]["clock"], (SHOPITEM_IMG_SIZE//2, SHOPITEM_IMG_SIZE//2)),
            "extra-life": pygame.transform.scale(self.assets["ui"]["heart"], (SHOPITEM_IMG_SIZE, SHOPITEM_IMG_SIZE)),
            "energy-lifetime": pygame.transform.scale(self.assets["ui"]["energy"], (SHOPITEM_IMG_SIZE, SHOPITEM_IMG_SIZE)),
            "magnet-lifetime": (magnet_img:=pygame.transform.scale(self.assets["ui"]["magnet"], (SHOPITEM_IMG_SIZE, SHOPITEM_IMG_SIZE))),
            "magnet-power": magnet_img,
            "chain":menu["chain-shop"]
        }
        self.assets["menu"] = {
            "chain":pygame.transform.scale_by(menu["chain"], 2),
            "chain-rot": pygame.transform.scale_by(pygame.transform.rotate(menu["chain"], 90), 2),
            "island": menu["island"],
            "spike-l": (spike_l:=pygame.transform.rotate(menu["spike"], 45)),
            "spike-r": pygame.transform.flip(spike_l, True, False),
            "corner-tl": menu["corner"],
            "corner-tr": pygame.transform.flip(menu["corner"], True, False),
            "corner-bl": pygame.transform.flip(menu["corner"], False, True),
            "corner-br": pygame.transform.flip(menu["corner"], True, True),
            "side-l": menu["side"],
            "side-r": pygame.transform.flip(menu["side"], True, False),
            "side-t": (side_t:=pygame.transform.rotate(menu["side"], -90)),
            "side-b": pygame.transform.flip(side_t, False, True),
            "mine-big": self.assets["enemies"]["mine"]["big"],
            "mine-small": self.assets["enemies"]["mine"]["small"],
            "mine-normal": self.assets["enemies"]["mine"]["normal"],
            
        }

    def __getitem__(self, name):
        return self.assets[name]
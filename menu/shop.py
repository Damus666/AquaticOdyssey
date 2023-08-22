from settings import *
from support import center_menu_chains, get_window, main_font
from menu.elements import ButtonOscillating
from menu.shopitem import ShopItem

class Shop:
    def __init__(self, menu):
        self.menu = menu
        self.assets = self.menu.assets
        self.display_surface = get_window()
        self.font = self.menu.font
        self.shop_font = main_font(24)
        self.player = self.menu.level.player

        self.menu_img, self.menu_rect, self.inner_rect, self.chain_rects_v, self.chain_rects_h = \
            center_menu_chains(self.assets["menu"], 1.1, 1.1, 2, 2, True,)
        
        self.title_surf = self.menu.title_font.render("Shop", False, "white")
        self.title_rect = self.title_surf.get_rect(midtop=self.inner_rect.midtop)

        self.back_button = ButtonOscillating(self.assets["enemies"]["mine"]["normal"],
                            self.font.render("Back", False, "white"), topleft=self.menu_rect.topleft)
        
        self.coins_img = self.menu.level.ui.coin_img
        self.coins_rect = self.coins_img.get_rect(topright=(self.inner_rect.right,self.inner_rect.top))
        self.refresh_coins()

        self.last_stages = DEFAULT_DATA.copy()
        self.item_w = self.inner_rect.w//2-UI_SPACING//2
        self.items:list[ShopItem] = []
        self.last_upgraded = None
        
    def build_shop(self):
        for i in self.items.copy():
            self.items.remove(i)
            del i
        x = self.inner_rect.x
        y = self.title_rect.bottom+UI_SPACING
        for item_name, stage in self.menu.inventory.items():
            item = ShopItem(self, (x,y), item_name, stage, self.item_w, self.last_stages[item_name] )
            if item_name == self.last_upgraded: item.mine_button.logic.clicked = True
            self.items.append(item)
            if x == self.inner_rect.x: x = self.inner_rect.x+self.item_w+UI_SPACING
            else:
                x = self.inner_rect.x
                y += item.get_height()+UI_SPACING

    def upgrade(self, name, price):
        if self.player.coins >= price:
            self.player.coins -= price
            self.last_stages = self.menu.inventory.copy()
            self.menu.inventory[name] += 1
            self.menu.level.save_data()
            self.menu.save_data()
            self.last_upgraded = name
            self.build_shop()
            self.refresh_coins()
        
    def refresh_coins(self):
        self.coin_txt_surf = self.shop_font.render(f"{self.menu.level.player.coins}", False, "white")
        self.coin_txt_rect = self.coin_txt_surf.get_rect(midright=(self.coins_rect.left-UI_SPACING, self.coins_rect.centery))

    def update(self, dt):
        if self.back_button.check(self.menu.audio):
            self.menu.back_from_shop()
        for item in self.items: item.update(dt)

    def draw(self):
        for chain_rect in self.chain_rects_v: self.display_surface.blit(self.assets["menu"]["chain"], chain_rect)
        for chain_rect in self.chain_rects_h: self.display_surface.blit(self.assets["menu"]["chain-rot"], chain_rect)
        self.display_surface.blit(self.menu_img, self.menu_rect)
        self.display_surface.blit(self.title_surf, self.title_rect)
        self.back_button.draw()
        self.display_surface.blit(self.coins_img, self.coins_rect)
        self.display_surface.blit(self.coin_txt_surf, self.coin_txt_rect)
        for item in self.items: item.draw()
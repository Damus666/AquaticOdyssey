from settings import *
from support import get_window, lerp
from menu.elements import ButtonIT

class ShopItem:
    def __init__(self, shop, topleft, name, stage, width, last_stage):
        self.shop = shop
        self.name = name
        self.stage = stage
        self.last_stage = last_stage
        self.should_lerp = self.stage != self.last_stage
        self.price = MENU_STAGES[name]["price"]*(self.stage+1)
        self.width = width
        self.display_surface = get_window()
        self.max_stage = len(MENU_STAGES[name]["values"])-1
        self.can_upgrade = self.stage < self.max_stage
        self.can_buy = self.shop.player.coins >= self.price
    
        self.mine_img = pygame.transform.scale(shop.assets["enemies"]["mine"]["big"], (SHOPITEM_MINE_SIZE, SHOPITEM_MINE_SIZE))
        self.mine_button = ButtonIT(self.mine_img, pygame.Surface((1,1)), topleft)
        if not self.can_upgrade or not self.can_buy: self.mine_button.logic.can = False
        self.icon = shop.assets["shop"][name]
        self.secondary_icon = shop.assets["shop"]["clock"] if "lifetime" in name else shop.assets["shop"]["plus"]
        self.icon_rect = self.icon.get_rect(center=self.mine_button.hitbox.center)
        self.secondary_rect = self.secondary_icon.get_rect(topleft=self.mine_button.hitbox.center)

        self.chain_original = self.shop.assets["shop"]["chain"]
        old_w, old_h = self.chain_original.get_size()
        new_w = width-(self.icon_rect.w+((self.mine_button.hitbox.w-self.icon_rect.w)//2))
        new_h = old_h*(new_w/old_w)
        self.chain_img = pygame.transform.scale(self.chain_original, (new_w, new_h))
        self.chain_rect = self.chain_img.get_rect(midleft = self.icon_rect.topright)

        self.chain_stage = self.chain_original.copy()
        self.original_chain_stage = self.chain_stage
        self.last_colored_w = (self.chain_stage.get_width()*self.last_stage)/self.max_stage
        self.full_colored_w = (self.chain_stage.get_width()*self.stage)/self.max_stage
        self.current_colored_w = self.last_colored_w
        if not self.should_lerp: self.apply_colored_chain()

        self.upgrade_txt_surf = self.shop.shop_font.render("<-Upgrade" if self.can_upgrade else "Max", False, "white")
        self.upgrade_txt_rect = self.upgrade_txt_surf.get_rect(midleft=(self.mine_button.hitbox.right, self.icon_rect.bottom))
        self.coin_rect = self.shop.coins_img.get_rect(midleft=(self.upgrade_txt_rect.right+UI_SPACING, self.upgrade_txt_rect.centery))
        self.price_surf = self.shop.shop_font.render(f"{self.price}", False, "white" if self.can_buy else "red")
        self.price_rect = self.price_surf.get_rect(midleft=(self.coin_rect.right+UI_SPACING, self.coin_rect.centery))

    def apply_colored_chain(self):
        for x in range(self.original_chain_stage.get_width()):
            if x < self.current_colored_w:
                for y in range(self.original_chain_stage.get_height()):
                    if self.original_chain_stage.get_at((x,y)).a > 0:
                        self.original_chain_stage.set_at((x,y), ON_CHAIN_COL)
        self.chain_stage = pygame.transform.scale(self.original_chain_stage, self.chain_img.get_size())

    def get_height(self):
        return self.mine_button.hitbox.height
    
    def update(self, dt):
        if self.mine_button.check(self.shop.menu.audio):
            if self.can_upgrade and self.can_buy: self.shop.upgrade(self.name, self.price)
        if self.should_lerp:
            self.current_colored_w = lerp(self.current_colored_w, self.full_colored_w, SHOP_LERP_SPEED*dt)
            self.apply_colored_chain()
            if self.full_colored_w - self.current_colored_w < 1: self.should_lerp = False

    def draw(self):
        self.display_surface.blit(self.chain_img, self.chain_rect)
        self.display_surface.blit(self.chain_stage, self.chain_rect)
        self.mine_button.draw()
        self.display_surface.blit(self.icon, self.icon_rect)
        self.display_surface.blit(self.secondary_icon, self.secondary_rect)
        self.display_surface.blit(self.upgrade_txt_surf, self.upgrade_txt_rect)
        if self.can_upgrade:
            self.display_surface.blit(self.shop.coins_img, self.coin_rect)
            self.display_surface.blit(self.price_surf, self.price_rect)
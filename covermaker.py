import pygame
from support import main_font, build_menu
from assetloader import AssetLoader

pygame.init()
screen = pygame.display.set_mode((1000,700))
clock = pygame.time.Clock()

assets = AssetLoader()
menu_img, inner_rect = build_menu(assets["menu"], 630, 500)
menu_img = pygame.transform.scale(menu_img, (630,500))
menu_rect = menu_img.get_rect(center=(500,350))
inner_rect.center = menu_rect.center

font = main_font(80)
aquatic = font.render("Aquatic", False, "white")
odyssey = font.render("Odyssey", False, "white")
a_rect = aquatic.get_rect(midbottom=inner_rect.center)
o_rect = odyssey.get_rect(midtop=inner_rect.center)

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            surface = pygame.Surface((1000,700))
            surface.blit(screen, (0, 0))
            surface.set_colorkey("white")
            pygame.image.save(surface, "cover.png")
            
            pygame.quit()

    screen.fill("white")

    screen.blit(menu_img, menu_rect)
    screen.blit(aquatic, a_rect)
    screen.blit(odyssey, o_rect)

    pygame.display.update()
    clock.tick(0)
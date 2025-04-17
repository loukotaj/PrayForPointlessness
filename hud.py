import pygame
from config import WIDTH, WAVES, HUD_FONT_SIZE

def draw_hud(screen, player, central_tower, wave_index):
    font = pygame.font.SysFont(None, HUD_FONT_SIZE)
    wave_label = wave_index+1 if wave_index < len(WAVES) else len(WAVES)
    hud_text = (
        f"Wave: {wave_label}/{len(WAVES)} | "
        f"Player HP: {int(player.health)}/{player.max_health} | "
        f"Money: {int(player.money)} | "
        f"Tower HP: {int(central_tower.health)}/{central_tower.max_health} | "
        f"Press U for Upgrades | Press H for Help"
    )
    surf = font.render(hud_text, True, (255, 255, 255))
    screen.blit(surf, (20, 20))

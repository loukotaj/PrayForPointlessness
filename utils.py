import pygame

def draw_health_bar(surface, x, y, width, height, health, max_health, color_fg=(80,220,80), color_bg=(60,60,60), border_color=(0,0,0), border_width=2):
    health_ratio = max(0, min(1, health / max_health if max_health > 0 else 0))
    pygame.draw.rect(surface, color_bg, (x, y, width, height))
    pygame.draw.rect(surface, color_fg, (x, y, int(width * health_ratio), height))
    if border_width > 0:
        pygame.draw.rect(surface, border_color, (x, y, width, height), border_width)

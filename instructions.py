import pygame
from config import WIDTH, HEIGHT, INSTRUCTIONS_FONT_SIZE, INSTRUCTIONS_OVERLAY_SIZE, INSTRUCTIONS_OVERLAY_ALPHA

def draw_instructions(screen):
    lines = [
        "== CONTROLS ==",
        "WASD: Move",
        "Mouse Click: Shoot",
        "T: Place Tower (cost 50)",
        "U: Open/Close Upgrade Menu (use number keys to buy an upgrade)",
        "H: Toggle this Help Overlay",
        "",
        "== GOAL ==",
        "Defend the Central Tower from waves of enemies!",
        "Survive all waves to achieve victory.",
        "Press SPACE to continue..."
    ]
    font = pygame.font.SysFont(None, INSTRUCTIONS_FONT_SIZE)
    overlay = pygame.Surface(INSTRUCTIONS_OVERLAY_SIZE, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, INSTRUCTIONS_OVERLAY_ALPHA))
    screen.blit(overlay, (WIDTH//2 - INSTRUCTIONS_OVERLAY_SIZE[0]//2, HEIGHT//2 - INSTRUCTIONS_OVERLAY_SIZE[1]//2))
    y_off = HEIGHT//2 - INSTRUCTIONS_OVERLAY_SIZE[1]//2 + 20
    for line in lines:
        ts = font.render(line, True, (255, 255, 255))
        rect = ts.get_rect(center=(WIDTH//2, y_off))
        screen.blit(ts, rect)
        y_off += 35

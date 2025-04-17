import pygame
import sys
from state import GameState
from config import WIDTH, HEIGHT
import asyncio
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    GameState.init(screen)

    running = True
    while running:
        await asyncio.sleep(0)  # You must include this statement in your main loop. Keep the argument at 0.
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                GameState.process_event(event)
        GameState.update()

    pygame.quit()
    sys.exit()

asyncio.run(main())

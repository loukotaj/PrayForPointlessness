import pygame, math
from typing import List
from projectile import Projectile          # <-- existing class
from enemy import BaseEnemy
from utils import draw_health_bar

class Player:
    def __init__(self, x, y,
                 radius=20, speed=5,
                 max_health=50,
                 bullet_damage=8, bullet_speed=9,
                 fire_cooldown=18):
        # -------------------------------------------------- stats / movement
        self.x, self.y   = x, y
        self.radius      = radius
        self.speed       = speed

        self.max_health  = max_health
        self.health      = max_health
        self.money       = 50

        # -------------------------------------------------- shooting
        self.bullet_damage   = bullet_damage
        self.bullet_speed    = bullet_speed
        self.fire_cooldown   = fire_cooldown   # frames between shots
        self.fire_timer      = 0               # counts down to 0

        # -------------------------------------------------- invincibility
        self.iframes_max = 60
        self.iframes     = 0

    # ================================================================ UPDATE
    def update(self, W, H, enemies: List[BaseEnemy], projectiles: List[Projectile]):
        # -------- movement (W A S D) ---------------------------------------
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: self.x -= self.speed
        if keys[pygame.K_d]: self.x += self.speed
        if keys[pygame.K_w]: self.y -= self.speed
        if keys[pygame.K_s]: self.y += self.speed
        self.x = max(self.radius, min(W - self.radius, self.x))
        self.y = max(self.radius, min(H - self.radius, self.y))

        # -------- shoot while LMB pressed ---------------------------------
        if self.fire_timer: self.fire_timer -= 1
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed and self.fire_timer == 0:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - self.x, my - self.y
            dist   = math.hypot(dx, dy)
            if dist:      # create a bullet
                vx, vy = dx / dist, dy / dist
                projectiles.append(
                    Projectile(self.x, self.y, vx, vy,
                               speed=self.bullet_speed,
                               damage=self.bullet_damage,
                               is_friendly=True))
                self.fire_timer = self.fire_cooldown

        # -------- invincibility frames -----------------------------------
        if self.iframes: self.iframes -= 1

    # ================================================================ MISC
    def take_damage(self, dmg):
        if self.iframes: return
        self.health  = max(0, self.health - dmg)
        self.iframes = self.iframes_max

    # ================================================================ DRAW
    def draw(self, surf):
        # flicker while invincible
        flick = self.iframes and (self.iframes // 5) % 2
        col   = (200,200,200) if flick else (255,255,255)
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), self.radius)

        # health bar
        draw_health_bar(surf,
                        self.x - self.radius, self.y - self.radius - 18,
                        self.radius*2, 8,
                        self.health, self.max_health)

        # simple face
        eye_r = max(2, self.radius // 6)
        for dx in (-self.radius//3, self.radius//3):
            pygame.draw.circle(surf, (0,0,0),
                               (int(self.x + dx), int(self.y - self.radius//3)), eye_r)
        pygame.draw.line(surf, (0,0,0),
                         (self.x - self.radius//2, self.y + self.radius//4),
                         (self.x + self.radius//2, self.y + self.radius//4), 2)

import pygame
import math
from typing import List
from projectile import Projectile
from enemy import BaseEnemy
from utils import draw_health_bar
from music_manager import MusicManager

class CentralTower:
    def __init__(self, x, y,
                 max_health=200, radius=40,
                 shot_cooldown=40, shot_speed=5,
                 shot_damage=5, shot_range=300):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_health = max_health
        self.health = max_health

        self.shot_cooldown = shot_cooldown
        self.shot_timer = 0
        self.shot_speed = shot_speed
        self.shot_damage = shot_damage
        self.shot_range = shot_range

        self.firing = False
        self.firing_timer = 0
        self.firing_flash_duration=5

        self.damage_flash_duration=20
        self.damage_flash_timer=0

    def update(self, enemies, projectiles):
        if self.health<=0:
            return
        if self.shot_timer>0:
            self.shot_timer-=1
        if self.firing:
            self.firing_timer-=1
            if self.firing_timer<=0:
                self.firing=False
        if self.damage_flash_timer>0:
            self.damage_flash_timer-=1

        if self.shot_timer<=0:
            tgt=self.find_nearest_enemy(enemies)
            if tgt:
                dx,dy= tgt.x-self.x, tgt.y-self.y
                dist=math.hypot(dx,dy)
                if dist>0:
                    dirx,diry=dx/dist, dy/dist
                    proj= Projectile(self.x,self.y, dirx,diry,
                                     speed=self.shot_speed, damage=self.shot_damage,
                                     is_friendly=True)
                    projectiles.append(proj)
                    self.shot_timer=self.shot_cooldown
                    self.firing=True
                    self.firing_timer=self.firing_flash_duration
                    MusicManager.play_sfx("laser.ogg")

    def find_nearest_enemy(self, enemies):
        best=None
        bd=999999
        for e in enemies:
            if e.health>0:
                dist=math.hypot(e.x-self.x,e.y-self.y)
                if dist<self.shot_range and dist<bd:
                    bd=dist
                    best=e
        return best

    def take_damage(self,dmg):
        self.health-=dmg
        if self.health<0:
            self.health=0
        self.damage_flash_timer=self.damage_flash_duration
        MusicManager.play_sfx("break.ogg")  # <-- play break sound

    def draw(self,surface):
        if self.health<=0: return
        # Draw range indicator
        pygame.draw.circle(
            surface,
            (180,180,180),
            (int(self.x), int(self.y)),
            self.shot_range,
            1
        )
        color=(255,0,0) if self.damage_flash_timer>0 else (100,100,255)
        if self.firing:
            color=(200,200,100)
        pygame.draw.circle(surface,color,(int(self.x),int(self.y)),self.radius)
        # Health bar
        bar_width = self.radius * 2
        bar_height = 10
        bar_x = int(self.x - self.radius)
        bar_y = int(self.y - self.radius - 20)
        draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, self.health, self.max_health)

class PlayerTower:
    def __init__(self, x, y,
                 max_health=80, radius=20,
                 shot_cooldown=40, shot_speed=5,
                 shot_damage=4, shot_range=200):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_health = max_health
        self.health = max_health

        self.shot_cooldown= shot_cooldown
        self.shot_timer=0
        self.shot_speed= shot_speed
        self.shot_damage= shot_damage
        self.shot_range= shot_range

        self.firing=False
        self.firing_timer=0
        self.firing_flash_duration=5

        self.damage_flash_duration=20
        self.damage_flash_timer=0

        self.regen_rate = 0.08  # Health per frame (about 5 per second at 60fps)

    def update(self, enemies, projectiles):
        if self.health<=0:
            return
        # Regenerate health if not at max
        if self.health < self.max_health:
            self.health = min(self.max_health, self.health + self.regen_rate)
        if self.shot_timer>0:
            self.shot_timer-=1
        if self.firing:
            self.firing_timer-=1
            if self.firing_timer<=0:
                self.firing=False
        if self.damage_flash_timer>0:
            self.damage_flash_timer-=1

        if self.shot_timer<=0:
            tgt=self.find_nearest_enemy(enemies)
            if tgt:
                dx,dy= tgt.x-self.x, tgt.y-self.y
                dist=math.hypot(dx,dy)
                if dist>0:
                    dirx,diry=dx/dist,dy/dist
                    proj= Projectile(
                        x=self.x,y=self.y,
                        dx=dirx,dy=diry,
                        speed=self.shot_speed,
                        damage=self.shot_damage,
                        is_friendly=True
                    )
                    projectiles.append(proj)
                    self.shot_timer=self.shot_cooldown
                    self.firing=True
                    self.firing_timer=self.firing_flash_duration
                    MusicManager.play_sfx("laser.ogg")

    def find_nearest_enemy(self,enemies):
        best=None
        bd=999999
        for e in enemies:
            if e.health>0:
                dist=math.hypot(e.x-self.x,e.y-self.y)
                if dist<self.shot_range and dist<bd:
                    bd=dist
                    best=e
        return best

    def take_damage(self, dmg):
        self.health-=dmg
        if self.health<0:
            self.health=0
        self.damage_flash_timer=self.damage_flash_duration

    def draw(self,surface):
        if self.health<=0: return
        # Draw range indicator
        pygame.draw.circle(
            surface,
            (180,180,180),
            (int(self.x), int(self.y)),
            self.shot_range,
            1
        )
        color=(255,0,0) if self.damage_flash_timer>0 else (100,200,100)
        if self.firing:
            color=(200,200,100)
        pygame.draw.circle(surface,color,(int(self.x),int(self.y)),self.radius)
        # Health bar
        bar_width = self.radius * 2
        bar_height = 8
        bar_x = int(self.x - self.radius)
        bar_y = int(self.y - self.radius - 16)
        draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, self.health, self.max_health)

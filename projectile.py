import pygame
import math

class Projectile:
    def __init__(self, x, y, dx, dy,
                 speed=5, damage=5,
                 is_friendly=True,
                 radius=5,
                 color=(255,255,0)):
        self.x=x
        self.y=y
        self.dx=dx
        self.dy=dy
        self.speed=speed
        self.damage=damage
        self.is_friendly=is_friendly
        self.radius=radius
        self.color=color
        self.alive=True

    def update(self,w,h):
        if not self.alive:return
        self.x+=self.dx*self.speed
        self.y+=self.dy*self.speed
        if self.x<0 or self.x>w or self.y<0 or self.y>h:
            self.alive=False

    def draw(self,surface):
        if self.alive:
            pygame.draw.circle(surface,self.color,(int(self.x),int(self.y)),self.radius)

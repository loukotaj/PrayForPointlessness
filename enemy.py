import pygame
import math
import random
from projectile import Projectile
from utils import draw_health_bar
from music_manager import MusicManager

class BaseEnemy:
    def __init__(self, x, y, speed, health, damage, kill_reward,
                 shot_cooldown, shot_speed, shot_range,
                 size, can_shoot=True, melee_range=25, melee_damage=4, melee_cooldown=60):
        self.x = x
        self.y = y
        self.speed = speed
        self.kill_reward = kill_reward
        self.shot_cooldown = shot_cooldown
        self.shot_timer = 0
        self.shot_speed = shot_speed
        self.shot_range = shot_range
        self.size = size
        self.can_shoot = can_shoot
        self.melee_range = melee_range
        self.melee_cooldown = melee_cooldown
        self.melee_timer = 0

        # Scale health and damage by difficulty
        diff = getattr(pygame, "difficulty", 1.0)
        self.max_health = health * diff
        self.health = self.max_health
        self.damage = damage * diff
        self.melee_damage = melee_damage * diff

        # For a hit flash
        self.is_hit = False
        self.hit_flash_duration = 5
        self.hit_timer = 0

        # Extra optional fields for new behaviors
        self.special_timer = 0  # can be used for special movement
        self.special_cooldown = 180  # frames between special actions

    def update(self, player, towers, central_tower, projectiles, all_enemies):
        if self.health <= 0:
            return

        # Possibly do a special action
        self.update_special_behavior()

        # Normal movement
        tx, ty = self.find_nearest_target(player, towers, central_tower)
        if tx is not None and ty is not None:
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.x += (dx/dist)*self.speed
                self.y += (dy/dist)*self.speed

        self.apply_separation(all_enemies)

        # Attack logic
        if self.can_shoot:
            self.handle_ranged_attack(player, towers, central_tower, projectiles)
        else:
            self.handle_melee_attack(player, towers, central_tower)

        # Hit flash
        if self.is_hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.is_hit = False

    def update_special_behavior(self):
        """
        Override in subclasses for specialized movement or actions.
        The base class can also do something generic, if desired.
        """
        pass

    def handle_ranged_attack(self, player, towers, central_tower, projectiles):
        if self.shot_timer > 0:
            self.shot_timer -= 1
        else:
            target, distance = self.find_target_for_projectile(player, towers, central_tower)
            if target is not None:
                dx, dy = (target.x - self.x), (target.y - self.y)
                dist = math.hypot(dx, dy)
                if dist > 0:
                    dirx = dx/dist
                    diry = dy/dist
                    proj = Projectile(
                        x=self.x,
                        y=self.y,
                        dx=dirx,
                        dy=diry,
                        speed=self.shot_speed,
                        damage=self.damage,
                        is_friendly=False
                    )
                    projectiles.append(proj)
                    MusicManager.play_sfx("laser.mp3")
                self.shot_timer = self.shot_cooldown

    def handle_melee_attack(self, player, towers, central_tower):
        if self.melee_timer > 0:
            self.melee_timer -= 1
        else:
            target, distance = self.find_target_for_melee(player, towers, central_tower)
            if target is not None and distance < self.melee_range:
                target.take_damage(self.melee_damage)
                self.melee_timer = self.melee_cooldown

    def find_nearest_target(self, player, towers, central_tower):
        possible = []
        if player.health > 0:
            possible.append((player.x, player.y))
        for t in towers:
            if t.health > 0:
                possible.append((t.x, t.y))
        if central_tower.health > 0:
            possible.append((central_tower.x, central_tower.y))

        if not possible:
            return (None, None)

        nearest = None
        nd = float('inf')
        for (tx, ty) in possible:
            d = math.hypot(tx - self.x, ty - self.y)
            if d < nd:
                nd = d
                nearest = (tx, ty)
        return nearest if nearest else (None, None)

    def find_target_for_projectile(self, player, towers, central_tower):
        best = None
        bd = float('inf')
        # Check player
        if player.health > 0:
            dp = math.hypot(player.x - self.x, player.y - self.y)
            if dp < self.shot_range and dp < bd:
                best = player
                bd = dp
        # Check towers
        for t in towers:
            if t.health > 0:
                dt = math.hypot(t.x - self.x, t.y - self.y)
                if dt < self.shot_range and dt < bd:
                    best = t
                    bd = dt
        # Check central tower
        if central_tower.health > 0:
            dc = math.hypot(central_tower.x - self.x, central_tower.y - self.y)
            if dc < self.shot_range and dc < bd:
                best = central_tower
                bd = dc
        if best is None:
            return (None, None)
        else:
            return (best, bd)

    def find_target_for_melee(self, player, towers, central_tower):
        best = None
        bd = float('inf')
        if player.health > 0:
            dp = math.hypot(player.x - self.x, player.y - self.y)
            if dp < self.melee_range and dp < bd:
                best = player
                bd = dp
        for t in towers:
            if t.health > 0:
                dt = math.hypot(t.x - self.x, t.y - self.y)
                if dt < self.melee_range and dt < bd:
                    best = t
                    bd = dt
        dc = math.hypot(central_tower.x - self.x, central_tower.y - self.y)
        if central_tower.health > 0 and dc < self.melee_range and dc < bd:
            best = central_tower
            bd = dc
        if best is None:
            return (None, None)
        else:
            return (best, bd)

    def apply_separation(self, all_enemies):
        sep_force = 0.5
        for oth in all_enemies:
            if oth is self or oth.health <= 0:
                continue
            dx = self.x - oth.x
            dy = self.y - oth.y
            dist = math.hypot(dx, dy)
            min_d = (self.size + oth.size) / 2
            if dist < min_d and dist > 0:
                push = (min_d - dist) * sep_force
                self.x += (dx/dist)*push
                self.y += (dy/dist)*push

    def take_damage(self, amt):
        self.health -= amt
        if self.health < 0:
            self.health = 0
        self.is_hit = True
        self.hit_timer = self.hit_flash_duration

    def center(self):
        # Returns the center (cx, cy) of the enemy for collision
        return (self.x + self.size / 2, self.y + self.size / 2)

    def draw(self, surface):
        color = (255,255,255) if self.is_hit else (200, 50, 50)
        pygame.draw.rect(surface, color, (self.x, self.y, self.size, self.size))
        # Health bar
        bar_width = self.size
        bar_height = 6
        bar_x = int(self.x)
        bar_y = int(self.y - 12)
        draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, self.health, self.max_health, color_fg=(220,80,80), border_width=1)

# ------------------------------------------------------------------------
# Specialized enemies with advanced or distinct behavior below

def spawn_enemy(shape_type, tier, x, y):
    if shape_type == "triangle":
        return TriangleEnemy(x, y, tier)
    elif shape_type == "square":
        return SquareEnemy(x, y, tier)
    elif shape_type == "star":
        return StarEnemy(x, y, tier)
    elif shape_type == "boss":
        return BossEnemy(x, y, tier)
    else:
        return SquareEnemy(x, y, tier=1)

class TriangleEnemy(BaseEnemy):
    def __init__(self, x, y, tier=1):
        # Tier-based stats
        health = 20 + 10*(tier-1)
        speed = 2 + 0.3*(tier-1)
        damage = 6 + 2*(tier-1)
        kill_reward = 5 + 2*(tier-1)
        shot_cooldown = 999  # effectively never shoots
        shot_speed = 0
        shot_range = 0
        # Make size scale more strongly with tier
        size = 28 + 8*(tier-1)
        # Melee range = 35 + 5*(tier-1)
        super().__init__(
            x, y,
            speed=speed,
            health=health,
            damage=damage,
            kill_reward=kill_reward,
            shot_cooldown=shot_cooldown,
            shot_speed=shot_speed,
            shot_range=shot_range,
            size=size,
            can_shoot=False,
            melee_range=35+5*(tier-1),
            melee_damage=damage,
            melee_cooldown=45
        )
        self.color = (random.randint(180,255), random.randint(50,150), random.randint(50,150))
        self.tier = tier
        # Specialized charge behavior
        self.charge_cooldown = 300 - 20*(tier-1)  # frames between charges
        self.charge_timer = 0
        self.charging = False
        self.charge_duration = 30

    def update_special_behavior(self):
        # Triangle occasionally "charges" in a straight line
        if self.charging:
            # Already in a charge
            self.charge_timer -= 1
            if self.charge_timer <= 0:
                self.charging = False
                self.speed /= 2  # revert speed
        else:
            # not charging
            if self.special_timer>0:
                self.special_timer-=1
            else:
                # begin a charge
                self.charging = True
                self.speed *= 2  # double speed
                self.charge_timer = self.charge_duration
                self.special_timer = self.charge_cooldown

    def draw(self, surface):
        color = (255, 200, 80) if not self.is_hit else (255,255,255)
        points = [
            (self.x + self.size/2, self.y),
            (self.x, self.y + self.size),
            (self.x + self.size, self.y + self.size)
        ]
        pygame.draw.polygon(surface, color, points)
        # Health bar
        bar_width = self.size
        bar_height = 6
        bar_x = int(self.x)
        bar_y = int(self.y - 12)
        draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, self.health, self.max_health, color_fg=(220,80,80), border_width=1)

class SquareEnemy(BaseEnemy):
    def __init__(self, x, y, tier=1):
        health = 30 + 15*(tier-1)
        speed = 1.5 + 0.2*(tier-1)
        damage = 8 + 2*(tier-1)
        kill_reward = 7 + 3*(tier-1)
        shot_cooldown = 80 - 8*(tier-1)
        shot_speed = 3 + 0.3*(tier-1)
        shot_range = 220 + 20*(tier-1)
        # Make size scale more strongly with tier
        size = 32 + 10*(tier-1)
        super().__init__(
            x, y,
            speed=speed,
            health=health,
            damage=damage,
            kill_reward=kill_reward,
            shot_cooldown=shot_cooldown,
            shot_speed=shot_speed,
            shot_range=shot_range,
            size=size,
            can_shoot=True,
            melee_range=25,
            melee_damage=damage,
            melee_cooldown=80
        )
        self.color = (random.randint(50,150), random.randint(180,255), random.randint(50,150))
        self.tier = tier

        # slight armor that reduces incoming damage
        self.armor = 1 + (tier - 1)

        # sometimes squares pause to aim
        self.aim_pause_timer = 0
        self.aim_pause_cooldown = 200

    def take_damage(self, amt):
        # reduce damage by armor
        amt = max(0, amt - self.armor)
        super().take_damage(amt)

    def update_special_behavior(self):
        # occasionally squares freeze in place for better aim
        if self.aim_pause_timer>0:
            self.aim_pause_timer-=1
            self.speed=0
        else:
            self.speed=1.5 + 0.2*(self.tier-1)
            if self.special_timer>0:
                self.special_timer-=1
            else:
                # do a pause
                self.aim_pause_timer=60
                self.special_timer=self.aim_pause_cooldown

    def draw(self, surface):
        color = (80, 200, 255) if not self.is_hit else (255,255,255)
        pygame.draw.rect(surface, color, (self.x, self.y, self.size, self.size))
        # Health bar
        bar_width = self.size
        bar_height = 6
        bar_x = int(self.x)
        bar_y = int(self.y - 12)
        draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, self.health, self.max_health, color_fg=(220,80,80), border_width=1)

class StarEnemy(BaseEnemy):
    def __init__(self, x, y, tier=1):
        health = 18 + 8*(tier-1)
        speed = 2.5 + 0.4*(tier-1)
        damage = 5 + 2*(tier-1)
        kill_reward = 8 + 3*(tier-1)
        shot_cooldown = 60 - 7*(tier-1)
        shot_speed = 5 + 0.5*(tier-1)
        shot_range = 260 + 20*(tier-1)
        # Make size scale more strongly with tier
        size = 28 + 9*(tier-1)
        super().__init__(
            x, y,
            speed=speed,
            health=health,
            damage=damage,
            kill_reward=kill_reward,
            shot_cooldown=shot_cooldown,
            shot_speed=shot_speed,
            shot_range=shot_range,
            size=size,
            can_shoot=True,
            melee_range=30,
            melee_damage=damage,
            melee_cooldown=70
        )
        self.color = (random.randint(50,150), random.randint(50,150), random.randint(180,255))
        self.tier = tier

        # short dash effect
        self.dash_timer = 0
        self.dash_duration = 20
        self.dash_speed_multiplier = 3
        self.dash_cooldown = 240

        # small invisibility frames
        self.invis_timer = 0
        self.invis_duration = 40

    def take_damage(self, amt):
        # If invis_timer > 0, we ignore damage
        if self.invis_timer>0:
            return
        super().take_damage(amt)

    def update_special_behavior(self):
        if self.dash_timer>0:
            self.dash_timer-=1
            if self.dash_timer<=0:
                self.speed /= self.dash_speed_multiplier
                # after dash, become invisible for a short time
                self.invis_timer=self.invis_duration
        else:
            if self.special_timer>0:
                self.special_timer-=1
            else:
                # do a dash
                self.dash_timer=self.dash_duration
                self.special_timer=self.dash_cooldown
                self.speed*= self.dash_speed_multiplier

        if self.invis_timer>0:
            self.invis_timer-=1

    def draw(self, surface):
        # if invis_timer>0, we can either reduce alpha or skip drawing
        if self.invis_timer>0:
            # draw partially transparent
            alpha_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            if self.is_hit:
                c = (255,255,255,self.invis_timer*3)  # flicker
            else:
                c = (*self.color, 60)  # faint
            cx = self.x + self.size//2
            cy = self.y + self.size//2
            # star shape
            points = []
            num_pts=5
            outer_r=self.size//2
            inner_r=outer_r*0.5
            angle_offset=-math.pi/2
            for i in range(num_pts*2):
                r = outer_r if i%2==0 else inner_r
                angle = (math.pi*i/num_pts)+angle_offset
                px = (self.size//2) + r*math.cos(angle)
                py = (self.size//2) + r*math.sin(angle)
                points.append((px,py))
            pygame.draw.polygon(alpha_surf, c, points)
            surface.blit(alpha_surf, (self.x, self.y))
            # Health bar
            bar_width = self.size
            bar_height = 6
            bar_x = int(self.x)
            bar_y = int(self.y - 12)
            draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, self.health, self.max_health, color_fg=(220,80,80), border_width=1)
        else:
            # normal
            color = (255,255,255) if self.is_hit else self.color
            cx = self.x + self.size//2
            cy = self.y + self.size//2
            points = []
            num_pts = 5
            outer_r = self.size//2
            inner_r = outer_r*0.5
            angle_offset = -math.pi/2
            for i in range(num_pts*2):
                r = outer_r if i%2==0 else inner_r
                angle = (math.pi*i/num_pts)+angle_offset
                px = cx + r*math.cos(angle)
                py = cy + r*math.sin(angle)
                points.append((px,py))
            pygame.draw.polygon(surface, color, points)
            # Health bar
            bar_width = self.size
            bar_height = 6
            bar_x = int(self.x)
            bar_y = int(self.y - 12)
            draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, self.health, self.max_health, color_fg=(220,80,80), border_width=1)

class BossEnemy(BaseEnemy):
    def __init__(self, x, y, tier=1):
        # Boss stats: much larger, much more health, much slower
        health = 300 + 300*(tier-1)  # Increased health
        speed = 0.7 + 0.1*(tier-1)   # Much slower
        damage = 18 + 4*(tier-1)
        kill_reward = 50 + 10*(tier-1)
        shot_cooldown = 36 - 3*(tier-1)  # much faster
        shot_speed = 7 + 1*(tier-1)
        shot_range = 350 + 30*(tier-1)
        size = 80 + 10*(tier-1)
        super().__init__(
            x, y,
            speed=speed,
            health=health,
            damage=damage,
            kill_reward=kill_reward,
            shot_cooldown=shot_cooldown,
            shot_speed=shot_speed,
            shot_range=shot_range,
            size=size,
            can_shoot=True,
            melee_range=55,
            melee_damage=damage,
            melee_cooldown=30
        )
        self.color = (255, 80, 200)
        self.tier = tier
        self.phase = 0
        self.phase_timer = 0

    def update_special_behavior(self):
        # Boss alternates between normal and "rage" phase (faster speed/attacks)
        if self.phase == 0:
            if self.special_timer > 0:
                self.special_timer -= 1
            else:
                self.phase = 1
                self.speed *= 1.7
                self.shot_cooldown = max(10, int(self.shot_cooldown * 0.5))
                self.phase_timer = 90
        elif self.phase == 1:
            if self.phase_timer > 0:
                self.phase_timer -= 1
            else:
                self.phase = 0
                self.speed /= 1.7
                self.shot_cooldown = int(self.shot_cooldown / 0.5)
                self.special_timer = 180

    def draw(self, surface):
        # Unique boss look: octagon with spikes
        cx = self.x + self.size // 2
        cy = self.y + self.size // 2
        base_color = (255, 80, 200) if not self.is_hit else (255,255,255)
        # Draw octagon
        oct_points = []
        num_sides = 8
        r = self.size // 2
        for i in range(num_sides):
            angle = 2 * math.pi * i / num_sides - math.pi / 8  # rotate a bit for visual appeal
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            oct_points.append((px, py))
        pygame.draw.polygon(surface, base_color, oct_points)
        # Draw spikes
        num_spikes = 8
        r_outer = r + 18
        for i in range(num_spikes):
            angle = 2 * math.pi * i / num_spikes - math.pi / 8
            x1 = cx + r * math.cos(angle)
            y1 = cy + r * math.sin(angle)
            x2 = cx + r_outer * math.cos(angle)
            y2 = cy + r_outer * math.sin(angle)
            pygame.draw.line(surface, (255, 180, 255), (x1, y1), (x2, y2), 5)
        # Health bar
        bar_width = self.size
        bar_height = 12
        bar_x = int(self.x)
        bar_y = int(self.y - 20)
        draw_health_bar(surface, bar_x, bar_y, bar_width, bar_height, self.health, self.max_health, color_fg=(255,80,200), border_width=2)

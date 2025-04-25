import pygame
from enum import Enum
from config import WIDTH, HEIGHT

class UpgradeType(Enum):
    PLAYER_ATTACK_DAMAGE = 1
    PLAYER_ATTACK_SPEED  = 2
    PLAYER_HEALTH        = 3
    PLAYER_SPEED         = 4
    CENTRAL_ATTACK       = 5
    CENTRAL_DEFENSE      = 6
    CENTRAL_REGEN        = 7
    TOWER_ATTACK         = 8
    TOWER_DEFENSE        = 9
    PASSIVE_INCOME       = 10

BASE_COSTS = {
    UpgradeType.PLAYER_ATTACK_DAMAGE : 20,
    UpgradeType.PLAYER_ATTACK_SPEED  : 15,
    UpgradeType.PLAYER_HEALTH        : 10,
    UpgradeType.PLAYER_SPEED         : 10,
    UpgradeType.CENTRAL_ATTACK       : 15,
    UpgradeType.CENTRAL_DEFENSE      : 14,
    UpgradeType.CENTRAL_REGEN        : 14,
    UpgradeType.TOWER_ATTACK         : 15,
    UpgradeType.TOWER_DEFENSE        : 12,
    UpgradeType.PASSIVE_INCOME       : 25,
}

LABELS = {
    UpgradeType.PLAYER_ATTACK_DAMAGE : "Player Damage",
    UpgradeType.PLAYER_ATTACK_SPEED  : "Player Fire Rate",
    UpgradeType.PLAYER_HEALTH        : "Player Max HP",
    UpgradeType.PLAYER_SPEED         : "Player Speed",
    UpgradeType.CENTRAL_ATTACK       : "Central Atk",
    UpgradeType.CENTRAL_DEFENSE      : "Central HP",
    UpgradeType.CENTRAL_REGEN        : "Central Regen",
    UpgradeType.TOWER_ATTACK         : "Tower Atk",
    UpgradeType.TOWER_DEFENSE        : "Tower HP",
    UpgradeType.PASSIVE_INCOME       : "Passive Income",
}

CATEGORIES = [
    {"label": "PLAYER",  "upgrades": [
        UpgradeType.PLAYER_ATTACK_DAMAGE,
        UpgradeType.PLAYER_ATTACK_SPEED,
        UpgradeType.PLAYER_HEALTH,
        UpgradeType.PLAYER_SPEED ]},
    {"label": "CENTRAL TOWER", "upgrades": [
        UpgradeType.CENTRAL_ATTACK,
        UpgradeType.CENTRAL_DEFENSE,
        UpgradeType.CENTRAL_REGEN ]},
    {"label": "PLAYER TOWERS", "upgrades": [
        UpgradeType.TOWER_ATTACK,
        UpgradeType.TOWER_DEFENSE ]},
    {"label": "MISC", "upgrades": [
        UpgradeType.PASSIVE_INCOME ]},
]

class UpgradeManager:
    COST_MULT = 1.6
    COOLDOWN_MULT = 0.82

    def __init__(self, player, central, towers):
        self.p = player
        self.c = central
        self.towers = towers
        self.levels = {u: 0 for u in UpgradeType}
        self.passive_income = 0.04
        self.player_regen   = 0.02
        self.central_regen  = 0.02

    def cost(self, upg):  return int(BASE_COSTS[upg] * (self.COST_MULT ** self.levels[upg]))
    def level(self, upg): return self.levels[upg]

    def apply(self, upg: UpgradeType) -> None:
        self.levels[upg] += 1
        if upg is UpgradeType.PLAYER_ATTACK_DAMAGE:
            self.p.bullet_damage += 0.7  # nerfed from +1
        elif upg is UpgradeType.PLAYER_ATTACK_SPEED:
            self.p.fire_cooldown = max(5, int(self.p.fire_cooldown * self.COOLDOWN_MULT)) 
        elif upg is UpgradeType.PLAYER_HEALTH:
            self.p.max_health += 12
            self.p.health     += 12
            self.player_regen += 0.03
        elif upg is UpgradeType.PLAYER_SPEED:
            self.p.speed += 0.7
        elif upg is UpgradeType.CENTRAL_ATTACK:
            self.c.shot_damage   += .5
            self.c.shot_range    += 30
            self.c.shot_cooldown = max(3, int(self.c.shot_cooldown * self.COOLDOWN_MULT))
        elif upg is UpgradeType.CENTRAL_DEFENSE:
            self.c.max_health += 25
            self.c.health     += 25
        elif upg is UpgradeType.CENTRAL_REGEN:
            self.central_regen += 0.03
        elif upg is UpgradeType.TOWER_ATTACK:
            for t in self.towers:
                t.shot_damage   += .7 
                t.shot_range    += 20
                t.shot_cooldown = max(2, int(t.shot_cooldown * self.COOLDOWN_MULT))  
        elif upg is UpgradeType.TOWER_DEFENSE:
            for t in self.towers:
                t.max_health += 15
                t.health     += 15
        elif upg is UpgradeType.PASSIVE_INCOME:
            self.passive_income += 0.015

    def update_passives(self):
        self.p.money += self.passive_income
        if 0 < self.p.health < self.p.max_health:
            self.p.health = min(self.p.max_health, self.p.health + self.player_regen)
        if 0 < self.c.health < self.c.max_health:
            self.c.health = min(self.c.max_health, self.c.health + self.central_regen)

class UpgradeMenu:
    W, H   = 600, 700  # wider menu
    PAD    = 22
    ROW_H  = 26
    BTN    = 36
    FONT   = pygame.font.match_font("consolas,couriernew,monospace")

    def __init__(self, mgr: UpgradeManager):
        self.mgr      = mgr
        self.buttons  = []
        self.message  = ""
        self.good     = True
        self.timer    = 0

    def handle_mouse(self, pos, player):
        for rect, upg in self.buttons:
            if rect.collidepoint(pos):
                cost = self.mgr.cost(upg)
                if player.money >= cost:
                    player.money -= cost
                    self.mgr.apply(upg)
                    self._flash(f"{LABELS[upg]} purchased", True)
                else:
                    self._flash("Not enough money", False)
                break

    def _flash(self, txt, success):
        self.message, self.good, self.timer = txt, success, 120

    def _tick(self):
        if self.timer:
            self.timer -= 1
            if self.timer == 0:
                self.message = ""

    def draw_menu(self, surf, player):
        self._tick()
        mx, my = WIDTH // 2 - self.W // 2, HEIGHT // 2 - self.H // 2
        panel = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 230))
        surf.blit(panel, (mx, my))
        font = pygame.font.Font(self.FONT, 18)
        cx   = mx + self.W // 2
        y    = my + 28
        title = font.render("UPGRADES", True, (255, 255, 0))
        surf.blit(title, title.get_rect(center=(cx, y)))
        y += 32
        self.buttons.clear()
        for cat in CATEGORIES:
            hdr = font.render(f"[ {cat['label']} ]", True, (140, 210, 255))
            surf.blit(hdr, (mx + self.PAD, y))
            y += self.ROW_H
            for upg in cat["upgrades"]:
                lvl  = self.mgr.level(upg)
                inc  = self._inc_token(upg)
                cost = self.mgr.cost(upg)
                line_txt = f"{LABELS[upg]:<16} Lv{lvl:<2} {inc:<6} ${cost:<3}"
                line_surf = font.render(line_txt, True, (255, 255, 255))
                surf.blit(line_surf, (mx + self.PAD, y))
                btn_rect = pygame.Rect(
                    mx + self.W - self.PAD - self.BTN, y - 2,
                    self.BTN, self.BTN
                )
                pygame.draw.rect(surf, (45, 170, 60), btn_rect, border_radius=7)
                plus_surf = font.render("+", True, (255, 255, 255))
                surf.blit(plus_surf, plus_surf.get_rect(center=btn_rect.center))
                self.buttons.append((btn_rect, upg))
                y += self.ROW_H
            y += 12
        footer = pygame.Rect(mx, my + self.H - 54, self.W, 54)
        pygame.draw.rect(surf, (20, 20, 20), footer)
        cash_surf = font.render(f"Money {int(player.money)}", True, (255, 255, 0))
        surf.blit(cash_surf, (mx + self.PAD, footer.y + 16))
        if self.message:
            color = (40, 255, 40) if self.good else (255, 70, 70)
            msg_surf = font.render(self.message, True, color)
            surf.blit(msg_surf, msg_surf.get_rect(center=(mx + self.W // 2, footer.y + 16)))

    def _inc_token(self, upg: UpgradeType) -> str:
        return {
            UpgradeType.PLAYER_ATTACK_DAMAGE : "+0.7 dmg",
            UpgradeType.PLAYER_ATTACK_SPEED  : "-18% cd",
            UpgradeType.PLAYER_HEALTH        : "+12 HP",
            UpgradeType.PLAYER_SPEED         : "+0.7 spd",
            UpgradeType.CENTRAL_ATTACK       : "+0.5 dmg/+30 rng +spd",
            UpgradeType.CENTRAL_DEFENSE      : "+25 HP",
            UpgradeType.CENTRAL_REGEN        : "+0.03 regen",
            UpgradeType.TOWER_ATTACK         : "+0.7 dmg/+20 rng +spd",
            UpgradeType.TOWER_DEFENSE        : "+15 HP",
            UpgradeType.PASSIVE_INCOME       : "+0.015/frame",
        }.get(upg, "")

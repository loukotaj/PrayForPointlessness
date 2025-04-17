# state.py
"""
Central game loop & global state.

Folders expected (relative to this file):

Images/
    intro_1_city.png           victory_glow.png
    intro_2_fences.png         defeat_ruins.png
    intro_3_roundabout.png     mid1_soften.png
    intro_4_construction.png   mid2_resistance.png
    intro_5_horizon.png

Music/
    intro/   *.mp3  *.ogg  …
    menu/    …
    battle/  …
    victory/ …
    defeat/  …
    fame/    …

Simply drop any number of tracks into those sub‑folders.
"""

import os, sys, random, math
import pygame

from config      import WIDTH, HEIGHT
from slides      import (INTRO_SLIDES, MID_SLIDES_A, MID_SLIDES_B,
                         VICTORY_SLIDES, DEFEAT_SLIDES)
from waves       import WAVES
from player      import Player
from tower       import CentralTower, PlayerTower
from enemy       import spawn_enemy
from projectile  import Projectile
from upgrades    import UpgradeManager, UpgradeMenu
from instructions import draw_instructions
from music_manager import MusicManager, MusicMode    # ← NEW

# ──────────────────────────────────────────────────────────
#   high‑level states
# ──────────────────────────────────────────────────────────
STATE_SLIDES  = 0
STATE_GAME    = 1
STATE_VICTORY = 2
STATE_DEFEAT  = 3


class GameState:
    # ------------------------------------------------------------------
    #   static “singletons”
    # ------------------------------------------------------------------
    screen: pygame.Surface = None
    current_state         = STATE_SLIDES

    player:        Player        = None
    central_tower: CentralTower  = None
    towers                       = []
    enemies                      = []
    projectiles                  = []

    upgrade_manager: UpgradeManager = None
    upgrade_menu:    UpgradeMenu    = None
    show_upgrades  = False
    show_help      = True

    # wave bookkeeping
    wave_index        = 0
    step_index        = 0
    remaining_in_step = 0
    spawn_timer       = 0
    wave_running      = False

    # slides / cut‑scenes
    slide_list  = INTRO_SLIDES
    slide_index = 0
    mid_a_shown = False
    mid_b_shown = False

    # small image cache
    _img_cache: dict[str, pygame.Surface] = {}

    # --------------------------------------------------------------
    #                        INIT / RESET
    # --------------------------------------------------------------
    @classmethod
    def init(cls, scr: pygame.Surface):
        cls.screen        = scr
        cls.current_state = STATE_SLIDES
        cls.slide_list    = INTRO_SLIDES
        cls.slide_index   = 0
        cls.mid_a_shown   = cls.mid_b_shown = False

        # music system -------------------------------------------------
        MusicManager.init()          # scans sub‑folders
        MusicManager.set_mode(MusicMode.INTRO)

        # main entities -----------------------------------------------
        cls.player = Player(WIDTH // 2, HEIGHT // 2 + 150)
        cls.central_tower = CentralTower(
            x=WIDTH // 2, y=HEIGHT // 2,
            max_health=300, radius=50,
            shot_cooldown=45, shot_speed=7,
            shot_damage=6,  shot_range=350
        )
        cls.towers.clear()
        cls.enemies.clear()
        cls.projectiles.clear()

        cls.wave_index        = 0
        cls.step_index        = 0
        cls.remaining_in_step = 0
        cls.spawn_timer       = 0
        cls.wave_running      = False

        cls.upgrade_manager = UpgradeManager(cls.player, cls.central_tower, cls.towers)
        cls.upgrade_menu    = UpgradeMenu(cls.upgrade_manager)

        cls.show_upgrades = False
        cls.show_help     = True

    # ==============================================================
    #                        EVENT HANDLER
    # ==============================================================
    @classmethod
    def process_event(cls, e: pygame.event.Event):
        # ---------- slides ----------
        if cls.current_state == STATE_SLIDES:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                # Check if on last slide
                if cls.slide_index == len(cls.slide_list) - 1:
                    if cls.slide_list is INTRO_SLIDES:
                        cls.current_state = STATE_GAME
                        MusicManager.set_mode(MusicMode.GAME)
                    elif cls.slide_list is VICTORY_SLIDES or cls.slide_list is DEFEAT_SLIDES:
                        cls.init(cls.screen)
                    else:  # mid‑game slides
                        cls.current_state = STATE_GAME
                        MusicManager.set_mode(MusicMode.GAME)
                else:
                    cls.slide_index += 1

        # ---------- victory / defeat ----------
        elif cls.current_state in (STATE_VICTORY, STATE_DEFEAT):
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif e.key == pygame.K_r:
                    cls.init(cls.screen)

        # ---------- gameplay ----------
        elif cls.current_state == STATE_GAME:
            if cls.show_upgrades:
                if e.type == pygame.KEYDOWN and e.key in (pygame.K_u, pygame.K_ESCAPE, pygame.K_SPACE):
                    cls.show_upgrades = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    cls.upgrade_menu.handle_mouse(e.pos, cls.player)
            elif cls.show_help:
                if e.type == pygame.KEYDOWN and e.key in (pygame.K_h, pygame.K_SPACE, pygame.K_ESCAPE):
                    cls.show_help = False
            else:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_u:
                        cls.show_upgrades = True
                    elif e.key == pygame.K_h:
                        cls.show_help = True
                    elif e.key == pygame.K_t and cls.player.money >= 50:
                        # Prevent placing towers on top of each other
                        px, py = cls.player.x, cls.player.y
                        min_dist = 20  # Minimum allowed distance between towers
                        too_close = False
                        for t in cls.towers:
                            dist = math.hypot(t.x - px, t.y - py)
                            if dist < t.radius + 25 + min_dist:
                                too_close = True
                                break
                        # Also prevent placing on top of central tower
                        dist_central = math.hypot(cls.central_tower.x - px, cls.central_tower.y - py)
                        if dist_central < cls.central_tower.radius + 25 + min_dist:
                            too_close = True
                        if not too_close:
                            cls.towers.append(PlayerTower(
                                x=px, y=py,
                                max_health=80, radius=25,
                                shot_cooldown=60, shot_speed=5,
                                shot_damage=4,  shot_range=200))
                            cls.player.money -= 50
                        # Optionally: else play error sound or flash message

    # ==============================================================
    #                          UPDATE
    # ==============================================================
    @classmethod
    def update(cls):
        if cls.current_state == STATE_SLIDES:
            cls._draw_slides(); return
        if cls.current_state == STATE_GAME:
            cls._update_game(); cls._draw_game(); return
        if cls.current_state == STATE_VICTORY:
            cls._draw_slides(); return
        if cls.current_state == STATE_DEFEAT:
            cls._draw_slides(); return

    # --------------------------------------------------------------
    #                      SLIDE HELPERS
    # --------------------------------------------------------------
    @classmethod
    def _load_image(cls, name: str) -> pygame.Surface:
        if not name: return None
        if name in cls._img_cache: return cls._img_cache[name]
        path = os.path.join("images", name)
        try:
            img  = pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            print(f"Image not found: {path}"); return None
        scale = HEIGHT / img.get_height()
        img   = pygame.transform.smoothscale(img, (int(img.get_width()*scale), HEIGHT))
        cls._img_cache[name] = img
        return img

    @staticmethod
    def _wrap(text, font, max_w):
        lines, out = text.split("\n"), []
        for para in lines:
            words, cur = para.split(), ""
            for w in words:
                test = (cur+" "+w).strip()
                if font.size(test)[0] > max_w:
                    out.append(cur); cur = w
                else: cur = test
            out.append(cur); out.append("")
        return out

    @classmethod
    def _draw_slides(cls):
        slides = cls.slide_list
        slide = slides[cls.slide_index]
        cls.screen.fill((0,0,0))
        left_w = WIDTH // 2
        right_w = WIDTH - left_w
        img_margin = 30

        # Draw image on right half
        if slide.get("art"):
            img = cls._load_image(slide["art"])
            if img:
                max_img_w = right_w - 2 * img_margin
                max_img_h = HEIGHT - 2 * img_margin
                scale = min(max_img_w / img.get_width(), max_img_h / img.get_height())
                img_w = int(img.get_width() * scale)
                img_h = int(img.get_height() * scale)
                img_scaled = pygame.transform.smoothscale(img, (img_w, img_h))
                img_rect = img_scaled.get_rect(center=(left_w + right_w // 2, HEIGHT // 2))
                cls.screen.blit(img_scaled, img_rect)

        # Draw text on left half
        font = pygame.font.SysFont(None, 40, bold=True)
        y = 60
        for ln in cls._wrap(slide["text"], font, left_w - 40):
            surf = font.render(ln, True, (255,255,255))
            cls.screen.blit(surf, surf.get_rect(midleft=(30, y)))
            y += 36

        # Navigation hint
        hint_font = pygame.font.SysFont(None, 32, bold=True)
        if cls.slide_index < len(slides) - 1:
            hint = hint_font.render("SPACE to continue", True, (200,200,200))
        else:
            # End-of-slideshow hints
            if slides is VICTORY_SLIDES:
                hint = hint_font.render("SPACE to finish", True, (200,255,200))
            elif slides is DEFEAT_SLIDES:
                hint = hint_font.render("SPACE to finish", True, (255,120,120))
            else:
                hint = hint_font.render("SPACE to continue", True, (200,200,200))
        cls.screen.blit(hint, hint.get_rect(bottomright=(WIDTH-30, HEIGHT-25)))
        pygame.display.flip()

    # --------------------------------------------------------------
    #                       GAME UPDATE
    # --------------------------------------------------------------
    @classmethod
    def _update_game(cls):
        if cls.show_upgrades or cls.show_help:
            return

        # entities
        cls.player.update(WIDTH, HEIGHT, cls.enemies, cls.projectiles)
        cls.central_tower.update(cls.enemies, cls.projectiles)
        for tw in cls.towers: tw.update(cls.enemies, cls.projectiles)
        cls.upgrade_manager.update_passives()

        # waves
        if cls.wave_running:
            cls._spawner_step()
        elif cls.wave_index < len(WAVES):
            cls._start_wave()

        # enemy / projectile step
        for e in cls.enemies:
            e.update(cls.player, cls.towers, cls.central_tower,
                     cls.projectiles, cls.enemies)
        for p in cls.projectiles:
            p.update(WIDTH, HEIGHT)
        cls._handle_projectiles()

        cls.projectiles[:] = [p for p in cls.projectiles if p.alive]
        cls.enemies[:]     = [e for e in cls.enemies if e.health > 0]
        cls.towers[:]      = [t for t in cls.towers if t.health > 0]

        if cls.player.health<=0 or cls.central_tower.health<=0:
            cls.slide_list  = DEFEAT_SLIDES
            cls.slide_index = 0
            cls.current_state = STATE_SLIDES
            MusicManager.set_mode(MusicMode.DEFEAT)

    # -------------- spawner helpers --------------
    @classmethod
    def _start_wave(cls):
        cls.wave_running   = True
        cls.step_index     = 0
        cls.remaining_in_step = WAVES[cls.wave_index]["steps"][0]["count"]
        cls.spawn_timer    = 0

    @classmethod
    def _spawner_step(cls):
        wave = WAVES[cls.wave_index]
        if cls.step_index < len(wave["steps"]):
            step = wave["steps"][cls.step_index]
            if cls.remaining_in_step > 0:
                cls.spawn_timer += 1
                if cls.spawn_timer >= wave["spawn_rate"]:
                    cls.spawn_timer = 0
                    cls._spawn_enemy(step)
            else:
                cls.step_index += 1
                if cls.step_index < len(wave["steps"]):
                    cls.remaining_in_step = wave["steps"][cls.step_index]["count"]
        else:
            if not any(e.health>0 for e in cls.enemies):
                cls.player.money += wave["reward"]
                cls.wave_running = False
                cls.wave_index  += 1
                # cut‑scenes
                if cls.wave_index == 5 and not cls.mid_a_shown:
                    cls._launch_cutscene(MID_SLIDES_A); cls.mid_a_shown=True
                elif cls.wave_index == 10 and not cls.mid_b_shown:
                    cls._launch_cutscene(MID_SLIDES_B); cls.mid_b_shown=True
                elif cls.wave_index >= len(WAVES):
                    cls._launch_cutscene(VICTORY_SLIDES, victory=True)

    @classmethod
    def _spawn_enemy(cls, step):
        cls.enemies.append(
            spawn_enemy(step["type"], step["tier"],
                        random.randint(0, WIDTH), 0))
        cls.remaining_in_step -= 1

    @classmethod
    def _launch_cutscene(cls, slides, *, victory=False):
        cls.slide_list  = slides
        cls.slide_index = 0
        cls.current_state = STATE_SLIDES
        MusicManager.set_mode(MusicMode.VICTORY if victory else MusicMode.MENU)

    # -------------- collisions --------------
    @classmethod
    def _handle_projectiles(cls):
        for p in cls.projectiles:
            if not p.alive: continue
            if p.is_friendly:
                for e in cls.enemies:
                    if e.health<=0: continue
                    ex,ey = e.center()
                    if math.hypot(ex-p.x, ey-p.y) < (e.size/2+p.radius):
                        e.take_damage(p.damage); p.alive=False
                        if e.health<=0: cls.player.money += e.kill_reward
                        break
            else:
                if math.hypot(cls.player.x-p.x, cls.player.y-p.y) < (cls.player.radius+p.radius):
                    cls.player.take_damage(p.damage); p.alive=False; continue
                for tw in cls.towers+[cls.central_tower]:
                    if math.hypot(tw.x-p.x, tw.y-p.y) < (tw.radius+p.radius):
                        tw.take_damage(p.damage); p.alive=False; break

    # -------------- draw --------------
    @classmethod
    def _draw_game(cls):
        cls.screen.fill((30,30,30))
        cls.central_tower.draw(cls.screen)
        for tw in cls.towers: tw.draw(cls.screen)
        for e  in cls.enemies: e.draw(cls.screen)
        for p  in cls.projectiles: p.draw(cls.screen)
        cls.player.draw(cls.screen)

        font = pygame.font.SysFont(None, 30)
        hud  = (f"Wave {cls.wave_index+1}/{len(WAVES)}    "
                f"HP {int(cls.player.health)}/{cls.player.max_health}    "
                f"Money {int(cls.player.money)}")
        cls.screen.blit(font.render(hud, True, (255,255,255)), (20,20))

        if cls.show_upgrades:
            cls.upgrade_menu.draw_menu(cls.screen, cls.player)
        if cls.show_help:
            draw_instructions(cls.screen)

        pygame.display.flip()

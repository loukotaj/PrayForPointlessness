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
STATE_MAINMENU = -1  # Add main menu state
STATE_SLIDES  = 0
STATE_GAME    = 1
STATE_VICTORY = 2
STATE_DEFEAT  = 3


class GameState:
    # ------------------------------------------------------------------
    #   static “singletons”
    # ------------------------------------------------------------------
    screen: pygame.Surface = None
    current_state         = STATE_MAINMENU  # Start at main menu

    player:        Player        = None
    central_tower: CentralTower  = None
    towers                       = []
    enemies                      = []
    projectiles                  = []

    upgrade_manager: UpgradeManager = None
    upgrade_menu:    UpgradeMenu    = None
    show_upgrades  = False
    show_help      = True

    difficulty = 1.0  # Default difficulty (1.0 = normal)
    mainmenu_slider = 1.0  # For UI slider
    mainmenu_slider_drag = False

    # wave bookkeeping
    wave_index        = 0
    step_index        = 0
    remaining_in_step = 0
    spawn_timer       = 0
    wave_running      = False
    wave_timer        = 0  # Add a timer for the current wave
    wave_time_limit   = 3600  # 1 minute at 60fps (default, but will be set per-wave)

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
        cls.current_state = STATE_MAINMENU  # Start at main menu
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
        cls.wave_timer        = 0

        cls.upgrade_manager = UpgradeManager(cls.player, cls.central_tower, cls.towers)
        cls.upgrade_menu    = UpgradeMenu(cls.upgrade_manager)

        cls.show_upgrades = False
        cls.show_help     = True

    # ==============================================================

    @classmethod
    def process_event(cls, e: pygame.event.Event):
        # ---------- main menu ----------
        if cls.current_state == STATE_MAINMENU:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                # Slider
                slider_rect = cls._mainmenu_slider_rect()
                slider_rect.y += 80  # match the y-offset in _draw_mainmenu
                if slider_rect.collidepoint(mx, my):
                    cls.mainmenu_slider_drag = True
                    cls._mainmenu_update_slider(mx)
                    return  # Don't start game if slider is clicked
                # Start button
                btn_rect = cls._mainmenu_btn_rect()
                btn_rect.y += 90  # match the y-offset in _draw_mainmenu
                if btn_rect.collidepoint(mx, my):
                    cls.difficulty = cls.mainmenu_slider
                    pygame.difficulty = cls.difficulty  # <-- Set global difficulty for enemy.py
                    cls.current_state = STATE_SLIDES
                    MusicManager.set_mode(MusicMode.INTRO)
                    return
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                cls.mainmenu_slider_drag = False
            elif e.type == pygame.MOUSEMOTION and cls.mainmenu_slider_drag:
                mx, _ = e.pos
                cls._mainmenu_update_slider(mx)
            return

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

    @classmethod
    def _mainmenu_btn_rect(cls):
        w, h = 320, 70
        x = WIDTH // 2 - w // 2
        y = HEIGHT // 2 + 100
        return pygame.Rect(x, y, w, h)

    @classmethod
    def _mainmenu_slider_rect(cls):
        # Slider bar area
        sw, sh = 400, 32
        sx = WIDTH // 2 - sw // 2
        sy = HEIGHT // 2 + 10
        return pygame.Rect(sx, sy, sw, sh)

    @classmethod
    def _mainmenu_update_slider(cls, mx):
        sw = 400
        sx = WIDTH // 2 - sw // 2
        rel = (mx - sx) / sw
        rel = max(0, min(1, rel))
        cls.mainmenu_slider = round(0.5 + 1.5 * rel, 2)

    # ==============================================================

    @classmethod
    def update(cls):
        if cls.current_state == STATE_MAINMENU:
            cls._draw_mainmenu(); return
        if cls.current_state == STATE_SLIDES:
            cls._draw_slides(); return
        if cls.current_state == STATE_GAME:
            cls._update_game(); cls._draw_game(); return
        if cls.current_state == STATE_VICTORY:
            cls._draw_slides(); return
        if cls.current_state == STATE_DEFEAT:
            cls._draw_slides(); return

    @classmethod
    def _draw_mainmenu(cls):
        cls.screen.fill((20, 20, 40))
        font_big = pygame.font.SysFont(None, 80, bold=True)
        font = pygame.font.SysFont(None, 38)
        font_small = pygame.font.SysFont(None, 28)
        # Title
        title = font_big.render("Pray for Pointlessness", True, (255, 255, 120))
        cls.screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 160)))  # moved up
        # Subtitle
        sub = font.render("Defend the Signal. Restore Roundness.", True, (180, 220, 255))
        cls.screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))  # moved up
        # Difficulty slider
        slider_rect = cls._mainmenu_slider_rect()
        slider_rect.y += 80  # move slider further down (was 30)
        pygame.draw.rect(cls.screen, (60, 60, 80), slider_rect, border_radius=10)
        # Slider bar
        bar_y = slider_rect.y + slider_rect.height // 2
        pygame.draw.line(cls.screen, (180,180,180), (slider_rect.x+16, bar_y), (slider_rect.x+slider_rect.width-16, bar_y), 6)
        # Slider knob
        rel = (cls.mainmenu_slider - 0.5) / 1.5
        knob_x = int(slider_rect.x + 16 + rel * (slider_rect.width - 32))
        pygame.draw.circle(cls.screen, (255, 220, 80), (knob_x, bar_y), 16)
        # Slider label
        diff_txt = f"Difficulty: {cls.mainmenu_slider:.2f}x"
        txt = font.render(diff_txt, True, (255,255,255))
        cls.screen.blit(txt, (slider_rect.x, slider_rect.y - 54))  # more space above slider
        # Min/max
        min_txt = font_small.render("Easy", True, (180,255,180))
        max_txt = font_small.render("Hard", True, (255,180,180))
        cls.screen.blit(min_txt, (slider_rect.x-8, bar_y+28))  # more space below bar
        cls.screen.blit(max_txt, (slider_rect.x+slider_rect.width-60, bar_y+28))
        # Start button
        btn_rect = cls._mainmenu_btn_rect()
        btn_rect.y += 90  # move button further down (was 40)
        pygame.draw.rect(cls.screen, (80, 180, 80), btn_rect, border_radius=12)
        btn_label = font.render("START", True, (255,255,255))
        cls.screen.blit(btn_label, btn_label.get_rect(center=btn_rect.center))
        # Instructions
        hint = font_small.render("Use the slider to set difficulty. Click START to play.", True, (200,200,200))
        cls.screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 300)))  # move hint further down
        pygame.display.flip()

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
            cls.wave_timer += 1  # Increment wave timer
            cls._spawner_step()
            # Check if wave is taking too long
            if cls.wave_timer > cls.wave_time_limit:
                # Force end of wave: remove all remaining enemies and give reward
                for e in cls.enemies:
                    e.health = 0
                # Do not clear enemies here; let them be removed after all projectiles processed
                wave = WAVES[cls.wave_index]
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
        cls.wave_timer     = 0  # Reset wave timer
        # Set wave_time_limit longer for later waves (base: 60s, +10s per wave)
        # Clamp to a reasonable max (e.g. 3 min)
        base = 3600  # 60s
        per_wave = 600  # 10s per wave
        max_limit = 10800  # 180s
        cls.wave_time_limit = min(base + per_wave * cls.wave_index, max_limit)

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
        # Spawn enemies from all edges, not just the top
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            x = random.randint(0, WIDTH)
            y = 0
        elif edge == 'bottom':
            x = random.randint(0, WIDTH)
            y = HEIGHT
        elif edge == 'left':
            x = 0
            y = random.randint(0, HEIGHT)
        else:  # right
            x = WIDTH
            y = random.randint(0, HEIGHT)
        cls.enemies.append(
            spawn_enemy(step["type"], step["tier"], x, y)
        )
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
        ctrl_font = pygame.font.SysFont(None, 26)
        ctrl_txt = "T: Tower   U: Upgrade   H: Help"
        cls.screen.blit(ctrl_font.render(ctrl_txt, True, (180,255,180)), (20, 0))

        if cls.wave_index >= len(WAVES):
            if len(cls.enemies) == 0:
                signal_strength = 1.0
            else:
                signal_strength = 0.999
        else:
            if cls.wave_index == len(WAVES) - 1 and len(cls.enemies) > 0:
                signal_strength = (cls.wave_index + 0.99) / len(WAVES)
            else:
                signal_strength = (cls.wave_index + 1) / len(WAVES)
        hud  = (f"Signal Strength {signal_strength:.3%}    "
            f"HP {int(cls.player.health)}/{cls.player.max_health}    "
            f"Roundness Points {int(cls.player.money)}")
        cls.screen.blit(font.render(hud, True, (255,255,255)), (20,20))

        if cls.show_upgrades:
            cls.upgrade_menu.draw_menu(cls.screen, cls.player)
        if cls.show_help:
            draw_instructions(cls.screen)

        pygame.display.flip()

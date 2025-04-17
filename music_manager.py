# music_manager.py
"""
Category‑based soundtrack controller.
Works with the six sub‑folders:
    intro • menu • battle • fame • victory • defeat
"""

import os, random
import pygame

MUSIC_ROOT = os.path.join(os.path.dirname(__file__), "music")

class MusicMode:
    INTRO   = "intro"    # story / cut‑scenes before play
    MENU    = "menu"     # upgrade screen or help overlay (optional)
    BATTLE  = "battle"   # mid game cutscene
    GAME    = "game"     # regular gameplay
    VICTORY = "victory"  # final win screen
    DEFEAT  = "defeat"   # game‑over

class MusicManager:
    _tracks   : dict[str, list[str]] = {}
    _cur_mode : str | None = None

    # ------------------------------------------------------------
    @classmethod
    def init(cls, volume: float = 0.7):
        pygame.mixer.init()
        pygame.mixer.music.set_volume(volume)
        # scan available folders
        for folder in os.listdir(MUSIC_ROOT):
            path = os.path.join(MUSIC_ROOT, folder)
            if os.path.isdir(path):
                cls._tracks[folder] = [
                    os.path.join(path, f)
                    for f in os.listdir(path)
                    if f.lower().endswith((".mp3", ".ogg", ".wav"))
                ]

    # ------------------------------------------------------------
    @classmethod
    def set_mode(cls, mode: str):
        if mode == cls._cur_mode or mode not in cls._tracks:
            return
        cls._cur_mode = mode
        if not cls._tracks[mode]:
            pygame.mixer.music.stop()
            return
        track = random.choice(cls._tracks[mode])
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(-1)

    @classmethod
    def fadeout(cls, ms: int = 1500):
        pygame.mixer.music.fadeout(ms)

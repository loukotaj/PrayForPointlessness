import os, random
import pygame
import sys

MUSIC_ROOT = os.path.join(os.path.dirname(__file__), "music")

class MusicMode:
    INTRO   = "intro"
    MENU    = "menu"
    BATTLE  = "battle"
    GAME    = "game"
    VICTORY = "victory"
    DEFEAT  = "defeat"

class MusicManager:
    _tracks   : dict[str, list[str]] = {}
    _cur_mode : str | None = None
    _sfx_cache: dict[str, pygame.mixer.Sound] = {}

    @classmethod
    def init(cls, volume: float = 0.7):
        pygame.mixer.init()
        pygame.mixer.music.set_volume(volume)
        for folder in os.listdir(MUSIC_ROOT):
            path = os.path.join(MUSIC_ROOT, folder)
            if os.path.isdir(path):
                cls._tracks[folder] = [
                    os.path.join(path, f)
                    for f in os.listdir(path)
                    if f.lower().endswith((".mp3", ".ogg", ".wav"))
                ]

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

    @classmethod
    def play_sfx(cls, name: str):
        # --- Web workaround: use JS audio for SFX if on pygbag/web ---
        if sys.platform == "emscripten":
            try:
                import js
                # Try to play the SFX using browser Audio
                js.eval(f"""
                (function(){{
                    let sfx = new Audio('/music/{name}');
                    sfx.volume = 0.7;
                    sfx.play();
                }})();
                """)
            except Exception:
                pass
            return
        # --- Desktop: use pygame.mixer.Sound as before ---
        path = os.path.join(MUSIC_ROOT, name)
        if not os.path.isfile(path):
            return
        if name not in cls._sfx_cache:
            try:
                cls._sfx_cache[name] = pygame.mixer.Sound(path)
            except Exception:
                return
        try:
            cls._sfx_cache[name].play()
        except Exception:
            pass

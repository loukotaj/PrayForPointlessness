WIDTH = 1800
HEIGHT = 1100

# Game states
STATE_INTRO = 0
STATE_GAME = 1
STATE_VICTORY = 2
STATE_DEFEAT = 3

# UI
HUD_FONT_SIZE = 36
INSTRUCTIONS_FONT_SIZE = 28
INSTRUCTIONS_OVERLAY_SIZE = (800, 400)
INSTRUCTIONS_OVERLAY_ALPHA = 180

# Player
PLAYER_START_MONEY = 50
PLAYER_START_X = WIDTH // 2
PLAYER_START_Y = HEIGHT // 2 + 150

# Central Tower
CENTRAL_TOWER_CONFIG = {
    "x": WIDTH // 2,
    "y": HEIGHT // 2,
    "max_health": 300,
    "radius": 50,
    "shot_cooldown": 45,
    "shot_speed": 7,
    "shot_damage": 6,
    "shot_range": 350,
}

# Player Tower
PLAYER_TOWER_COST = 50
PLAYER_TOWER_CONFIG = {
    "max_health": 80,
    "radius": 25,
    "shot_cooldown": 60,
    "shot_speed": 5,
    "shot_damage": 4,
    "shot_range": 200,
}

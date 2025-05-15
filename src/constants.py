# constants.py (or src/constants.py if using src folder)

"""
Game constants and configuration values.
"""

# Game basics
GAME_TITLE = "LoL Dodge Game"
VERSION = "0.1.0"
FPS = 60

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# UI colors
UI_BACKGROUND = DARK_GRAY
UI_TEXT = WHITE
UI_HIGHLIGHT = YELLOW
UI_SECONDARY = LIGHT_GRAY
UI_ACCENT = CYAN

# Game states
STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_OPTIONS = "options"
STATE_CREDITS = "credits"
STATE_GAME_OVER = "game_over"
STATE_PAUSE = "pause"

# Asset paths
ASSET_DIR = "assets"
IMAGE_DIR = f"{ASSET_DIR}/images"
SOUND_DIR = f"{ASSET_DIR}/sounds"
FONT_DIR = f"{ASSET_DIR}/fonts"

# Font settings
DEFAULT_FONT = "main_font.ttf"
TITLE_FONT_SIZE = 64
HEADING_FONT_SIZE = 48
NORMAL_FONT_SIZE = 32
SMALL_FONT_SIZE = 24

# Sound settings
DEFAULT_MUSIC_VOLUME = 0.7  # 70%
DEFAULT_SFX_VOLUME = 0.8    # 80%

# Game settings
DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"
DEFAULT_DIFFICULTY = DIFFICULTY_NORMAL

# Player settings
PLAYER_SPEED = 5
PLAYER_HEALTH = 100
PLAYER_LIVES = 3

# Enemy settings
ENEMY_SPEED = 3
ENEMY_HEALTH = 50
ENEMY_DAMAGE = 10

# Physics
GRAVITY = 0.5
JUMP_FORCE = -10
FRICTION = 0.8

# Menu settings
MENU_SPACING = 60
MENU_START_Y = 250

# Debug
DEBUG_MODE = False
SHOW_FPS = True
SHOW_HITBOXES = False

#Enemy Manager settings
SPAWN_DELAY = 180
MAX_ENEMIES = 10

#Abilities and Summoner Spells
FLASH_COOLDOWN = 60
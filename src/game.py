import pygame 
import json
import os
from src.player import Player 
from src.asset_manager import AssetManager
from game_states import *
from src.constants import (
    GAME_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, STATE_MENU,
    DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME
)

class Game:

    def __init__(self):
        pygame.init()
        
        self.settings = {}
        self.load_settings()
        
        self.fullscreen = self.settings.get("fullscreen", False)
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(400, 300)

        self.assets = AssetManager()
        self.assets.preload_common_assets()
        
        # Set volumes from settings
        music_volume = self.settings.get("music_volume", DEFAULT_MUSIC_VOLUME * 100) / 100
        sfx_volume = self.settings.get("sfx_volume", DEFAULT_SFX_VOLUME * 100) / 100
        self.assets.set_music_volume(music_volume)
        self.assets.set_sfx_volume(sfx_volume)

        self.state = StateFactory.create_state(STATE_MENU, self)
        
        # Initialize game variables
        self.score = 0
        self.enemies = []
        self.collectibles = []

    def __setattr__(self, name, value):
        if name == 'state' and value is None:
            import traceback
            print("WARNING: Setting game state to None!")
            traceback.print_stack()
        super().__setattr__(name, value)

    def load_settings(self):
        """Load game settings from a file or use defaults."""
        settings_path = "settings.json"
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    self.settings = json.load(f)
            else:
                # Default settings
                self.settings = {
                    "music_volume": DEFAULT_MUSIC_VOLUME * 100,  # Convert to percentage
                    "sfx_volume": DEFAULT_SFX_VOLUME * 100,      # Convert to percentage
                    "fullscreen": False
                }
                # Create the settings file
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Default settings
            self.settings = {
                "music_volume": DEFAULT_MUSIC_VOLUME * 100,
                "sfx_volume": DEFAULT_SFX_VOLUME * 100,
                "fullscreen": False
            }
            
    def save_settings(self):
        """Save current settings to a file."""
        try:
            with open('settings.json', 'w') as f:
                json.dump(self.settings, f, indent=4)
            print("Settings saved successfully")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
            
    def toggle_fullscreen(self, fullscreen=None):
        """Toggle between fullscreen and windowed mode."""
        if fullscreen is None:
            self.fullscreen = not self.settings.get("fullscreen", False)
        else:
            self.fullscreen = fullscreen
            
        self.settings["fullscreen"] = self.fullscreen
            
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        return self.fullscreen

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            
            # Quit
            if event.type == pygame.QUIT:
                self.running = False

            # Change game state
            if self.running:
                if self.state is None:
                    print("ERROR: Game state is None! Switching to default state...")
                    self.change_state(STATE_MENU)  # Switch to a safe default state
                else:
                    self.state.handle_events(events)

    def update(self):
        if self.state is None:
            print("ERROR: Game state is None! Switching to default state...")
            self.change_state(STATE_MENU)  # Switch to a safe default state
            return
            
        self.state.update()

    def render(self):
        self.screen.fill((0, 0, 0))
        if self.state:
            self.state.render(self.screen)
        pygame.display.flip()

    def change_state(self, new_state, **kwargs):
        print(f"Changing state to: {new_state}")
        self.state = StateFactory.create_state(new_state, self, **kwargs)

    def reset_game(self):
        """Reset the game to its initial state."""
        self.player = Player(400, 300)
        self.score = 0
        self.enemies = []
        self.collectibles = []
    
    def run(self):
        """Main game loop."""
        # Start menu music
        self.assets.play_music("menu_music")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()

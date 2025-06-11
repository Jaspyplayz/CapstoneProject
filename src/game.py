import pygame 
import json
import os
from src.characters.characters.player import BasePlayer  # Import your champion classes
from src.characters.characters.ezreal import Ezreal
from src.characters.characters.ashe import Ashe
from src.asset_manager import AssetManager
from src.enemy_manager import EnemyManager  
from src.camera import Camera
from src.game_states import *
from src.constants import (
    GAME_TITLE, MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, STATE_MENU,
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

        # Initialize camera
        self.camera = Camera(MAP_WIDTH, MAP_HEIGHT)

        # Character selection - default to "base"
        self.selected_character = self.settings.get("selected_character", "base")
        
        # Initialize player in the center of the map with selected character
        player_x = MAP_WIDTH // 2
        player_y = MAP_HEIGHT // 2
        self.create_player(player_x, player_y)

        self.assets = AssetManager()
        self.assets.preload_common_assets()
        
        # Load character assets
        self.load_character_assets()
        
        # Load projectile assets
        self.load_projectile_assets()
        
        # Set volumes from settings
        music_volume = self.settings.get("music_volume", DEFAULT_MUSIC_VOLUME * 100) / 100
        sfx_volume = self.settings.get("sfx_volume", DEFAULT_SFX_VOLUME * 100) / 100
        self.assets.set_music_volume(music_volume)
        self.assets.set_sfx_volume(sfx_volume)

        # Initialize game variables
        self.score = 0
        
        # Initialize enemy manager
        self.enemy_manager = EnemyManager(self)
        
        # Load enemy assets
        self.load_enemy_assets()
        
        self.state = StateFactory.create_state(STATE_MENU, self)

    def create_player(self, x, y):
        """Create a player based on the selected character"""
        if self.selected_character == "ezreal":
            self.player = Ezreal(x, y)
        elif self.selected_character == "ashe":
            self.player = Ashe(x, y)
        else:  # Default to base player
            self.player = BasePlayer(x, y)
    
    def set_character(self, character_id):
        """Set the selected character and save to settings"""
        self.selected_character = character_id
        self.settings["selected_character"] = character_id
        self.save_settings()
        
        # Update player with new character
        player_x = self.player.x if hasattr(self, 'player') else MAP_WIDTH // 2
        player_y = self.player.y if hasattr(self, 'player') else MAP_HEIGHT // 2
        self.create_player(player_x, player_y)

    def load_character_assets(self):
        """Load assets for different characters"""
        # Load base character assets
        self.assets.load_image("base_player", "characters/base_player.png")
        self.assets.load_image("base_portrait", "characters/base_portrait.png")
        
        # Load Ezreal assets
        self.assets.load_image("ezreal", "characters/ezreal.png")
        self.assets.load_image("ezreal_portrait", "characters/ezreal_portrait.png")
        self.assets.load_image("ezreal_q", "projectiles/ezreal_q.png")
        self.assets.load_sound("ezreal_q_sound", "characters/ezreal_q.wav")
        
        # Load Ashe assets
        self.assets.load_image("ashe", "characters/ashe.png")
        self.assets.load_image("ashe_portrait", "characters/ashe_portrait.png")
        self.assets.load_image("ashe_q", "projectiles/ashe_q.png")
        self.assets.load_sound("ashe_q_sound", "characters/ashe_q.wav")

    def load_projectile_assets(self):
        """Load projectile-related assets"""
        # Load projectile images (you can create these images)
        self.assets.load_image("projectile", "projectiles/basic_projectile.png")
        
        # Load projectile sounds
        self.assets.load_sound("projectile_fire", "projectiles/fire.wav")
        self.assets.load_sound("projectile_hit", "projectiles/hit.wav")

    def load_enemy_assets(self):
        """Load enemy-related assets"""
        # Load enemy images
        self.assets.load_image("enemy", "enemies/basic_enemy.png")
        self.assets.load_image("fast_enemy", "enemies/fast_enemy.png")
        self.assets.load_image("tank_enemy", "enemies/tank_enemy.png")
        
        # Load enemy sounds
        self.assets.load_sound("enemy_hit", "enemies/hit.wav")
        self.assets.load_sound("enemy_death", "enemies/death.wav")

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
                    "fullscreen": False,
                    "selected_character": "base"  # Default character
                }
                # Create the settings file
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Default settings
            self.settings = {
                "music_volume": DEFAULT_MUSIC_VOLUME * 100,
                "sfx_volume": DEFAULT_SFX_VOLUME * 100,
                "fullscreen": False,
                "selected_character": "base"  # Default character
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
        
        # Update the current game state with delta time
        self.state.update()
        
        # If we're in gameplay state, update camera and check for collisions
        if isinstance(self.state, PlayState):
            # Update camera to follow player
            self.camera.update(
                self.player.x + self.player.width // 2,
                self.player.y + self.player.height // 2,
                SCREEN_WIDTH, SCREEN_HEIGHT
            )
            self.check_projectile_collisions()

    def check_projectile_collisions(self):
        """Check for collisions between projectiles and enemies"""
        # Get active projectiles from player
        projectiles = self.player.get_active_projectiles()
        
        # Check each projectile against each enemy
        for projectile in projectiles:
            if not projectile.active:
                continue
                
            # Create a larger collision rect for more forgiving hit detection
            extended_rect = pygame.Rect(
                projectile.rect.x - 15,  # More generous collision area
                projectile.rect.y - 15,  # More generous collision area
                projectile.rect.width + 30,  # Expanded collision area
                projectile.rect.height + 30  # Expanded collision area
            )
            
            for enemy in self.enemy_manager.enemies:
                if not enemy.alive:
                    continue
                    
                # Check for collision with the extended projectile rect
                if enemy.rect.colliderect(extended_rect):
                    # Projectile hit an enemy
                    enemy_killed = enemy.take_damage(projectile.damage)
                    projectile.active = False  # Deactivate the projectile
                    
                    # Play hit sound
                    self.assets.play_sound("projectile_hit")
                    
                    # Add score if enemy was killed
                    if enemy_killed:
                        self.score += enemy.score_value
                        self.assets.play_sound("enemy_death")
                    else:
                        self.assets.play_sound("enemy_hit")
                    
                    # Break inner loop - one projectile hits one enemy
                    break

    def render(self):
        if self.state:
            self.state.render(self.screen)
        pygame.display.flip()

    def change_state(self, new_state, **kwargs):
        print(f"Changing state to: {new_state}")
        self.state = StateFactory.create_state(new_state, self, **kwargs)

    def reset_game(self):
        """Reset the game to its initial state."""
        # Reset player position to center of map
        player_x = MAP_WIDTH // 2
        player_y = MAP_HEIGHT // 2
        self.create_player(player_x, player_y)  # Use create_player instead of direct assignment
        self.score = 0
        
        # Reset enemy manager
        self.enemy_manager = EnemyManager(self)
    
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

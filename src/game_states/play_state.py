from src.game_states.game_state import GameState
import pygame
from src.constants import STATE_GAME_OVER, SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT

class PlayState(GameState):
    
    def __init__(self, game):
        super().__init__(game)
        self.player = game.player
        
        # Initialize enemy manager
        self.enemy_manager = game.enemy_manager  # Use the game's enemy manager instead of creating a new one
        
        # Game state variables
        self.score = self.game.score
        
        # Optional: Draw a grid to visualize the map
        self.draw_grid = True
        
        # Movement indicator
        self.movement_indicator_active = False
        self.movement_indicator_pos = (0, 0)
        self.movement_indicator_timer = 0
        self.movement_indicator_max_time = 60  # 1 second at 60 FPS
        
        # Character ability configuration
        self.character_abilities = {
            "ezreal": {
                "primary": "mystic_shot",
                "secondary": "essence_flux",
                "movement": "arcane_shift",
                "ultimate": "trueshot_barrage",
                "cooldowns": {
                    "primary": ("q_cooldown", "q_cooldown_max"),
                    "secondary": ("w_cooldown", "w_cooldown_max"),
                    "movement": ("e_cooldown", "e_cooldown_max"),
                    "ultimate": ("r_cooldown", "r_cooldown_max")
                }
            },
            "ashe": {
                "primary": "attack",  # Ashe uses basic attack as primary
                "secondary": "volley",
                "movement": "hawkshot",
                "ultimate": "enchanted_arrow",
                "cooldowns": {
                    "primary": ("attack_cooldown", "attack_cooldown_max"),
                    "secondary": ("volley_cooldown", "volley_cooldown_max"),
                    "movement": ("hawkshot_cooldown", "hawkshot_cooldown_max"),
                    "ultimate": ("ultimate_cooldown", "ultimate_cooldown_max")
                }
            }
        }
        
        # Start gameplay music
        self.game.assets.play_music("gameplay_music")
        
    def handle_events(self, events):
        for event in events:
            # Point and click right click movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right click
                    self._handle_movement()
                elif event.button == 1:  # Left click
                    self._handle_ability("primary")
                

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state("pause", previous_state=self)
                if event.key == pygame.K_d:
                    self._handle_flash()
                if event.key == pygame.K_q:
                    # Q key for primary ability
                    self._handle_ability("primary")
                if event.key == pygame.K_w:
                    # W key for secondary ability
                    self._handle_ability("secondary")
                if event.key == pygame.K_e:
                    # E key for movement ability
                    self._handle_ability("movement")
                if event.key == pygame.K_r:
                    # R key for ultimate ability
                    self._handle_ability("ultimate")
                if event.key == pygame.K_g:
                    # Toggle grid display
                    self.draw_grid = not self.draw_grid
                      
    def _handle_movement(self):
        # Get mouse position in screen coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert to world coordinates
        world_x = mouse_x + self.game.camera.x
        world_y = mouse_y + self.game.camera.y
        
        # Set destination in world coordinates
        self.player.set_destination(world_x, world_y)
        
        # Set movement indicator
        self.movement_indicator_active = True
        self.movement_indicator_pos = (world_x, world_y)
        self.movement_indicator_timer = self.movement_indicator_max_time
    
    def _handle_flash(self):
        # Get mouse position in screen coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert to world coordinates
        world_x = mouse_x + self.game.camera.x
        world_y = mouse_y + self.game.camera.y
        
        flash_success = self.player.flash(world_x, world_y)
        if flash_success:
            # Play flash sound effect if you have one
            self.game.assets.play_sound("flash")
    
    def _handle_ability(self, ability_type):
        """Generic ability handler for any character ability"""
        # Get mouse position in screen coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert to world coordinates
        world_x = mouse_x + self.game.camera.x
        world_y = mouse_y + self.game.camera.y
        
        # Get the current character
        character = self.game.selected_character
        
        # Check if we have ability config for this character
        if character not in self.character_abilities:
            return False
            
        # Get the ability name for this character and ability type
        ability_name = self.character_abilities[character].get(ability_type)
        if not ability_name:
            return False
            
        # Check if player has this ability
        ability_method = getattr(self.player, ability_name, None)
        if not ability_method or not callable(ability_method):
            return False
            
        # Execute the ability
        ability_success = ability_method(world_x, world_y)
        
        # Play sound if successful
        if ability_success:
            # Try character-specific sound first
            sound_key = f"{character}_{ability_type[0]}_sound"  # e.g., "ezreal_p_sound"
            
            # Check if the sound exists before playing it
            if hasattr(self.game.assets, "has_sound") and self.game.assets.has_sound(sound_key):
                self.game.assets.play_sound(sound_key)
            else:
                # Use a generic fallback sound
                self.game.assets.play_sound("projectile_fire")
                
        return ability_success


    def check_collisions(self):
        # Check for collisions between player and enemies
        for enemy in self.enemy_manager.enemies:
            if enemy.alive and self.player.rect.colliderect(enemy.rect):
                # Player takes damage when touching an enemy
                self.player.take_damage(10)
                # Push the player back
                self.player.knockback(enemy.x + enemy.width/2, enemy.y + enemy.height/2)
        
        # Check for projectile collisions with enemies
        self.check_projectile_collisions()

    def check_projectile_collisions(self):
        """Check for collisions between projectiles and enemies"""
        # Get active projectiles from player
        projectiles = self.player.get_active_projectiles()
        
        # Check each projectile against each enemy
        for projectile in projectiles:
            if not projectile.active:
                continue
                
            for enemy in self.enemy_manager.enemies:
                if enemy.alive and projectile.rect.colliderect(enemy.rect):
                    # Projectile hit an enemy
                    enemy_killed = enemy.take_damage(projectile.damage)
                    projectile.active = False  # Deactivate the projectile
                    
                    # Play hit sound
                    self.game.assets.play_sound("projectile_hit")
                    
                    # Add score if enemy was killed
                    if enemy_killed:
                        self.score += enemy.score_value
                        # Update the game's score whenever the local score changes
                        self.game.score = self.score
                        self.game.assets.play_sound("enemy_death")
                    else:
                        self.game.assets.play_sound("enemy_hit")
                    
                    # Break inner loop - one projectile hits one enemy
                    break

    def update(self): 
        # Update player
        self.player.update()
        
        # Keep player within map bounds
        self.player.x = max(0, min(self.player.x, MAP_WIDTH - self.player.width))
        self.player.y = max(0, min(self.player.y, MAP_HEIGHT - self.player.height))
        
        # Update camera to follow player
        self.game.camera.update(
            self.player.x + self.player.width // 2,
            self.player.y + self.player.height // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT
        )
        
        # Update all enemies
        self.enemy_manager.update()
        
        # Check for collisions
        self.check_collisions()
        
        # Update movement indicator
        if self.movement_indicator_timer > 0:
            self.movement_indicator_timer -= 1
        else:
            self.movement_indicator_active = False

        if self.player.health <= 0:
            # Make sure the game score is up to date before changing state
            self.game.score = self.score
            self.game.change_state(STATE_GAME_OVER, score=self.score)

    def render(self, screen):
        # Clear screen
        screen.fill((20, 20, 20))  # Dark background
        
        # Draw grid if enabled
        if self.draw_grid:
            self._draw_grid(screen)
        
        # Draw movement indicator if active
        if self.movement_indicator_active:
            # Get screen position for the indicator
            indicator_screen_x = self.movement_indicator_pos[0] - self.game.camera.x
            indicator_screen_y = self.movement_indicator_pos[1] - self.game.camera.y
            
            # Calculate size and opacity based on remaining time
            size_factor = 1.0 + 0.5 * (self.movement_indicator_timer / self.movement_indicator_max_time)
            opacity = int(200 * (self.movement_indicator_timer / self.movement_indicator_max_time))
            
            # Create a surface with per-pixel alpha
            indicator_size = int(30 * size_factor)
            indicator_surface = pygame.Surface((indicator_size, indicator_size), pygame.SRCALPHA)
            
            # Draw outer circle
            pygame.draw.circle(
                indicator_surface,
                (0, 255, 0, opacity),  # Green with fading opacity
                (indicator_size // 2, indicator_size // 2),
                indicator_size // 2,
                3  # Line width
            )
            
            # Draw X mark inside
            line_width = 2
            margin = indicator_size // 4
            pygame.draw.line(
                indicator_surface,
                (0, 255, 0, opacity),
                (margin, margin),
                (indicator_size - margin, indicator_size - margin),
                line_width
            )
            pygame.draw.line(
                indicator_surface,
                (0, 255, 0, opacity),
                (margin, indicator_size - margin),
                (indicator_size - margin, margin),
                line_width
            )
            
            # Draw the indicator
            screen.blit(
                indicator_surface,
                (indicator_screen_x - indicator_size // 2, indicator_screen_y - indicator_size // 2)
            )
        
        # Draw enemies with camera offset
        for enemy in self.enemy_manager.enemies:
            if enemy.alive:
                # Get camera-adjusted position
                camera_pos = self.game.camera.apply(enemy)
                # Only draw if on screen (with some margin)
                if (-100 <= camera_pos[0] <= SCREEN_WIDTH + 100 and 
                    -100 <= camera_pos[1] <= SCREEN_HEIGHT + 100):
                    # Use the enemy's draw_with_camera method instead of directly blitting
                    enemy.draw_with_camera(screen, camera_pos)
        
        # Draw player with camera offset
        player_pos = self.game.camera.apply(self.player)
        screen.blit(self.player.image, player_pos)
        
        # Draw projectiles with camera offset
        for projectile in self.player.get_active_projectiles():
            if projectile.active:
                # Get camera-adjusted rect
                proj_rect = self.game.camera.apply_rect(projectile.rect)
                # If the projectile has an image, use it; otherwise use a rectangle
                if hasattr(projectile, 'image') and projectile.image:
                    screen.blit(projectile.image, proj_rect)
                else:
                    pygame.draw.rect(screen, projectile.color, proj_rect)
        
        # Draw UI elements (these are in screen coordinates, not world coordinates)
        self._draw_ui(screen)

    
    def _draw_grid(self, screen):
        # Draw a grid to visualize the map
        grid_color = (50, 50, 50)  # Dark gray
        grid_spacing = 200  # Space between grid lines
        
        # Vertical lines
        for x in range(0, MAP_WIDTH, grid_spacing):
            if 0 <= x - self.game.camera.x <= SCREEN_WIDTH:
                pygame.draw.line(screen, grid_color, 
                                (x - self.game.camera.x, 0), 
                                (x - self.game.camera.x, SCREEN_HEIGHT))
        
        # Horizontal lines
        for y in range(0, MAP_HEIGHT, grid_spacing):
            if 0 <= y - self.game.camera.y <= SCREEN_HEIGHT:
                pygame.draw.line(screen, grid_color, 
                                (0, y - self.game.camera.y), 
                                (SCREEN_WIDTH, y - self.game.camera.y))
                                
        # Draw map boundaries
        boundary_color = (100, 100, 255)  # Light blue
        pygame.draw.rect(screen, boundary_color, 
                        pygame.Rect(-self.game.camera.x, -self.game.camera.y, 
                                   MAP_WIDTH, MAP_HEIGHT), 2)
    
    def _draw_ui(self, screen):
        # Example of drawing score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # Draw player health bar
        health_ratio = self.player.health / self.player.max_health
        pygame.draw.rect(screen, (255, 0, 0), (10, 50, 200, 20))
        pygame.draw.rect(screen, (0, 255, 0), (10, 50, 200 * health_ratio, 20))
        
        # Draw ability cooldowns
        self._draw_ability_cooldowns(screen)
        
        # Draw character name
        character_name = self.game.selected_character.capitalize()
        char_text = font.render(f"Character: {character_name}", True, (255, 255, 255))
        screen.blit(char_text, (SCREEN_WIDTH - 250, 10))
            
        # Display current position and map size
        pos_text = font.render(f"Pos: ({int(self.player.x)}, {int(self.player.y)}) | Map: {MAP_WIDTH}x{MAP_HEIGHT}", 
                              True, (200, 200, 200))
        screen.blit(pos_text, (10, SCREEN_HEIGHT - 40))
    
    def _draw_ability_cooldowns(self, screen):
        """Draw cooldown indicators for abilities"""
        # Define ability slots with their display properties
        ability_slots = [
            {"key": "attack_cooldown", "max_key": "attack_cooldown_max", "pos": (10, 80), "color": (200, 200, 0), "label": "Auto"},
            {"pos": (60, 80), "color": (50, 150, 255), "label": "Q", "ability_type": "primary"},
            {"pos": (110, 80), "color": (255, 200, 50), "label": "W", "ability_type": "secondary"},
            {"pos": (160, 80), "color": (100, 200, 255), "label": "E", "ability_type": "movement"},
            {"pos": (210, 80), "color": (255, 100, 50), "label": "R", "ability_type": "ultimate"}
        ]
        
        font = pygame.font.Font(None, 24)
        character = self.game.selected_character
        
        # Draw each ability slot
        for slot in ability_slots:
            cooldown = 0
            cooldown_max = 1
            
            # For auto attack, use direct attribute
            if "key" in slot:
                if hasattr(self.player, slot["key"]):
                    cooldown = getattr(self.player, slot["key"])
                    cooldown_max = getattr(self.player, slot["max_key"])
            # For abilities, use character config
            elif "ability_type" in slot and character in self.character_abilities:
                ability_type = slot["ability_type"]
                if ability_type in self.character_abilities[character]["cooldowns"]:
                    cooldown_key, cooldown_max_key = self.character_abilities[character]["cooldowns"][ability_type]
                    if hasattr(self.player, cooldown_key):
                        cooldown = getattr(self.player, cooldown_key)
                        cooldown_max = getattr(self.player, cooldown_max_key)
            
            # Draw cooldown indicator if ability is on cooldown
            if cooldown > 0:
                cooldown_ratio = 1 - (cooldown / cooldown_max)
                x, y = slot["pos"]
                
                # Draw background
                pygame.draw.rect(screen, (100, 100, 100), (x, y, 40, 40))
                # Draw fill based on cooldown
                pygame.draw.rect(screen, slot["color"], (x, y, 40, 40 * cooldown_ratio))
                
                # Draw label
                text = font.render(slot["label"], True, (255, 255, 255))
                text_x = x + (40 - text.get_width()) // 2
                text_y = y + (40 - text.get_height()) // 2
                screen.blit(text, (text_x, text_y))

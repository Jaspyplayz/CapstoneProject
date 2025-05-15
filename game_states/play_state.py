from game_states.game_state import GameState
import pygame
from src.constants import STATE_GAME_OVER, SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT
from src.enemy_manager import EnemyManager  # Import the EnemyManager class

class PlayState(GameState):
    
    def __init__(self, game):
        super().__init__(game)
        self.player = game.player
        
        # Initialize enemy manager
        self.enemy_manager = EnemyManager(self.game)
        
        # Load enemy-related sounds
        self.game.assets.load_sound("enemy_hit", "enemies/hit.wav")
        self.game.assets.load_sound("enemy_death", "enemies/death.wav")
        
        # Load projectile-related sounds
        self.game.assets.load_sound("projectile_fire", "projectiles/fire.wav")
        self.game.assets.load_sound("projectile_hit", "projectiles/hit.wav")
        
        # Game state variables
        self.score = self.game.score
        
        # Optional: Draw a grid to visualize the map
        self.draw_grid = True
        
        # Movement indicator
        self.movement_indicator_active = False
        self.movement_indicator_pos = (0, 0)
        self.movement_indicator_timer = 0
        self.movement_indicator_max_time = 60  # 1 second at 60 FPS
        
    def handle_events(self, events):
        for event in events:
            # Point and click right click movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self._handle_movement()
                

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state("pause", previous_state=self)
                if event.key == pygame.K_d:
                    self._handle_flash()
                if event.key == pygame.K_q:
                    # Left click for projectile attack
                    self._handle_attack()
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
            # self.game.assets.play_sound("flash")
            pass
    
    def _handle_attack(self):
        # Get mouse position in screen coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert to world coordinates
        world_x = mouse_x + self.game.camera.x
        world_y = mouse_y + self.game.camera.y
        
        # Try to fire a projectile
        attack_success = self.player.attack(world_x, world_y)
        
        # Play sound if attack was successful (not on cooldown)
        if attack_success:
            self.game.assets.play_sound("projectile_fire")

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
        
        # Draw attack cooldown indicator
        if self.player.attack_cooldown > 0:
            cooldown_ratio = 1 - (self.player.attack_cooldown / self.player.attack_cooldown_max)
            pygame.draw.rect(screen, (100, 100, 100), (10, 80, 200, 10))
            pygame.draw.rect(screen, (200, 200, 0), (10, 80, 200 * cooldown_ratio, 10))
            
        # Display current position and map size
        pos_text = font.render(f"Pos: ({int(self.player.x)}, {int(self.player.y)}) | Map: {MAP_WIDTH}x{MAP_HEIGHT}", 
                              True, (200, 200, 200))
        screen.blit(pos_text, (10, SCREEN_HEIGHT - 40))

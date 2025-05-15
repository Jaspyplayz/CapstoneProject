from game_states.game_state import GameState
import pygame
from src.constants import STATE_GAME_OVER
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
        
    def handle_events(self, events):
        for event in events:
            # Point and click right click movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self._handle_movement()
                

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state("pause", previous_state=self)
                if event.key == pygame.K_d:
                    self._handle_flash()
                if event.key == pygame.K_q:
                    # Left click for projectile attack
                    self._handle_attack()
                      
    def _handle_movement(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.player.set_destination(mouse_x, mouse_y)
    
    def _handle_flash(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        flash_success = self.player.flash(mouse_x, mouse_y)
        if flash_success:
            # Play flash sound effect if you have one
            # self.game.assets.play_sound("flash")
            pass
    
    def _handle_attack(self):
        # Get mouse position for attack direction
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Try to fire a projectile
        attack_success = self.player.attack(mouse_x, mouse_y)
        
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
        
        # Update all enemies
        self.enemy_manager.update()
        
        # Check for collisions
        self.check_collisions()

        if self.player.health <= 0:
            # Make sure the game score is up to date before changing state
            self.game.score = self.score
            self.game.change_state(STATE_GAME_OVER, score=self.score)

    def render(self, screen):
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw player
        self.player.draw(screen)
        
        # Draw all enemies
        self.enemy_manager.draw(screen)
        
        # Draw UI elements like score, health bar, etc.
        self._draw_ui(screen)
    
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

# Enemy.py
import pygame
import random
import math
from src.constants import MAP_WIDTH, MAP_HEIGHT, RED, GREEN

class Enemy:
    def __init__(self, game, speed, health, x=None, y=None):
        self.game = game

        # Enemy properties
        self.speed = speed
        self.health = health
        self.max_health = health
        self.detection_radius = 250
        self.score_value = 100

        # Load enemy image first so we can set width/height based on it
        self.image = self.game.assets.load_image("enemy", "enemies/basic_enemy.jpg")
        
        # Set width and height based on the actual image dimensions
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Enemy coordinate spawnpoint - now using MAP dimensions instead of SCREEN dimensions
        self.x = x if x is not None else random.randint(0, MAP_WIDTH - self.width)
        self.y = y if y is not None else random.randint(0, MAP_HEIGHT - self.height)
        
        # Create hitbox that matches the visual sprite exactly
        self.rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )
        
        # Create a mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)

        # Movement vectors
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = random.uniform(0, 2 * math.pi)
        self.set_velocity_from_angle()

        # Direction change timer
        self.direction_change_timer = 0
        self.direction_change_delay = random.randint(60, 120)

        # Sound effects
        self.hit_sound = "enemy_hit"
        self.death_sound = "enemy_death"

        # State
        self.alive = True
        self.debug_mode = False
        
        # Hit effect
        self.hit_flash = 0
        self.hit_flash_duration = 5
    
    def set_velocity_from_angle(self):
        self.velocity_x = math.cos(self.angle) * self.speed
        self.velocity_y = math.sin(self.angle) * self.speed

    def update(self):
        if not self.alive:
            return 
        
        # Update hit flash effect
        if self.hit_flash > 0:
            self.hit_flash -= 1
        
        # Check if player is within detection radius
        player_x = self.game.player.x + self.game.player.width/2
        player_y = self.game.player.y + self.game.player.height/2
        
        dx = player_x - (self.x + self.width/2)
        dy = player_y - (self.y + self.height/2)
        distance_to_player = math.sqrt(dx*dx + dy*dy)
        
        # If player is close, seek them
        if distance_to_player < self.detection_radius:
            aggression = 0.3 + (1 - distance_to_player / self.detection_radius) * 0.4
            self.seek_player(player_x, player_y, aggression)
        else:
            # Handle direction changes
            self.direction_change_timer += 1
            if self.direction_change_timer >= self.direction_change_delay:
                self.change_direction()
                self.direction_change_timer = 0

        # Move based on velocity
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Boundary handling - now using MAP dimensions
        if self.x < 0:
            self.x = 0
            self.bounce_horizontal()
        elif self.x > MAP_WIDTH - self.width:
            self.x = MAP_WIDTH - self.width
            self.bounce_horizontal()

        if self.y < 0:
            self.y = 0
            self.bounce_vertical()
        elif self.y > MAP_HEIGHT - self.height:
            self.y = MAP_HEIGHT - self.height
            self.bounce_vertical()

        # Update hitbox position
        self.update_hitbox()

    def update_hitbox(self):
        """Update the hitbox position based on the enemy's position"""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def bounce_horizontal(self):
        self.angle = math.pi - self.angle
        self.set_velocity_from_angle()
    
    def bounce_vertical(self):
        self.angle = -self.angle
        self.set_velocity_from_angle()

    def change_direction(self):
        self.angle = random.uniform(0, 2 * math.pi)
        self.set_velocity_from_angle()
        self.direction_change_delay = random.randint(60, 120)

    def seek_player(self, player_x, player_y, aggression=0.5):
        dx = player_x - (self.x + self.width/2)
        dy = player_y - (self.y + self.height/2)
        angle_to_player = math.atan2(dy, dx)

        # Blend current angle with angle to player based on aggression
        self.angle = (1-aggression) * self.angle + aggression * angle_to_player
        
        # Add slight randomness to movement
        self.angle += random.uniform(-0.3, 0.3)
        self.set_velocity_from_angle()

    def take_damage(self, amount):
        """
        Apply damage to the enemy
        Returns True if the enemy died, False otherwise
        """
        if not self.alive:
            return False
        
        self.health -= amount
        self.hit_flash = self.hit_flash_duration
        
        # Play hit sound
        if hasattr(self.game, 'assets'):
            self.game.assets.play_sound(self.hit_sound)

        if self.health <= 0:
            self.die()
            return True
        return False

    def die(self):
        """Handle enemy death"""
        self.alive = False
        
        # Play death sound
        if hasattr(self.game, 'assets'):
            self.game.assets.play_sound(self.death_sound)

    def draw(self, surface):
        if not self.alive:
            return
        
        # Create a copy of the image for hit flash effect
        current_image = self.image.copy() if self.hit_flash == 0 else self.create_hit_effect()
        
        # Draw enemy - this method is used when not using camera
        surface.blit(current_image, (int(self.x), int(self.y)))

        # Draw health bar
        health_bar_width = self.width - 10
        health_ratio = max(0, self.health / self.max_health)

        # Health bar background
        pygame.draw.rect(surface, RED, 
                        (int(self.x) + 5, int(self.y) - 10, health_bar_width, 5))
        
        # Health bar foreground
        pygame.draw.rect(surface, GREEN, 
                        (int(self.x) + 5, int(self.y) - 10, int(health_bar_width * health_ratio), 5))
        
        # Debug: Draw hitbox if debug mode is enabled
        if self.debug_mode:
            pygame.draw.rect(surface, (255, 0, 255), self.rect, 1)
    
    def draw_with_camera(self, surface, camera_pos):
        """Draw the enemy with camera offset"""
        if not self.alive:
            return
        
        # Create a copy of the image for hit flash effect
        current_image = self.image.copy() if self.hit_flash == 0 else self.create_hit_effect()
        
        # Draw enemy at camera position
        surface.blit(current_image, camera_pos)

        # Draw health bar with camera offset
        health_bar_width = self.width - 10
        health_ratio = max(0, self.health / self.max_health)

        # Health bar background
        pygame.draw.rect(surface, RED, 
                        (camera_pos[0] + 5, camera_pos[1] - 10, health_bar_width, 5))
        
        # Health bar foreground
        pygame.draw.rect(surface, GREEN, 
                        (camera_pos[0] + 5, camera_pos[1] - 10, int(health_bar_width * health_ratio), 5))
        
        # Debug: Draw hitbox if debug mode is enabled
        if self.debug_mode:
            # Create a new rect at the camera position with same dimensions
            debug_rect = pygame.Rect(camera_pos[0], camera_pos[1], self.rect.width, self.rect.height)
            pygame.draw.rect(surface, (255, 0, 255), debug_rect, 1)
    
    def create_hit_effect(self):
        """Create a white flash effect when enemy is hit"""
        # Create a surface the same size as the enemy
        flash_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # First draw the original enemy image
        flash_image.blit(self.image, (0, 0))
        
        # Create a white overlay with transparency
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 150))  # White with alpha (0-255)
        
        # Apply the overlay to our new surface
        flash_image.blit(overlay, (0, 0))
        
        return flash_image

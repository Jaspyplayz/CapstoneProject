# src/projectile.py
import pygame
import math
from src.constants import RED, GREEN, MAP_WIDTH, MAP_HEIGHT, FLASH_COOLDOWN

class Projectile:
    def __init__(self, x, y, target_x, target_y, speed=10, damage=25, range=400):
        self.x = x
        self.y = y
        self.start_x = x  # Store starting position for range calculation
        self.start_y = y
        self.width = 10
        self.height = 10
        self.color = (0, 200, 255)  # Cyan color for projectiles
        self.damage = damage
        self.speed = speed
        self.range = range
        self.distance_traveled = 0
        self.active = True
        self.piercing = False  # Whether the projectile pierces through enemies
        self.image = None  # Can be set to use an image instead of a rectangle
        
        # For projectiles that expire after a certain time
        self.lifetime = None
        self.time_alive = 0
        
        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = max(1, math.hypot(dx, dy))  # Avoid division by zero
        self.velocity_x = (dx / distance) * speed
        self.velocity_y = (dy / distance) * speed
        
        # Store previous position for continuous collision detection
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Create proper rect for collision detection
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def update(self):
        if not self.active:
            return
            
        # Store previous position for continuous collision detection
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Move projectile
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Calculate distance traveled this frame
        frame_distance = math.hypot(self.velocity_x, self.velocity_y)
        self.distance_traveled += frame_distance
        
        # Update lifetime if set
        if self.lifetime is not None:
            self.time_alive += 1
            if self.time_alive >= self.lifetime:
                self.active = False
        
        # Check if projectile is out of range or out of map bounds
        if (self.distance_traveled >= self.range or 
            self.x < 0 or self.x > MAP_WIDTH or 
            self.y < 0 or self.y > MAP_HEIGHT):
            self.active = False
    
    def draw(self, screen):
        if not self.active:
            return
        
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            
        # Optional: Draw a trail
        trail_length = min(30, int(self.distance_traveled))
        if trail_length > 0:
            trail_x = self.x - self.velocity_x * (trail_length / self.speed)
            trail_y = self.y - self.velocity_y * (trail_length / self.speed)
            pygame.draw.line(screen, (0, 100, 200), 
                           (self.x + self.width/2, self.y + self.height/2),
                           (trail_x + self.width/2, trail_y + self.height/2), 3)
    
    def draw_with_camera(self, surface, camera_pos):
        """Draw the projectile with camera offset"""
        if not self.active:
            return
        
        # Draw projectile at camera-adjusted position
        camera_rect = pygame.Rect(camera_pos[0], camera_pos[1], self.width, self.height)
        
        if self.image:
            surface.blit(self.image, camera_rect)
        else:
            pygame.draw.rect(surface, self.color, camera_rect)
        
        # Draw trail with camera offset
        trail_length = min(30, int(self.distance_traveled))
        if trail_length > 0:
            # Calculate trail position in world coordinates
            trail_x = self.x - self.velocity_x * (trail_length / self.speed)
            trail_y = self.y - self.velocity_y * (trail_length / self.speed)
            
            # Convert to camera coordinates
            trail_camera_x = camera_pos[0] + (trail_x - self.x)
            trail_camera_y = camera_pos[1] + (trail_y - self.y)
            
            # Draw the trail line
            trail_color = (0, 100, 200)
            
            # Special trail colors for Ezreal abilities
            if self.color == (50, 150, 255):  # Q - Mystic Shot
                trail_color = (20, 100, 255)
            elif self.color == (255, 200, 50):  # W - Essence Flux
                trail_color = (200, 150, 20)
            elif self.color == (255, 100, 50):  # R - Trueshot Barrage
                trail_color = (255, 50, 0)
                
            pygame.draw.line(surface, trail_color, 
                           (camera_pos[0] + self.width/2, camera_pos[1] + self.height/2),
                           (trail_camera_x + self.width/2, trail_camera_y + self.height/2), 
                           3 if not self.piercing else 5)  # Thicker trail for piercing projectiles

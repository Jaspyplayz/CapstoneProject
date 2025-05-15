import pygame
import math
from src.constants import RED, GREEN, FLASH_COOLDOWN, SCREEN_WIDTH, SCREEN_HEIGHT

class Projectile:
    def __init__(self, x, y, target_x, target_y, speed=10, damage=25, range=400):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 10
        self.color = (0, 200, 255)  # Cyan color for projectiles
        self.damage = damage
        self.speed = speed
        self.range = range
        self.distance_traveled = 0
        self.active = True
        
        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = max(1, math.hypot(dx, dy))  # Avoid division by zero
        self.velocity_x = (dx / distance) * speed
        self.velocity_y = (dy / distance) * speed
    
    def update(self):
        if not self.active:
            return
            
        # Move projectile
        prev_x, prev_y = self.x, self.y
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Calculate distance traveled this frame
        frame_distance = math.hypot(self.x - prev_x, self.y - prev_y)
        self.distance_traveled += frame_distance
        
        # Check if projectile is out of range or out of bounds
        if (self.distance_traveled >= self.range or 
            self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.active = False
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        if not self.active:
            return
            
        pygame.draw.rect(screen, self.color, self.rect)
        # Optional: Draw a trail
        trail_length = min(30, int(self.distance_traveled))
        if trail_length > 0:
            trail_x = self.x - self.velocity_x * (trail_length / self.speed)
            trail_y = self.y - self.velocity_y * (trail_length / self.speed)
            pygame.draw.line(screen, (0, 100, 200), 
                           (self.x + self.width/2, self.y + self.height/2),
                           (trail_x + self.width/2, trail_y + self.height/2), 3)

class BasePlayer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = RED
        self.speed = 5
        self.flash_range = 200  

        # Movement system
        self.target_x = None 
        self.target_y = None
        self.moving = False

        # Health Attribute
        self.health = 100
        self.max_health = 100

        # Cooldown system
        self.flash_cooldown = 0  # Start with ability ready
        self.flash_cooldown_max = FLASH_COOLDOWN
        
        # Attack attributes
        self.attack_damage = 25
        self.attack_cooldown = 0
        self.attack_cooldown_max = 15  # 4 attacks per second at 60 FPS
        self.projectiles = []  # List to store active projectiles

    def set_destination(self, x, y):
        """Improved with boundary checking"""
        self.target_x = x
        self.target_y = y
        self.moving = True

    def update(self):
        """Optimized movement and cooldown logic with boundary checking"""
        # Update cooldowns first
        if self.flash_cooldown > 0:
            self.flash_cooldown -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Movement processing
        if self.moving and self.target_x is not None and self.target_y is not None:
            center_x = self.x + self.width/2
            center_y = self.y + self.height/2
            dx = self.target_x - center_x
            dy = self.target_y - center_y
            distance = math.hypot(dx, dy)

            if distance < self.speed:
                # Snap to target when close
                new_x = self.target_x - self.width/2
                new_y = self.target_y - self.height/2
                
                # Apply boundary constraints
                new_x = self.constrain_position_x(new_x)
                new_y = self.constrain_position_y(new_y)
                
                self.x = new_x
                self.y = new_y
                self.moving = False
                self.target_x = None
                self.target_y = None
            else:
                # Calculate new position with normalized movement vector
                new_x = self.x + (dx/distance) * self.speed
                new_y = self.y + (dy/distance) * self.speed
                
                # Apply boundary constraints
                new_x = self.constrain_position_x(new_x)
                new_y = self.constrain_position_y(new_y)
                
                # If we hit a boundary, stop moving
                if new_x == 0 or new_x == SCREEN_WIDTH - self.width or new_y == 0 or new_y == SCREEN_HEIGHT - self.height:
                    self.moving = False
                    self.target_x = None
                    self.target_y = None
                
                self.x = new_x
                self.y = new_y

        # Update projectiles
        for projectile in self.projectiles[:]:  # Create a copy to safely remove items
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)

    def constrain_position_x(self, x):
        """Keep x position within screen bounds"""
        return max(0, min(SCREEN_WIDTH - self.width, x))
    
    def constrain_position_y(self, y):
        """Keep y position within screen bounds"""
        return max(0, min(SCREEN_HEIGHT - self.height, y))

    def flash(self, mouse_x, mouse_y):
        """Flash toward mouse position, limited by maximum range"""
        if self.flash_cooldown > 0:
            return False

        # Calculate player center position
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        # Calculate direction vector to mouse
        dx = mouse_x - center_x
        dy = mouse_y - center_y
        distance = math.hypot(dx, dy)
        
        # Determine target position based on range
        if distance <= self.flash_range:
            # Mouse is within range, flash directly to it
            target_x = mouse_x
            target_y = mouse_y
        else:
            # Mouse is beyond range, flash to maximum range in that direction
            angle = math.atan2(dy, dx)
            target_x = center_x + math.cos(angle) * self.flash_range
            target_y = center_y + math.sin(angle) * self.flash_range
        
        # Clear movement state
        self.moving = False
        self.target_x = None
        self.target_y = None

        # Calculate new position (centered on target) with boundary constraints
        new_x = target_x - self.width/2
        new_y = target_y - self.height/2
        
        # Apply boundary constraints
        self.x = self.constrain_position_x(new_x)
        self.y = self.constrain_position_y(new_y)

        # Activate cooldown
        self.flash_cooldown = self.flash_cooldown_max
        return True

    
    def take_damage(self, amount):
        """Handle player taking damage"""
        self.health = max(0, self.health - amount)
        return self.health <= 0  # Returns True if player died

    def heal(self, amount):
        """Handle player healing"""
        self.health = min(self.max_health, self.health + amount)
    
    def attack(self, target_x, target_y):
        """Fire a projectile toward the target position"""
        if self.attack_cooldown > 0:
            return False
            
        # Calculate projectile starting position (center of player)
        start_x = self.x + self.width/2 - 5  # Center and adjust for projectile size
        start_y = self.y + self.height/2 - 5
        
        # Create and add the projectile
        projectile = Projectile(
            start_x, 
            start_y, 
            target_x, 
            target_y,
            speed=15,
            damage=self.attack_damage
        )
        self.projectiles.append(projectile)
        
        # Set cooldown
        self.attack_cooldown = self.attack_cooldown_max
        return True
    
    def get_active_projectiles(self):
        """Return list of active projectiles for collision detection"""
        return [p for p in self.projectiles if p.active]
        
    def knockback(self, source_x, source_y):
        """Push player away from damage source with boundary checking"""
        # Calculate direction vector from source to player
        """
        dx = (self.x + self.width/2) - source_x
        dy = (self.y + self.height/2) - source_y
        
        # Normalize and apply knockback
        distance = max(1, math.hypot(dx, dy))  # Avoid division by zero
        knockback_strength = 0
        
        new_x = self.x + (dx / distance) * knockback_strength
        new_y = self.y + (dy / distance) * knockback_strength
        
        # Apply boundary constraints
        self.x = self.constrain_position_x(new_x)
        self.y = self.constrain_position_y(new_y)
        
        # Reset movement target when knocked back
        self.moving = False
        self.target_x = None
        self.target_y = None
        """
        pass

    @property
    def rect(self):
        """Return a pygame Rect representing the player's position"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        """Enhanced drawing with cooldown visualization and projectiles"""
        # Draw player rectangle
        pygame.draw.rect(screen, self.color, 
                        (self.x, self.y, self.width, self.height))

        # Draw movement path
        if self.moving and self.target_x is not None and self.target_y is not None:
            start_pos = (self.x + self.width/2, self.y + self.height/2)
            pygame.draw.line(screen, GREEN, start_pos, 
                           (self.target_x, self.target_y), 2)

        # Visualize flash cooldown 
        if self.flash_cooldown > 0:
            cooldown_ratio = 1 - (self.flash_cooldown / self.flash_cooldown_max)
            radius = int(25 * cooldown_ratio)
            center = (int(self.x + self.width/2), int(self.y + self.height/2))
            pygame.draw.circle(screen, (200, 200, 200, 150), center, radius, 2)
            
        # Draw all projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)

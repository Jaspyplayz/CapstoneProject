import pygame
import math
from src.constants import RED, GREEN, MAP_WIDTH, MAP_HEIGHT, FLASH_COOLDOWN
from src.projectile import Projectile

class BasePlayer:
    def __init__(self, x, y, image_path=None):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = RED
        self.speed = 5
        self.flash_range = 200  

        # Image loading
        self.image = None
        if image_path:
            try:
                # Try to load the image from the provided path
                self.image = pygame.image.load(image_path).convert_alpha()
                # Scale the image to match the player size
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Error loading image: {e}")
                # Fallback to colored surface if image loading fails
                self.image = pygame.Surface((self.width, self.height))
                self.image.fill(self.color)
        else:
            # No image path provided, use colored surface
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(self.color)

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
        
        # Visual effects system
        self.visual_effects = []  # List to store visual effects

    def set_destination(self, x, y):
        """Set destination in world coordinates"""
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
                if new_x == 0 or new_x == MAP_WIDTH - self.width or new_y == 0 or new_y == MAP_HEIGHT - self.height:
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
                
        # Update visual effects
        for effect in self.visual_effects[:]:
            effect['duration'] -= 1
            if effect['duration'] <= 0:
                self.visual_effects.remove(effect)

    def constrain_position_x(self, x):
        """Keep x position within map bounds"""
        return max(0, min(MAP_WIDTH - self.width, x))
    
    def constrain_position_y(self, y):
        """Keep y position within map bounds"""
        return max(0, min(MAP_HEIGHT - self.height, y))

    def flash(self, mouse_x, mouse_y):
        """Flash toward mouse position, limited by maximum range"""
        if self.flash_cooldown > 0:
            return False

        # Store original position for visual effect
        original_x = self.x
        original_y = self.y

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
        
        # Create flash visual effect (yellow)
        self.create_flash_effect(original_x, original_y, self.x, self.y)

        # Activate cooldown
        self.flash_cooldown = self.flash_cooldown_max
        return True
    
    def create_flash_effect(self, start_x, start_y, end_x, end_y):
        """Create visual effect for Flash ability"""
        # Create start effect (disappearing from original position)
        self.visual_effects.append({
            'type': 'flash_start',
            'x': start_x + self.width/2,
            'y': start_y + self.height/2,
            'radius': 30,
            'color': (255, 255, 0),  # Yellow for flash
            'duration': 15,
            'max_duration': 15
        })
        
        # Create end effect (appearing at new position)
        self.visual_effects.append({
            'type': 'flash_end',
            'x': end_x + self.width/2,
            'y': end_y + self.height/2,
            'radius': 30,
            'color': (255, 255, 0),  # Yellow for flash
            'duration': 15,
            'max_duration': 15
        })
    
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
        # Knockback functionality is commented out in the original code
        pass

    @property
    def rect(self):
        """Return a pygame Rect representing the player's position"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        """Enhanced drawing with image, cooldown visualization and projectiles"""
        # Draw player image instead of rectangle
        screen.blit(self.image, (self.x, self.y))

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
            
        # Draw flash visual effects
        self.draw_flash_effects(screen)
    
    def draw_flash_effects(self, screen):
        """Draw flash visual effects"""
        for effect in self.visual_effects:
            if effect['type'] in ('flash_start', 'flash_end'):
                # Calculate fade-out alpha
                alpha = int(255 * (effect['duration'] / effect['max_duration']))
                
                # Calculate expanding/contracting radius
                if effect['type'] == 'flash_start':
                    # Start small and expand
                    progress = 1 - (effect['duration'] / effect['max_duration'])
                    radius = int(effect['radius'] * (0.5 + progress * 0.5))
                else:  # flash_end
                    # Start large and contract
                    progress = effect['duration'] / effect['max_duration']
                    radius = int(effect['radius'] * (0.5 + progress * 0.5))
                
                # Create a surface with per-pixel alpha
                s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                color_with_alpha = (*effect['color'], alpha)
                
                # Draw circle with fading opacity
                pygame.draw.circle(s, color_with_alpha, (radius, radius), radius, 2)
                
                # Draw to screen
                screen.blit(s, (effect['x'] - radius, effect['y'] - radius))
    
    def draw_with_camera(self, surface, camera_rect):
        """Draw player with camera offset"""
        # Draw player image at camera position
        surface.blit(self.image, (camera_rect.x, camera_rect.y))

        # Draw movement path if active
        if self.moving and self.target_x is not None and self.target_y is not None:
            # Convert world coordinates to screen coordinates
            start_pos = (camera_rect.x + self.width/2, camera_rect.y + self.height/2)
            
            # Calculate target position on screen
            target_screen_x = camera_rect.x + (self.target_x - self.x)
            target_screen_y = camera_rect.y + (self.target_y - self.y)
            
            pygame.draw.line(surface, GREEN, start_pos, 
                           (target_screen_x, target_screen_y), 2)

        # Visualize flash cooldown with camera offset
        if self.flash_cooldown > 0:
            cooldown_ratio = 1 - (self.flash_cooldown / self.flash_cooldown_max)
            radius = int(25 * cooldown_ratio)
            center = (int(camera_rect.x + self.width/2), int(camera_rect.y + self.height/2))
            pygame.draw.circle(surface, (200, 200, 200, 150), center, radius, 2)
            
        # Draw all projectiles with camera offset
        for projectile in self.projectiles:
            if projectile.active:
                # Calculate projectile's position relative to the camera
                proj_camera_x = camera_rect.x + (projectile.x - self.x)
                proj_camera_y = camera_rect.y + (projectile.y - self.y)
                projectile.draw_with_camera(surface, (proj_camera_x, proj_camera_y))
                
        # Draw flash effects with camera offset
        self.draw_flash_effects_with_camera(surface, camera_rect)
    
    def draw_flash_effects_with_camera(self, surface, camera_rect):
        """Draw flash visual effects with camera offset"""
        for effect in self.visual_effects:
            if effect['type'] in ('flash_start', 'flash_end'):
                # Calculate fade-out alpha
                alpha = int(255 * (effect['duration'] / effect['max_duration']))
                
                # Calculate expanding/contracting radius
                if effect['type'] == 'flash_start':
                    # Start small and expand
                    progress = 1 - (effect['duration'] / effect['max_duration'])
                    radius = int(effect['radius'] * (0.5 + progress * 0.5))
                else:  # flash_end
                    # Start large and contract
                    progress = effect['duration'] / effect['max_duration']
                    radius = int(effect['radius'] * (0.5 + progress * 0.5))
                
                # Calculate effect's position relative to the camera
                effect_camera_x = camera_rect.x + (effect['x'] - self.x)
                effect_camera_y = camera_rect.y + (effect['y'] - self.y)
                
                # Create a surface with per-pixel alpha
                s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                color_with_alpha = (*effect['color'], alpha)
                
                pygame.draw.circle(s, color_with_alpha, (radius, radius), radius, 2)
                
                # Draw to screen
                surface.blit(s, (effect_camera_x - radius, effect_camera_y - radius))

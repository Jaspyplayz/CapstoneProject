# src/characters/ashe.py
import pygame
import math
from .player import BasePlayer
from src.projectile import Projectile

class Ashe(BasePlayer):
    def __init__(self, x, y):
        # Call the parent class constructor first
        super().__init__(x, y)
        
        # Override default attributes
        self.color = (150, 200, 255)  # Ice blue color for Ashe
        self.attack_damage = 25
        self.attack_cooldown_max = 15  # Slightly slower attack speed than Ezreal
        self.speed = 5  # Standard movement speed
        
        # Ashe-specific attributes
        self.projectiles = []  # List to store active projectiles
        self.slowed_enemies = []  # List to store enemies slowed by frost
        
        # Q - Frost Shot (passive: basic attacks slow)
        self.frost_slow_amount = 0.3  # 30% slow
        self.frost_slow_duration = 120  # 2 seconds at 60 FPS
        
        # W - Volley (multiple arrows in a cone)
        self.volley_cooldown = 0
        self.volley_cooldown_max = 60  # 1 second at 60 FPS
        self.volley_damage = 40
        self.volley_range = 800
        self.volley_arrows = 7  # Number of arrows in volley
        
        # E - Hawkshot (vision ability)
        self.hawkshot_cooldown = 0
        self.hawkshot_cooldown_max = 240  # 4 seconds at 60 FPS
        self.hawkshot_range = 1500
        self.hawkshot_duration = 300  # 5 seconds at 60 FPS
        self.hawkshot_active = False
        self.hawkshot_pos = (0, 0)
        self.hawkshot_timer = 0
        
        # R - Enchanted Crystal Arrow
        self.ultimate_cooldown = 0
        self.ultimate_cooldown_max = 480  # 8 seconds at 60 FPS
        self.ultimate_damage = 200
        self.ultimate_range = 2000
        self.ultimate_stun_duration = 180  # 3 seconds at 60 FPS
        
        # Flash (from BasePlayer)
        self.flash_cooldown = 0
        self.flash_cooldown_max = 300  # 5 seconds at 60 FPS
        self.flash_range = 600
        
        # Update the image with the new color
        self.image.fill(self.color)
    
    def update(self):
        # Update base player functionality
        super().update()
        
        # Update Ashe-specific cooldowns
        if self.volley_cooldown > 0:
            self.volley_cooldown -= 1
        if self.hawkshot_cooldown > 0:
            self.hawkshot_cooldown -= 1
        if self.ultimate_cooldown > 0:
            self.ultimate_cooldown -= 1
            
        # Update projectiles
        for projectile in self.projectiles[:]:  # Create a copy to safely remove items
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)
        
        # Update slowed enemies (decrease duration)
        for slow in self.slowed_enemies[:]:
            slow['duration'] -= 1
            if slow['duration'] <= 0:
                self.slowed_enemies.remove(slow)
                
        # Update hawkshot
        if self.hawkshot_active:
            self.hawkshot_timer -= 1
            if self.hawkshot_timer <= 0:
                self.hawkshot_active = False
    
    def attack(self, target_x, target_y):
        """Basic attack - Frost Shot (applies slow)"""
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
        projectile.color = (200, 230, 255)  # Ice blue arrow
        projectile.is_frost_arrow = True  # Special flag for frost effect
        self.projectiles.append(projectile)
        
        # Set cooldown
        self.attack_cooldown = self.attack_cooldown_max
        return True
    
    def volley(self, target_x, target_y):
        """W ability - Volley: Fires multiple arrows in a cone"""
        if self.volley_cooldown > 0:
            return False
            
        # Calculate projectile starting position
        start_x = self.x + self.width/2 - 5
        start_y = self.y + self.height/2 - 5
        
        # Calculate direction vector to target
        dx = target_x - start_x
        dy = target_y - start_y
        base_angle = math.atan2(dy, dx)
        
        # Create multiple arrows in a cone pattern
        for i in range(self.volley_arrows):
            # Calculate spread angle (-30 to +30 degrees)
            spread = (i / (self.volley_arrows - 1)) * 60 - 30
            spread_rad = math.radians(spread)
            
            # Calculate new angle with spread
            angle = base_angle + spread_rad
            
            # Calculate new target point
            arrow_range = self.volley_range
            arrow_target_x = start_x + math.cos(angle) * arrow_range
            arrow_target_y = start_y + math.sin(angle) * arrow_range
            
            # Create arrow projectile
            arrow = Projectile(
                start_x, 
                start_y, 
                arrow_target_x, 
                arrow_target_y,
                speed=18,
                damage=self.volley_damage,
                range=self.volley_range
            )
            
            # Make volley arrow visually distinct
            arrow.color = (180, 220, 255)  # Light blue
            arrow.width = 10
            arrow.height = 10
            arrow.rect = pygame.Rect(int(arrow.x), int(arrow.y), 
                                    arrow.width, arrow.height)
            arrow.is_frost_arrow = True  # Apply frost effect
            
            self.projectiles.append(arrow)
        
        # Set cooldown
        self.volley_cooldown = self.volley_cooldown_max
        return True
    
    def hawkshot(self, target_x, target_y):
        """E ability - Hawkshot: Reveals an area"""
        if self.hawkshot_cooldown > 0:
            return False
        
        # Calculate direction vector to target
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        dx = target_x - center_x
        dy = target_y - center_y
        distance = math.hypot(dx, dy)
        
        # Determine hawkshot position (limit to range)
        if distance <= self.hawkshot_range:
            hawkshot_x = target_x
            hawkshot_y = target_y
        else:
            # Target is beyond range, place at maximum range in that direction
            angle = math.atan2(dy, dx)
            hawkshot_x = center_x + math.cos(angle) * self.hawkshot_range
            hawkshot_y = center_y + math.sin(angle) * self.hawkshot_range
        
        # Create a hawkshot projectile (visual only)
        projectile = Projectile(
            center_x - 5,
            center_y - 5,
            hawkshot_x,
            hawkshot_y,
            speed=25,
            damage=0,  # No damage
            range=self.hawkshot_range
        )
        
        # Make hawkshot visually distinct
        projectile.color = (255, 255, 150)  # Yellow
        projectile.width = 15
        projectile.height = 15
        projectile.rect = pygame.Rect(int(projectile.x), int(projectile.y), 
                                    projectile.width, projectile.height)
        projectile.is_hawkshot = True  # Special flag
        
        self.projectiles.append(projectile)
        
        # Set hawkshot active
        self.hawkshot_active = True
        self.hawkshot_pos = (hawkshot_x, hawkshot_y)
        self.hawkshot_timer = self.hawkshot_duration
        
        # Set cooldown
        self.hawkshot_cooldown = self.hawkshot_cooldown_max
        return True
    
    def enchanted_arrow(self, target_x, target_y):
        """R ability - Enchanted Crystal Arrow: Long-range stun and damage"""
        if self.ultimate_cooldown > 0:
            return False
            
        # Calculate projectile starting position
        start_x = self.x + self.width/2 - 15
        start_y = self.y + self.height/2 - 15
        
        # Create the ultimate arrow projectile
        ultimate = Projectile(
            start_x, 
            start_y, 
            target_x, 
            target_y,
            speed=20,
            damage=self.ultimate_damage,
            range=self.ultimate_range
        )
        
        # Make ultimate arrow visually distinct
        ultimate.color = (100, 200, 255)  # Bright blue
        ultimate.width = 30
        ultimate.height = 30
        ultimate.rect = pygame.Rect(int(ultimate.x), int(ultimate.y), 
                                    ultimate.width, ultimate.height)
        
        # Special properties
        ultimate.is_ultimate = True
        ultimate.stun_duration = self.ultimate_stun_duration
        
        self.projectiles.append(ultimate)
        
        # Set cooldown
        self.ultimate_cooldown = self.ultimate_cooldown_max
        return True
        
    def flash(self, target_x, target_y):
        """Flash summoner spell - Instantly teleport to a nearby location"""
        # Inherit the flash ability from BasePlayer
        return super().flash(target_x, target_y)
    
    def slow_enemy(self, enemy):
        """Apply frost slow to an enemy"""
        # Check if enemy is already slowed
        for slow in self.slowed_enemies:
            if slow['enemy'] == enemy:
                # Refresh duration
                slow['duration'] = self.frost_slow_duration
                return
        
        # Apply new slow
        original_speed = getattr(enemy, 'original_speed', None)
        if original_speed is None:
            # First time being slowed, store original speed
            enemy.original_speed = enemy.speed
            original_speed = enemy.speed
        
        # Apply slow effect
        enemy.speed = original_speed * (1 - self.frost_slow_amount)
        
        # Add to slowed enemies list
        self.slowed_enemies.append({
            'enemy': enemy,
            'duration': self.frost_slow_duration
        })
    
    def remove_slow(self, enemy):
        """Remove slow effect from an enemy"""
        for slow in self.slowed_enemies[:]:
            if slow['enemy'] == enemy:
                # Restore original speed if it exists
                if hasattr(enemy, 'original_speed'):
                    enemy.speed = enemy.original_speed
                
                # Remove from slowed enemies list
                self.slowed_enemies.remove(slow)
                return
    
    def get_active_projectiles(self):
        """Return list of active projectiles for collision detection"""
        return [p for p in self.projectiles if p.active]
    
    def draw(self, screen):
        """Draw Ashe with ability cooldown indicators"""
        # Draw base player elements
        super().draw(screen)
        
        # Draw all projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        # Draw hawkshot vision area if active
        if self.hawkshot_active:
            vision_radius = 150
            vision_surface = pygame.Surface((vision_radius*2, vision_radius*2), pygame.SRCALPHA)
            
            # Calculate opacity based on remaining time
            opacity = int(150 * (self.hawkshot_timer / self.hawkshot_duration))
            
            # Draw vision circle
            pygame.draw.circle(
                vision_surface,
                (255, 255, 150, opacity),  # Yellow with fading opacity
                (vision_radius, vision_radius),
                vision_radius
            )
            
            # Draw the vision area
            screen.blit(
                vision_surface,
                (self.hawkshot_pos[0] - vision_radius, self.hawkshot_pos[1] - vision_radius)
            )
        
        # Draw ability cooldown indicators
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        # W cooldown (top)
        if self.volley_cooldown > 0:
            cooldown_ratio = 1 - (self.volley_cooldown / self.volley_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(screen, (180, 220, 255, 150), 
                             (int(center_x), int(center_y - 30)), radius, 2)
        
        # E cooldown (right)
        if self.hawkshot_cooldown > 0:
            cooldown_ratio = 1 - (self.hawkshot_cooldown / self.hawkshot_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(screen, (255, 255, 150, 150), 
                             (int(center_x + 30), int(center_y)), radius, 2)
        
        # R cooldown (bottom)
        if self.ultimate_cooldown > 0:
            cooldown_ratio = 1 - (self.ultimate_cooldown / self.ultimate_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(screen, (100, 200, 255, 150), 
                             (int(center_x), int(center_y + 30)), radius, 2)
        
        # Flash cooldown (top-right)
        if self.flash_cooldown > 0:
            cooldown_ratio = 1 - (self.flash_cooldown / self.flash_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(screen, (255, 255, 0, 150), 
                             (int(center_x + 30), int(center_y - 30)), radius, 2)
    
    def draw_with_camera(self, surface, camera_rect):
        """Draw Ashe with camera offset"""
        # Draw base player elements
        super().draw_with_camera(surface, camera_rect)
        
        # Draw all projectiles with camera offset
        for projectile in self.projectiles:
            if projectile.active:
                # Calculate projectile's position relative to the camera
                proj_camera_x = camera_rect.x + (projectile.x - self.x)
                proj_camera_y = camera_rect.y + (projectile.y - self.y)
                projectile.draw_with_camera(surface, (proj_camera_x, proj_camera_y))
        
        # Draw hawkshot vision area if active
        if self.hawkshot_active:
            vision_radius = 150
            vision_surface = pygame.Surface((vision_radius*2, vision_radius*2), pygame.SRCALPHA)
            
            # Calculate opacity based on remaining time
            opacity = int(150 * (self.hawkshot_timer / self.hawkshot_duration))
            
            # Draw vision circle
            pygame.draw.circle(
                vision_surface,
                (255, 255, 150, opacity),  # Yellow with fading opacity
                (vision_radius, vision_radius),
                vision_radius
            )
            
            # Calculate hawkshot position relative to the camera
            hawkshot_camera_x = self.hawkshot_pos[0] - self.game.camera.x if hasattr(self, 'game') else self.hawkshot_pos[0]
            hawkshot_camera_y = self.hawkshot_pos[1] - self.game.camera.y if hasattr(self, 'game') else self.hawkshot_pos[1]
            
            # Draw the vision area
            surface.blit(
                vision_surface,
                (hawkshot_camera_x - vision_radius, hawkshot_camera_y - vision_radius)
            )
        
        # Draw ability cooldown indicators with camera offset
        center_x = camera_rect.x + self.width/2
        center_y = camera_rect.y + self.height/2
        
        # W cooldown (top)
        if self.volley_cooldown > 0:
            cooldown_ratio = 1 - (self.volley_cooldown / self.volley_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(surface, (180, 220, 255, 150), 
                             (int(center_x), int(center_y - 30)), radius, 2)
        
        # E cooldown (right)
        if self.hawkshot_cooldown > 0:
            cooldown_ratio = 1 - (self.hawkshot_cooldown / self.hawkshot_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(surface, (255, 255, 150, 150), 
                             (int(center_x + 30), int(center_y)), radius, 2)
        
        # R cooldown (bottom)
        if self.ultimate_cooldown > 0:
            cooldown_ratio = 1 - (self.ultimate_cooldown / self.ultimate_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(surface, (100, 200, 255, 150), 
                             (int(center_x), int(center_y + 30)), radius, 2)
        
        # Flash cooldown (top-right)
        if self.flash_cooldown > 0:
            cooldown_ratio = 1 - (self.flash_cooldown / self.flash_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(surface, (255, 255, 0, 150), 
                             (int(center_x + 30), int(center_y - 30)), radius, 2)

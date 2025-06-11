# src/characters/ezreal.py
import pygame
import math
from .player import BasePlayer
from src.projectile import Projectile

class Ezreal(BasePlayer):
    def __init__(self, x, y):
        # Call the parent class constructor with image path
        super().__init__(x, y, "assets/images/characters/ezreal.png")
        
        # Override default attributes
        self.attack_damage = 30
        self.attack_cooldown_max = 12  # Faster attack speed
        self.speed = 6  # Slightly faster movement
        
        # If image loading failed, use a blue color as fallback
        if not hasattr(self, 'image') or self.image is None:
            self.color = (0, 100, 255)  # Blue color for Ezreal
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(self.color)
        else:
            self.color = (0, 100, 255)  # Keep color reference for other uses
        
        # Ezreal-specific attributes
        self.projectiles = []  # List to store active projectiles
        self.marked_enemies = []  # List to store enemies marked by W
        
        # Q - Mystic Shot
        self.q_cooldown = 0
        self.q_cooldown_max = 30  # 0.5 seconds at 60 FPS
        self.q_damage = 50
        self.q_range = 1150
        
        # W - Essence Flux (marks enemies but doesn't damage directly)
        self.w_cooldown = 0
        self.w_cooldown_max = 90  # 1.5 seconds at 60 FPS
        self.w_mark_duration = 240  # 4 seconds at 60 FPS
        self.w_range = 1000
        
        # E - Arcane Shift
        self.e_cooldown = 0
        self.e_cooldown_max = 180  # 3 seconds at 60 FPS
        self.e_range = 475
        self.e_damage = 80
        
        # R - Trueshot Barrage
        self.r_cooldown = 0
        self.r_cooldown_max = 600  # 10 seconds at 60 FPS
        self.r_damage = 150
        self.r_range = 2000  # Very long range
        
        # Flash (from BasePlayer)
        self.flash_cooldown = 0
        self.flash_cooldown_max = 300  # 5 seconds at 60 FPS
        self.flash_range = 600
    
    def update(self):
        # Update base player functionality
        super().update()
        
        # Update Ezreal-specific cooldowns
        if self.q_cooldown > 0:
            self.q_cooldown -= 1
        if self.w_cooldown > 0:
            self.w_cooldown -= 1
        if self.e_cooldown > 0:
            self.e_cooldown -= 1
        if self.r_cooldown > 0:
            self.r_cooldown -= 1
            
        # Update projectiles
        for projectile in self.projectiles[:]:  # Create a copy to safely remove items
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)
        
        # Update marked enemies (decrease duration)
        for mark in self.marked_enemies[:]:
            mark['duration'] -= 1
            if mark['duration'] <= 0:
                self.marked_enemies.remove(mark)
    
    def attack(self, target_x, target_y):
        """Basic attack (overrides BasePlayer.attack)"""
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
        projectile.color = (255, 255, 100)  # Yellow basic attack
        projectile.can_proc_w = True  # This projectile can trigger W marks
        self.projectiles.append(projectile)
        
        # Set cooldown
        self.attack_cooldown = self.attack_cooldown_max
        return True
    
    def mystic_shot(self, target_x, target_y):
        """Q ability - Mystic Shot: Long range skillshot that applies on-hit effects"""
        if self.q_cooldown > 0:
            return False
            
        # Calculate projectile starting position
        start_x = self.x + self.width/2 - 5
        start_y = self.y + self.height/2 - 5
        
        # Create a special Q projectile with custom properties
        q_projectile = Projectile(
            start_x, 
            start_y, 
            target_x, 
            target_y,
            speed=20,
            damage=self.q_damage,
            range=self.q_range
        )
        
        # Make Q projectile visually distinct
        q_projectile.color = (50, 150, 255)  # Lighter blue
        q_projectile.width = 15
        q_projectile.height = 15
        q_projectile.rect = pygame.Rect(int(q_projectile.x), int(q_projectile.y), 
                                        q_projectile.width, q_projectile.height)
        q_projectile.can_proc_w = True  # Q can trigger W marks
        
        self.projectiles.append(q_projectile)
        
        # Set cooldown
        self.q_cooldown = self.q_cooldown_max
        return True
    
    def essence_flux(self, target_x, target_y):
        """W ability - Essence Flux: Passes through enemies, marks champions but doesn't damage"""
        if self.w_cooldown > 0:
            return False
            
        # Calculate projectile starting position
        start_x = self.x + self.width/2 - 8
        start_y = self.y + self.height/2 - 8
        
        # Create a special W projectile with custom properties
        w_projectile = Projectile(
            start_x, 
            start_y, 
            target_x, 
            target_y,
            speed=15,
            damage=0,  # No direct damage
            range=self.w_range
        )
        
        # Make W projectile visually distinct
        w_projectile.color = (255, 200, 50)  # Yellow
        w_projectile.width = 20
        w_projectile.height = 20
        w_projectile.rect = pygame.Rect(int(w_projectile.x), int(w_projectile.y), 
                                        w_projectile.width, w_projectile.height)
        
        # W passes through enemies and marks them
        w_projectile.piercing = True
        w_projectile.is_w_marker = True  # Special flag for W ability
        
        self.projectiles.append(w_projectile)
        
        # Set cooldown
        self.w_cooldown = self.w_cooldown_max
        return True
    
    def arcane_shift(self, target_x, target_y):
        """E ability - Arcane Shift: Blink to location and fire a bolt at nearest enemy"""
        if self.e_cooldown > 0:
            return False
        
        # Store original position
        original_x = self.x
        original_y = self.y
        
        # Calculate player center position
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        # Calculate direction vector to target
        dx = target_x - center_x
        dy = target_y - center_y
        distance = math.hypot(dx, dy)
        
        # Determine blink distance (shorter than flash)
        if distance <= self.e_range:
            # Target is within range, blink directly to it
            target_x = target_x
            target_y = target_y
        else:
            # Target is beyond range, blink to maximum range in that direction
            angle = math.atan2(dy, dx)
            target_x = center_x + math.cos(angle) * self.e_range
            target_y = center_y + math.sin(angle) * self.e_range
        
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
        
        # Create a damage bolt at the destination
        bolt_x = self.x + self.width/2 - 5
        bolt_y = self.y + self.height/2 - 5
        
        # Create a bolt projectile that fires in the same direction as the blink
        bolt_projectile = Projectile(
            bolt_x,
            bolt_y,
            bolt_x + dx,  # Continue in same direction
            bolt_y + dy,
            speed=18,
            damage=self.e_damage,
            range=300
        )
        
        # Make E bolt visually distinct
        bolt_projectile.color = (100, 200, 255)  # Light blue
        bolt_projectile.width = 15
        bolt_projectile.height = 15
        bolt_projectile.rect = pygame.Rect(int(bolt_projectile.x), int(bolt_projectile.y), 
                                        bolt_projectile.width, bolt_projectile.height)
        bolt_projectile.can_proc_w = True  # E can trigger W marks
        
        self.projectiles.append(bolt_projectile)
        
        # Set cooldown
        self.e_cooldown = self.e_cooldown_max
        return True
    
    def trueshot_barrage(self, target_x, target_y):
        """R ability - Trueshot Barrage: Global skillshot that damages all enemies in its path"""
        if self.r_cooldown > 0:
            return False
            
        # Calculate projectile starting position
        start_x = self.x + self.width/2 - 15
        start_y = self.y + self.height/2 - 15
        
        # Create a special R projectile with custom properties
        r_projectile = Projectile(
            start_x, 
            start_y, 
            target_x, 
            target_y,
            speed=25,
            damage=self.r_damage,
            range=self.r_range
        )
        
        # Make R projectile visually distinct
        r_projectile.color = (255, 100, 50)  # Orange-red
        r_projectile.width = 30
        r_projectile.height = 30
        r_projectile.rect = pygame.Rect(int(r_projectile.x), int(r_projectile.y), 
                                        r_projectile.width, r_projectile.height)
        
        # Make R pierce through enemies
        r_projectile.piercing = True
        r_projectile.can_proc_w = True  # R can trigger W marks
        
        self.projectiles.append(r_projectile)
        
        # Set cooldown
        self.r_cooldown = self.r_cooldown_max
        return True
        
    def flash(self, target_x, target_y):
        """Flash summoner spell - Instantly teleport to a nearby location"""
        # Inherit the flash ability from BasePlayer
        return super().flash(target_x, target_y)
    
    def mark_enemy(self, enemy):
        """Mark an enemy with Essence Flux (W)"""
        # Check if enemy is already marked
        for mark in self.marked_enemies:
            if mark['enemy'] == enemy:
                # Refresh duration
                mark['duration'] = self.w_mark_duration
                return
        
        # Add new mark
        self.marked_enemies.append({
            'enemy': enemy,
            'duration': self.w_mark_duration
        })
    
    def is_enemy_marked(self, enemy):
        """Check if an enemy is marked by W"""
        for mark in self.marked_enemies:
            if mark['enemy'] == enemy:
                return True
        return False
    
    def proc_w_mark(self, enemy):
        """Process W mark when hit by an ability that can proc it"""
        for mark in self.marked_enemies[:]:
            if mark['enemy'] == enemy:
                # Deal bonus damage (40 at level 1)
                enemy.take_damage(40)
                
                # Remove the mark
                self.marked_enemies.remove(mark)
                
                # Reduce E cooldown by 3 seconds (180 frames)
                self.e_cooldown = max(0, self.e_cooldown - 180)
                
                return True
        return False
    
    def get_active_projectiles(self):
        """Return list of active projectiles for collision detection"""
        return [p for p in self.projectiles if p.active]
    
    def draw(self, screen):
        """Draw Ezreal with ability cooldown indicators"""
        # Draw base player elements
        super().draw(screen)
        
        # Draw all projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        # Draw ability cooldown indicators
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        # Q cooldown (top)
        if self.q_cooldown > 0:
            cooldown_ratio = 1 - (self.q_cooldown / self.q_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(screen, (50, 150, 255, 150), 
                             (int(center_x), int(center_y - 30)), radius, 2)
        
        # W cooldown (right)
        if self.w_cooldown > 0:
            cooldown_ratio = 1 - (self.w_cooldown / self.w_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(screen, (255, 200, 50, 150), 
                             (int(center_x + 30), int(center_y)), radius, 2)
        
        # E cooldown (bottom)
        if self.e_cooldown > 0:
            cooldown_ratio = 1 - (self.e_cooldown / self.e_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(screen, (100, 200, 255, 150), 
                             (int(center_x), int(center_y + 30)), radius, 2)
        
        # R cooldown (left)
        if self.r_cooldown > 0:
            cooldown_ratio = 1 - (self.r_cooldown / self.r_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(screen, (255, 100, 50, 150), 
                             (int(center_x - 30), int(center_y)), radius, 2)
        
        # Flash cooldown (top-right)
        if self.flash_cooldown > 0:
            cooldown_ratio = 1 - (self.flash_cooldown / self.flash_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(screen, (255, 255, 0, 150), 
                             (int(center_x + 30), int(center_y - 30)), radius, 2)
    
    def draw_with_camera(self, surface, camera_rect):
        """Draw Ezreal with camera offset"""
        # Draw base player elements
        super().draw_with_camera(surface, camera_rect)
        
        # Draw all projectiles with camera offset
        for projectile in self.projectiles:
            if projectile.active:
                # Calculate projectile's position relative to the camera
                proj_camera_x = camera_rect.x + (projectile.x - self.x)
                proj_camera_y = camera_rect.y + (projectile.y - self.y)
                projectile.draw_with_camera(surface, (proj_camera_x, proj_camera_y))
        
        # Draw ability cooldown indicators with camera offset
        center_x = camera_rect.x + self.width/2
        center_y = camera_rect.y + self.height/2
        
        # Q cooldown (top)
        if self.q_cooldown > 0:
            cooldown_ratio = 1 - (self.q_cooldown / self.q_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(surface, (50, 150, 255, 150), 
                             (int(center_x), int(center_y - 30)), radius, 2)
        
        # W cooldown (right)
        if self.w_cooldown > 0:
            cooldown_ratio = 1 - (self.w_cooldown / self.w_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(surface, (255, 200, 50, 150), 
                             (int(center_x + 30), int(center_y)), radius, 2)
        
        # E cooldown (bottom)
        if self.e_cooldown > 0:
            cooldown_ratio = 1 - (self.e_cooldown / self.e_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(surface, (100, 200, 255, 150), 
                             (int(center_x), int(center_y + 30)), radius, 2)
        
        # R cooldown (left)
        if self.r_cooldown > 0:
            cooldown_ratio = 1 - (self.r_cooldown / self.r_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(surface, (255, 100, 50, 150), 
                             (int(center_x - 30), int(center_y)), radius, 2)
        
        # Flash cooldown (top-right)
        if self.flash_cooldown > 0:
            cooldown_ratio = 1 - (self.flash_cooldown / self.flash_cooldown_max)
            radius = int(15 * cooldown_ratio)
            pygame.draw.circle(surface, (255, 255, 0, 150), 
                             (int(center_x + 30), int(center_y - 30)), radius, 2)

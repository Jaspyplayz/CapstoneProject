# src/enemy.py
import pygame
import random
import math
import os
from src.constants import MAP_WIDTH, MAP_HEIGHT, RED, GREEN
from src.projectile import Projectile  # Import your existing Projectile class

class Enemy:
    def __init__(self, game, speed, health, enemy_type="basic", x=None, y=None):
        self.game = game

        # Basic properties
        self.speed = speed
        self.health = health
        self.max_health = health
        self.detection_radius = 400
        self.score_value = 100
        self.enemy_type = enemy_type  # Store the enemy type
        
        # Size and appearance
        self.width = 30
        self.height = 30
        self.color = (255, 0, 0)  # Default color, will be set by EnemyManager
        
        # Position
        self.x = x if x is not None else random.randint(0, MAP_WIDTH - self.width)
        self.y = y if y is not None else random.randint(0, MAP_HEIGHT - self.height)
        
        # Collision detection
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        # State
        self.alive = True
        self.hit_flash = 0
        self.hit_flash_duration = 5
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = random.uniform(0, 2 * math.pi)
        self.direction_change_timer = 0
        self.direction_change_delay = random.randint(60, 120)
        
        # Set initial velocity
        self.set_velocity_from_angle()
        
        # Visual features for drawing
        self.eye_radius = max(3, int(self.width / 10))
        self.eye_distance = max(5, int(self.width / 6))
        
        # Image will be set later by EnemyManager
        self.image = None
        self.mask = None
        
        # Projectile system
        self.projectiles = []
        self.attack_cooldown = 0
        self.attack_range = 300  # Range at which enemy will start shooting
        
        # Set attack properties based on enemy type
        self.setup_attack_properties()

    def setup_attack_properties(self):
        """Set attack properties based on enemy type"""
        # Default values
        self.can_shoot = True
        self.attack_cooldown_max = 120  # 2 seconds at 60 FPS
        self.projectile_speed = 5
        self.projectile_damage = 5
        self.projectile_range = 600
        
        # Customize based on enemy type
        if self.enemy_type == "basic":
            self.can_shoot = True
            self.attack_cooldown_max = 120
            self.projectile_speed = 5
            self.projectile_damage = 5
            self.projectile_color = (255, 100, 100)
            
        elif self.enemy_type == "fast":
            self.can_shoot = True
            self.attack_cooldown_max = 90  # Shoots more frequently
            self.projectile_speed = 7      # Faster projectiles
            self.projectile_damage = 3     # Less damage
            self.projectile_color = (100, 255, 100)
            
        elif self.enemy_type == "tank":
            self.can_shoot = True
            self.attack_cooldown_max = 180  # Shoots less frequently
            self.projectile_speed = 4       # Slower projectiles
            self.projectile_damage = 8      # More damage
            self.projectile_color = (100, 100, 255)
            
        elif self.enemy_type == "boss":
            self.can_shoot = True
            self.attack_cooldown_max = 60   # Shoots frequently
            self.projectile_speed = 6
            self.projectile_damage = 12     # High damage
            self.projectile_color = (200, 50, 200)
            self.attack_range = 400         # Longer attack range

    def set_velocity_from_angle(self):
        """Set velocity based on current angle"""
        self.velocity_x = math.cos(self.angle) * self.speed
        self.velocity_y = math.sin(self.angle) * self.speed

    def update(self):
        """Update enemy position and state"""
        if not self.alive:
            return
            
        # Update hit flash effect
        if self.hit_flash > 0:
            self.hit_flash -= 1
            
        # Get player position
        player_x = self.game.player.x + self.game.player.width/2
        player_y = self.game.player.y + self.game.player.height/2
        
        # Calculate distance to player
        dx = player_x - (self.x + self.width/2)
        dy = player_y - (self.y + self.height/2)
        distance_to_player = math.sqrt(dx*dx + dy*dy)
        
        # Chase player if within detection radius
        if distance_to_player < self.detection_radius:
            self.angle = math.atan2(dy, dx)
            
            # If within attack range, slow down or stop and attack
            if distance_to_player < self.attack_range and self.can_shoot:
                # Slow down or stop when attacking
                if self.enemy_type == "tank" or self.enemy_type == "boss":
                    # Tanks and bosses stop completely when shooting
                    self.velocity_x = 0
                    self.velocity_y = 0
                else:
                    # Other enemies slow down
                    self.velocity_x = math.cos(self.angle) * (self.speed * 0.5)
                    self.velocity_y = math.sin(self.angle) * (self.speed * 0.5)
                
                # Attack if cooldown is ready
                if self.attack_cooldown <= 0:
                    self.shoot_at_player(player_x, player_y)
                    self.attack_cooldown = self.attack_cooldown_max
            else:
                # Normal movement when not attacking
                self.set_velocity_from_angle()
        else:
            # Random wandering
            self.direction_change_timer += 1
            if self.direction_change_timer >= self.direction_change_delay:
                self.angle += random.uniform(-math.pi/2, math.pi/2)
                self.set_velocity_from_angle()
                self.direction_change_timer = 0
                self.direction_change_delay = random.randint(60, 120)
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Move based on velocity
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Keep within map boundaries
        if self.x < 0:
            self.x = 0
            self.angle = math.pi - self.angle
            self.set_velocity_from_angle()
        elif self.x > MAP_WIDTH - self.width:
            self.x = MAP_WIDTH - self.width
            self.angle = math.pi - self.angle
            self.set_velocity_from_angle()

        if self.y < 0:
            self.y = 0
            self.angle = -self.angle
            self.set_velocity_from_angle()
        elif self.y > MAP_HEIGHT - self.height:
            self.y = MAP_HEIGHT - self.height
            self.angle = -self.angle
            self.set_velocity_from_angle()

        # Update hitbox position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Update projectiles
        self.update_projectiles()

    def shoot_at_player(self, player_x, player_y):
        """Shoot a projectile at the player"""
        if not self.can_shoot:
            return
            
        # Calculate projectile starting position (center of enemy)
        start_x = self.x + self.width/2
        start_y = self.y + self.height/2
        
        # Add some randomness to aim for non-boss enemies
        if self.enemy_type != "boss":
            spread = 0.1  # Radians
            angle = math.atan2(player_y - start_y, player_x - start_x)
            angle += random.uniform(-spread, spread)
            
            # Recalculate target position with spread
            target_distance = math.sqrt((player_x - start_x)**2 + (player_y - start_y)**2)
            target_x = start_x + math.cos(angle) * target_distance
            target_y = start_y + math.sin(angle) * target_distance
        else:
            # Bosses have perfect aim
            target_x = player_x
            target_y = player_y
        
        # Create projectile using the existing Projectile class
        projectile = Projectile(
            start_x, 
            start_y, 
            target_x, 
            target_y,
            speed=self.projectile_speed,
            damage=self.projectile_damage,
            range=self.projectile_range
        )
        
        # Customize projectile based on enemy type
        projectile.color = self.projectile_color
        
        # Special projectile effects for different enemy types
        if self.enemy_type == "boss":
            projectile.width = projectile.height = 12  # Bigger projectile
            projectile.rect = pygame.Rect(int(projectile.x), int(projectile.y), projectile.width, projectile.height)
        elif self.enemy_type == "fast":
            projectile.width = projectile.height = 8  # Smaller projectile
            projectile.rect = pygame.Rect(int(projectile.x), int(projectile.y), projectile.width, projectile.height)
        
        self.projectiles.append(projectile)
        
        # Special attack patterns for different enemy types
        if self.enemy_type == "fast" and random.random() < 0.3:
            # Fast enemies sometimes shoot a burst of 3 projectiles
            self.attack_cooldown = 15  # Short cooldown for next shot
        
        if self.enemy_type == "boss":
            # Boss sometimes fires multiple projectiles in a spread pattern
            if random.random() < 0.4:
                self.fire_spread_attack(start_x, start_y, player_x, player_y)

    def fire_spread_attack(self, start_x, start_y, player_x, player_y):
        """Fire multiple projectiles in a spread pattern (boss only)"""
        base_angle = math.atan2(player_y - start_y, player_x - start_x)
        
        # Fire 5 projectiles in a spread
        for i in range(-2, 3):
            angle = base_angle + (i * 0.15)  # 0.15 radians between shots
            
            # Calculate target position
            target_distance = 1000  # Just needs to be large
            target_x = start_x + math.cos(angle) * target_distance
            target_y = start_y + math.sin(angle) * target_distance
            
            # Create projectile using the existing Projectile class
            projectile = Projectile(
                start_x, 
                start_y, 
                target_x, 
                target_y,
                speed=self.projectile_speed,
                damage=self.projectile_damage,
                range=self.projectile_range
            )
            
            # Customize projectile
            projectile.color = self.projectile_color
            projectile.width = projectile.height = 10
            projectile.rect = pygame.Rect(int(projectile.x), int(projectile.y), projectile.width, projectile.height)
            
            self.projectiles.append(projectile)

    def update_projectiles(self):
        """Update all projectiles fired by this enemy"""
        for projectile in self.projectiles[:]:
            projectile.update()
            
            # Check for collision with player
            if (projectile.active and 
                projectile.rect.colliderect(self.game.player.rect)):
                # Damage player
                self.game.player.take_damage(projectile.damage)
                projectile.active = False
            
            # Remove inactive projectiles
            if not projectile.active:
                self.projectiles.remove(projectile)

    def take_damage(self, amount):
        """Apply damage to the enemy"""
        if not self.alive:
            return False
        
        self.health -= amount
        self.hit_flash = self.hit_flash_duration
        
        if self.health <= 0:
            self.die()
            return True
        return False

    def die(self):
        """Handle enemy death"""
        self.alive = False
        
        # Deactivate all projectiles when enemy dies
        for projectile in self.projectiles:
            projectile.active = False
        self.projectiles = []

    def load_image(self):
        """Try to load the enemy image from assets folder"""
        try:
            # List of possible paths to try
            possible_paths = [
                f"assets/images/enemies/{self.enemy_type}_enemy.png",
                f"./assets/images/enemies/{self.enemy_type}_enemy.png",
                os.path.join(os.getcwd(), f"assets/images/enemies/{self.enemy_type}_enemy.png"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), f"assets/images/enemies/{self.enemy_type}_enemy.png")
            ]
            
            # Try each path
            for path in possible_paths:
                if os.path.exists(path):
                    image = pygame.image.load(path).convert_alpha()
                    image = pygame.transform.scale(image, (self.width, self.height))
                    return image
            
            return None
            
        except Exception:
            return None

    def create_enemy_surface(self):
        """Create and return a surface with the enemy drawn on it"""
        # Create a surface with per-pixel alpha
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw the base shape
        pygame.draw.ellipse(surface, self.color, (0, 0, self.width, self.height))
        
        # Add darker outline
        pygame.draw.ellipse(surface, (max(0, self.color[0] - 50), 
                                    max(0, self.color[1] - 50), 
                                    max(0, self.color[2] - 50)), 
                        (0, 0, self.width, self.height), 2)
        
        # Calculate eye positions
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Eyes look in the direction of movement
        eye_offset_x = math.cos(self.angle) * self.eye_distance
        eye_offset_y = math.sin(self.angle) * self.eye_distance
        
        # Left eye
        left_eye_x = center_x - self.eye_distance + eye_offset_x * 0.3
        left_eye_y = center_y - self.eye_distance + eye_offset_y * 0.3
        
        # Right eye
        right_eye_x = center_x + self.eye_distance + eye_offset_x * 0.3
        right_eye_y = center_y - self.eye_distance + eye_offset_y * 0.3
        
        # Draw eyes (white)
        pygame.draw.circle(surface, (255, 255, 255), (int(left_eye_x), int(left_eye_y)), self.eye_radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(right_eye_x), int(right_eye_y)), self.eye_radius)
        
        # Draw pupils (black)
        pupil_offset_x = math.cos(self.angle) * (self.eye_radius * 0.5)
        pupil_offset_y = math.sin(self.angle) * (self.eye_radius * 0.5)
        
        pygame.draw.circle(surface, (0, 0, 0), 
                        (int(left_eye_x + pupil_offset_x), int(left_eye_y + pupil_offset_y)), 
                        max(1, self.eye_radius // 2))
        pygame.draw.circle(surface, (0, 0, 0), 
                        (int(right_eye_x + pupil_offset_x), int(right_eye_y + pupil_offset_y)), 
                        max(1, self.eye_radius // 2))
        
        # Draw simple mouth
        mouth_y = center_y + self.height // 4
        mouth_width = self.width // 2
        mouth_height = self.height // 6
        
        pygame.draw.ellipse(surface, (0, 0, 0), 
                        (center_x - mouth_width//2, mouth_y, mouth_width, mouth_height))
        
        # Add special visual elements based on enemy type
        if self.enemy_type == "boss":
            # Add a crown for boss enemies
            crown_points = [
                (center_x, 2),
                (center_x - self.width//4, self.height//6),
                (center_x + self.width//4, self.height//6)
            ]
            pygame.draw.polygon(surface, (255, 215, 0), crown_points)  # Gold crown
            
        elif self.enemy_type == "fast":
            # Add speed lines for fast enemies
            for i in range(3):
                start_x = 2
                start_y = self.height//4 + i * (self.height//6)
                end_x = self.width//3
                end_y = start_y
                pygame.draw.line(surface, (0, 0, 0), (start_x, start_y), (end_x, end_y), 2)
                
        elif self.enemy_type == "tank":
            # Add armor plates for tank enemies
            pygame.draw.arc(surface, (100, 100, 100), 
                          (self.width//6, self.height//6, 
                           self.width*2//3, self.height*2//3), 
                          math.pi/4, math.pi*7/4, 3)
        
        return surface

    def draw(self, surface):
        """Draw the enemy directly to the surface"""
        if not self.alive:
            return
        
        # Create image if it doesn't exist yet
        if self.image is None:
            self.image = self.create_enemy_surface()
            self.mask = pygame.mask.from_surface(self.image)
        
        # Use the pre-rendered image
        enemy_surface = self.image.copy() if self.hit_flash > 0 else self.image
        
        # Apply hit flash effect
        if self.hit_flash > 0:
            flash_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_overlay.fill((255, 255, 255, 150))
            enemy_surface.blit(flash_overlay, (0, 0))
        
        # Draw enemy
        surface.blit(enemy_surface, (int(self.x), int(self.y)))

        # Draw health bar
        health_bar_width = self.width - 10
        health_ratio = max(0, self.health / self.max_health)

        # Health bar background
        pygame.draw.rect(surface, RED, 
                        (int(self.x) + 5, int(self.y) - 10, health_bar_width, 5))
        
        # Health bar foreground
        pygame.draw.rect(surface, GREEN, 
                        (int(self.x) + 5, int(self.y) - 10, int(health_bar_width * health_ratio), 5))
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)

    def draw_with_camera(self, surface, camera_pos):
        """Draw the enemy with camera offset"""
        if not self.alive:
            return
        
        # Create image if it doesn't exist yet
        if self.image is None:
            self.image = self.create_enemy_surface()
            self.mask = pygame.mask.from_surface(self.image)
        
        # Use the pre-rendered image
        enemy_surface = self.image.copy() if self.hit_flash > 0 else self.image
        
        # Apply hit flash effect
        if self.hit_flash > 0:
            flash_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_overlay.fill((255, 255, 255, 150))
            enemy_surface.blit(flash_overlay, (0, 0))
        
        # Draw enemy at camera position
        surface.blit(enemy_surface, camera_pos)

        # Draw health bar with camera offset
        health_bar_width = self.width - 10
        health_ratio = max(0, self.health / self.max_health)

        # Health bar background
        pygame.draw.rect(surface, RED, 
                        (camera_pos[0] + 5, camera_pos[1] - 10, health_bar_width, 5))
        
        # Health bar foreground
        pygame.draw.rect(surface, GREEN, 
                        (camera_pos[0] + 5, camera_pos[1] - 10, int(health_bar_width * health_ratio), 5))
        
        # Draw projectiles with camera offset
        for projectile in self.projectiles:
            # Calculate projectile's camera position
            proj_camera_pos = (
                camera_pos[0] - (self.x + self.width/2 - projectile.x),
                camera_pos[1] - (self.y + self.height/2 - projectile.y)
            )
            projectile.draw_with_camera(surface, proj_camera_pos)

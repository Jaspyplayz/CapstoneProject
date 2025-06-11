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
        self.detection_radius = 300  # Increased detection radius
        self.score_value = 100
        
        # AI behavior parameters
        self.aggression = random.uniform(0.3, 0.7)  # How aggressively it pursues the player
        self.intelligence = random.uniform(0.4, 0.9)  # How well it predicts player movement
        self.personality = random.choice(["aggressive", "cautious", "erratic", "flanker"])
        self.state = "wander"  # Current AI state: wander, chase, retreat, flank
        
        # Combat stats
        self.attack_damage = random.randint(5, 15)
        self.attack_cooldown = 0
        self.attack_cooldown_max = random.randint(30, 60)  # Time between attacks
        self.knockback_resistance = random.uniform(0.5, 1.0)

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

        # State
        self.alive = True
        self.debug_mode = False
        
        # Status effects - Define these BEFORE calling set_velocity_from_angle
        self.stunned = 0  # Stun duration counter
        self.slowed = 0   # Slow duration counter
        self.slow_amount = 0  # How much enemy is slowed (0-1)
        self.effects = []  # List of active effects (stun, slow, etc.)
        
        # Movement vectors
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = random.uniform(0, 2 * math.pi)
        self.target_angle = self.angle
        self.turn_speed = random.uniform(0.02, 0.08)  # How quickly enemy can change direction
        
        # Now we can safely call this since slowed and slow_amount are defined
        self.set_velocity_from_angle()

        # Direction change timer
        self.direction_change_timer = 0
        self.direction_change_delay = random.randint(60, 120)
        
        # State timers
        self.state_timer = 0
        self.state_duration = random.randint(180, 300)  # How long to stay in current state
        
        # Path finding
        self.path_timer = 0
        self.path_update_rate = 30  # How often to recalculate path
        self.waypoints = []
        self.current_waypoint = 0
        
        # Memory of player's last known position
        self.player_last_seen_x = 0
        self.player_last_seen_y = 0
        self.player_last_seen_time = 0
        self.memory_duration = random.randint(180, 360)  # How long enemy remembers player position

        # Sound effects
        self.hit_sound = "enemy_hit"
        self.death_sound = "enemy_death"
        
        # Hit effect
        self.hit_flash = 0
        self.hit_flash_duration = 5
        
    def set_velocity_from_angle(self):
        effective_speed = self.speed
        if self.slowed > 0:
            effective_speed *= (1 - self.slow_amount)
            
        self.velocity_x = math.cos(self.angle) * effective_speed
        self.velocity_y = math.sin(self.angle) * effective_speed

    def update(self):
        if not self.alive:
            return 
        
        # Update hit flash effect
        if self.hit_flash > 0:
            self.hit_flash -= 1
            
        # Update status effects
        self.update_status_effects()
        
        # Skip movement if stunned
        if self.stunned > 0:
            return
        
        # Get player position
        player_x = self.game.player.x + self.game.player.width/2
        player_y = self.game.player.y + self.game.player.height/2
        
        # Calculate distance to player
        dx = player_x - (self.x + self.width/2)
        dy = player_y - (self.y + self.height/2)
        distance_to_player = math.sqrt(dx*dx + dy*dy)
        
        # Update player's last known position if visible
        if distance_to_player < self.detection_radius:
            self.player_last_seen_x = player_x
            self.player_last_seen_y = player_y
            self.player_last_seen_time = 0
        else:
            self.player_last_seen_time += 1
        
        # Update AI state based on conditions
        self.update_ai_state(distance_to_player)
        
        # Execute behavior based on current state
        if self.state == "chase":
            self.chase_player(player_x, player_y, distance_to_player)
        elif self.state == "wander":
            self.wander()
        elif self.state == "retreat":
            self.retreat_from_player(player_x, player_y)
        elif self.state == "flank":
            self.flank_player(player_x, player_y)
        elif self.state == "investigate":
            self.investigate_last_seen()
            
        # Gradually turn towards target angle (smoother turning)
        angle_diff = (self.target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        if abs(angle_diff) > 0.01:
            self.angle += min(self.turn_speed, abs(angle_diff)) * (1 if angle_diff > 0 else -1)
            self.set_velocity_from_angle()
        
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
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def update_status_effects(self):
        """Update all active status effects"""
        # Update stun
        if self.stunned > 0:
            self.stunned -= 1
            
        # Update slow
        if self.slowed > 0:
            self.slowed -= 1
            if self.slowed <= 0:
                self.slow_amount = 0
                self.set_velocity_from_angle()  # Reset speed
                
        # Update other effects
        for effect in self.effects[:]:  # Create a copy to safely remove items
            effect['duration'] -= 1
            if effect['duration'] <= 0:
                self.effects.remove(effect)
                # Handle effect expiration
                if effect['type'] == 'frost':
                    self.slowed = 0
                    self.slow_amount = 0
                    self.set_velocity_from_angle()

    def update_ai_state(self, distance_to_player):
        """Update the AI state based on game conditions"""
        # Update state timer
        self.state_timer += 1
        
        # Check for state transitions
        if self.state_timer >= self.state_duration:
            # Time to potentially change state
            self.state_timer = 0
            self.state_duration = random.randint(180, 300)
            
            # Determine new state based on personality and situation
            if distance_to_player < self.detection_radius:
                # Player is detected
                if self.personality == "aggressive":
                    self.state = "chase"
                elif self.personality == "cautious" and self.health < self.max_health * 0.3:
                    self.state = "retreat"
                elif self.personality == "flanker":
                    self.state = "flank"
                elif self.personality == "erratic":
                    self.state = random.choice(["chase", "wander", "flank"])
                else:
                    self.state = "chase"
            elif self.player_last_seen_time < self.memory_duration:
                # Player was seen recently
                self.state = "investigate"
            else:
                # No recent player contact
                self.state = "wander"
        
        # Override state based on immediate conditions
        if self.personality == "aggressive" and distance_to_player < self.detection_radius:
            self.state = "chase"
        elif self.personality == "cautious" and self.health < self.max_health * 0.3 and distance_to_player < self.detection_radius:
            self.state = "retreat"

    def wander(self):
        """Random wandering behavior"""
        self.direction_change_timer += 1
        if self.direction_change_timer >= self.direction_change_delay:
            self.change_direction()
            self.direction_change_timer = 0

    def chase_player(self, player_x, player_y, distance):
        """Chase the player with intelligence-based prediction"""
        # Basic position
        dx = player_x - (self.x + self.width/2)
        dy = player_y - (self.y + self.height/2)
        
        # For smarter enemies, try to predict where player will be
        if self.intelligence > 0.6 and hasattr(self.game.player, 'velocity_x'):
            # Predict player position based on current velocity
            prediction_time = distance / (self.speed * 10)  # Time to reach player
            player_x += self.game.player.velocity_x * prediction_time * self.intelligence
            player_y += self.game.player.velocity_y * prediction_time * self.intelligence
            
            # Recalculate direction with prediction
            dx = player_x - (self.x + self.width/2)
            dy = player_y - (self.y + self.height/2)
        
        # Set target angle toward player (or predicted position)
        self.target_angle = math.atan2(dy, dx)
        
        # Add some randomness based on personality
        if self.personality == "erratic":
            self.target_angle += random.uniform(-0.5, 0.5)
            
        # Try to attack if close enough
        if distance < 50 and self.attack_cooldown <= 0:
            self.attack_player()

    def retreat_from_player(self, player_x, player_y):
        """Move away from the player"""
        dx = player_x - (self.x + self.width/2)
        dy = player_y - (self.y + self.height/2)
        
        # Target angle is opposite direction from player
        self.target_angle = math.atan2(-dy, -dx)
        
        # Add some randomness for more natural movement
        self.target_angle += random.uniform(-0.3, 0.3)

    def flank_player(self, player_x, player_y):
        """Try to move to the side of the player"""
        dx = player_x - (self.x + self.width/2)
        dy = player_y - (self.y + self.height/2)
        
        # Get angle to player
        angle_to_player = math.atan2(dy, dx)
        
        # Choose a flanking angle (perpendicular to player direction)
        flank_direction = 1 if random.random() > 0.5 else -1
        flank_angle = angle_to_player + (math.pi/2 * flank_direction)
        
        # Set target angle
        self.target_angle = flank_angle
        
        # Periodically update flanking direction
        if random.random() < 0.01:  # 1% chance each frame
            self.target_angle = angle_to_player + (math.pi/2 * -flank_direction)  # Switch sides

    def investigate_last_seen(self):
        """Move to player's last known position"""
        dx = self.player_last_seen_x - (self.x + self.width/2)
        dy = self.player_last_seen_y - (self.y + self.height/2)
        distance = math.sqrt(dx*dx + dy*dy)
        
        # If close to last seen position, start wandering
        if distance < 50:
            self.state = "wander"
            self.state_timer = 0
            return
            
        # Set target angle toward last seen position
        self.target_angle = math.atan2(dy, dx)
        
        # Add slight randomness
        self.target_angle += random.uniform(-0.2, 0.2)

    def attack_player(self):
        """Attack the player if in range"""
        # Check if player is in attack range
        player_x = self.game.player.x + self.game.player.width/2
        player_y = self.game.player.y + self.game.player.height/2
        
        dx = player_x - (self.x + self.width/2)
        dy = player_y - (self.y + self.height/2)
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 50:  # Attack range
            # Deal damage to player
            if hasattr(self.game.player, 'take_damage'):
                self.game.player.take_damage(self.attack_damage)
                
            # Set attack cooldown
            self.attack_cooldown = self.attack_cooldown_max
            
            # Visual feedback
            self.hit_flash = self.hit_flash_duration
            
            return True
        return False

    def update_hitbox(self):
        """Update the hitbox position based on the enemy's position"""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def bounce_horizontal(self):
        self.angle = math.pi - self.angle
        self.target_angle = self.angle
        self.set_velocity_from_angle()
    
    def bounce_vertical(self):
        self.angle = -self.angle
        self.target_angle = self.angle
        self.set_velocity_from_angle()

    def change_direction(self):
        # More natural direction changes
        # Prefer to change by smaller amounts rather than completely random
        change_amount = random.uniform(-math.pi/2, math.pi/2)
        self.target_angle = (self.angle + change_amount) % (2 * math.pi)
        self.direction_change_delay = random.randint(60, 120)

    def seek_player(self, player_x, player_y, aggression=0.5):
        """Legacy method - now handled by chase_player"""
        self.state = "chase"
        self.chase_player(player_x, player_y, 
                         math.hypot(player_x - (self.x + self.width/2), 
                                   player_y - (self.y + self.height/2)))

    def apply_knockback(self, angle, force):
        """Apply knockback force to the enemy"""
        # Reduce force based on knockback resistance
        effective_force = force * (1 - self.knockback_resistance)
        
        # Apply knockback
        self.x += math.cos(angle) * effective_force
        self.y += math.sin(angle) * effective_force
        
        # Update hitbox
        self.update_hitbox()

    def apply_stun(self, duration):
        """Apply stun effect to the enemy"""
        self.stunned = max(self.stunned, duration)  # Take the longer stun duration

    def apply_slow(self, amount, duration):
        """Apply slow effect to the enemy"""
        self.slowed = max(self.slowed, duration)
        self.slow_amount = max(self.slow_amount, amount)
        self.set_velocity_from_angle()  # Update velocity with new speed

    def apply_effect(self, effect_type, duration, intensity=1.0):
        """Apply a status effect to the enemy"""
        # Check if effect already exists
        for effect in self.effects:
            if effect['type'] == effect_type:
                # Refresh duration if new duration is longer
                if duration > effect['duration']:
                    effect['duration'] = duration
                    effect['intensity'] = max(effect['intensity'], intensity)
                return
        
        # Add new effect
        self.effects.append({
            'type': effect_type,
            'duration': duration,
            'intensity': intensity
        })
        
        # Apply immediate effect
        if effect_type == 'stun':
            self.apply_stun(duration)
        elif effect_type == 'slow' or effect_type == 'frost':
            self.apply_slow(intensity, duration)

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
            
        # React to damage - cautious enemies may flee
        if self.personality == "cautious" and self.health < self.max_health * 0.5:
            self.state = "retreat"
            self.state_timer = 0
            self.state_duration = random.randint(120, 240)

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
        
        # Apply visual effects for status effects
        if self.stunned > 0:
            # Add stars or other stun indicator
            pygame.draw.circle(current_image, (255, 255, 0), (self.width//2, 5), 3)
            pygame.draw.circle(current_image, (255, 255, 0), (self.width//2-10, 5), 3)
            pygame.draw.circle(current_image, (255, 255, 0), (self.width//2+10, 5), 3)
        
        if self.slowed > 0:
            # Add blue tint for slowed
            blue_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            blue_overlay.fill((0, 0, 255, 50))
            current_image.blit(blue_overlay, (0, 0))
        
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
        
        # Debug: Draw hitbox and AI state if debug mode is enabled
        if self.debug_mode:
            pygame.draw.rect(surface, (255, 0, 255), self.rect, 1)
            
            # Draw detection radius
            pygame.draw.circle(surface, (255, 255, 0), 
                              (int(self.x + self.width/2), int(self.y + self.height/2)), 
                              self.detection_radius, 1)
            
            # Draw current state text
            font = pygame.font.SysFont(None, 20)
            state_text = font.render(self.state, True, (255, 255, 255))
            surface.blit(state_text, (int(self.x), int(self.y) - 25))
            
            # Draw direction indicator
            end_x = self.x + self.width/2 + math.cos(self.angle) * 30
            end_y = self.y + self.height/2 + math.sin(self.angle) * 30
            pygame.draw.line(surface, (0, 255, 0), 
                           (int(self.x + self.width/2), int(self.y + self.height/2)),
                           (int(end_x), int(end_y)), 2)
    
    def draw_with_camera(self, surface, camera_pos):
        """Draw the enemy with camera offset"""
        if not self.alive:
            return
        
        # Create a copy of the image for hit flash effect
        current_image = self.image.copy() if self.hit_flash == 0 else self.create_hit_effect()
        
        # Apply visual effects for status effects
        if self.stunned > 0:
            # Add stars or other stun indicator
            pygame.draw.circle(current_image, (255, 255, 0), (self.width//2, 5), 3)
            pygame.draw.circle(current_image, (255, 255, 0), (self.width//2-10, 5), 3)
            pygame.draw.circle(current_image, (255, 255, 0), (self.width//2+10, 5), 3)
        
        if self.slowed > 0:
            # Add blue tint for slowed
            blue_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            blue_overlay.fill((0, 0, 255, 50))
            current_image.blit(blue_overlay, (0, 0))
        
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
            
            # Draw current state text
            font = pygame.font.SysFont(None, 20)
            state_text = font.render(self.state, True, (255, 255, 255))
            surface.blit(state_text, (camera_pos[0], camera_pos[1] - 25))
    
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

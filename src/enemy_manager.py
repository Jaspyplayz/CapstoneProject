# EnemyManager.py
from src.constants import MAX_ENEMIES, SPAWN_DELAY, MAP_WIDTH, MAP_HEIGHT
from src.enemy import Enemy
import random
import pygame
import math
import time

class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_delay = SPAWN_DELAY
        self.max_enemies = MAX_ENEMIES
        self.debug_mode = False  # Toggle for showing hitboxes
        
        # Wave system
        self.current_wave = 1
        self.wave_timer = 0
        self.wave_duration = 1800  # 30 seconds at 60 FPS
        self.wave_cooldown = 300   # 5 seconds between waves
        self.in_wave_cooldown = False
        self.wave_start_time = time.time()
        
        # Enemy variety
        self.enemy_types = {
            "basic": {
                "speed": (1.0, 2.0),
                "health": (80, 120),
                "image": "enemies/basic_enemy.jpg",
                "weight": 100  # Spawn weight (higher = more common)
            },
            "fast": {
                "speed": (2.5, 3.5),
                "health": (50, 80),
                "image": "enemies/basic_enemy.jpg",  # Replace with actual fast enemy image
                "weight": 0    # Start at 0, will increase with waves
            },
            "tank": {
                "speed": (0.7, 1.2),
                "health": (150, 200),
                "image": "enemies/basic_enemy.jpg",  # Replace with actual tank enemy image
                "weight": 0    # Start at 0, will increase with waves
            },
            "boss": {
                "speed": (0.5, 0.8),
                "health": (400, 600),
                "image": "enemies/basic_enemy.jpg",  # Replace with actual boss enemy image
                "weight": 0    # Special spawn conditions
            }
        }
        
        # Spawn patterns
        self.spawn_patterns = [
            "random",       # Random positions around the map
            "surrounding",  # Surround the player
            "directional",  # All from one direction
            "corners"       # From map corners
        ]
        self.current_spawn_pattern = "random"
        
        # Special events
        self.special_events = {
            "horde": False,     # Many weak enemies
            "elite": False,     # Few strong enemies
            "boss_wave": False  # Boss with minions
        }
        
        # Statistics
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.last_spawn_positions = []  # Track recent spawn positions
        
        # Initialize wave
        self.update_wave_settings()

    def update(self):
        # Update wave system
        self.update_wave()
        
        # Create a list of enemies to remove after iteration
        enemies_to_remove = []
        
        for enemy in self.enemies:
            # Pass debug mode to enemy
            enemy.debug_mode = self.debug_mode
            enemy.update()

            # Keep enemy within map bounds
            enemy.x = max(0, min(enemy.x, MAP_WIDTH - enemy.width))
            enemy.y = max(0, min(enemy.y, MAP_HEIGHT - enemy.height))
            
            # Update enemy's rect position
            enemy.rect.x = int(enemy.x)
            enemy.rect.y = int(enemy.y)

            if not enemy.alive:
                enemies_to_remove.append(enemy)
                self.enemies_killed += 1
        
        # Remove dead enemies after iteration is complete
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)

        # Handle enemy spawning
        if not self.in_wave_cooldown:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay and len(self.enemies) < self.max_enemies:
                self.spawn_enemy()
                self.spawn_timer = 0

    def update_wave(self):
        """Update wave timer and handle wave transitions"""
        if self.in_wave_cooldown:
            self.wave_timer += 1
            if self.wave_timer >= self.wave_cooldown:
                # Start new wave
                self.current_wave += 1
                self.in_wave_cooldown = False
                self.wave_timer = 0
                self.wave_start_time = time.time()
                self.update_wave_settings()
                
                # Announce new wave
                print(f"Wave {self.current_wave} started!")
        else:
            self.wave_timer += 1
            if self.wave_timer >= self.wave_duration:
                # End current wave
                self.in_wave_cooldown = True
                self.wave_timer = 0
                
                # Clear all enemies when wave ends (optional)
                # self.enemies = []
                
                print(f"Wave {self.current_wave} completed! Next wave in {self.wave_cooldown/60} seconds.")

    def update_wave_settings(self):
        """Update enemy types and spawn settings based on current wave"""
        # Define these constants here instead of relying on undefined variables
        MIN_ENEMIES = 5
        
        # Adjust max enemies based on wave
        self.max_enemies = min(MIN_ENEMIES + self.current_wave, MAX_ENEMIES)
        
        # Adjust spawn delay (faster spawns in later waves)
        self.spawn_delay = max(SPAWN_DELAY - (self.current_wave * 2), 20)
        
        # Unlock enemy types based on wave
        if self.current_wave >= 3:
            self.enemy_types["fast"]["weight"] = 40
        if self.current_wave >= 5:
            self.enemy_types["tank"]["weight"] = 30
        if self.current_wave >= 10 and self.current_wave % 5 == 0:
            self.enemy_types["boss"]["weight"] = 10
            self.special_events["boss_wave"] = True
        
        # Select spawn pattern
        if self.current_wave % 3 == 0:
            self.current_spawn_pattern = "surrounding"
        elif self.current_wave % 4 == 0:
            self.current_spawn_pattern = "directional"
        elif self.current_wave % 5 == 0:
            self.current_spawn_pattern = "corners"
        else:
            self.current_spawn_pattern = "random"
            
        # Special events
        if self.current_wave % 7 == 0:
            self.special_events["horde"] = True
            self.max_enemies += 5
            self.spawn_delay = max(10, self.spawn_delay // 2)
        else:
            self.special_events["horde"] = False
            
        if self.current_wave % 6 == 0:
            self.special_events["elite"] = True
        else:
            self.special_events["elite"] = False

    def spawn_enemy(self):
        """Spawn a new enemy based on current settings"""
        # Select enemy type based on weights
        enemy_type = self.select_enemy_type()
        
        # Get spawn position based on pattern
        spawn_pos = self.get_spawn_position()
        
        # Get enemy properties
        speed_range = self.enemy_types[enemy_type]["speed"]
        health_range = self.enemy_types[enemy_type]["health"]
        image_path = self.enemy_types[enemy_type]["image"]
        
        # Adjust stats based on wave and special events
        wave_multiplier = 1.0 + (self.current_wave * 0.1)
        
        # Calculate stats
        speed = random.uniform(speed_range[0], speed_range[1])
        health = random.randint(int(health_range[0] * wave_multiplier), 
                               int(health_range[1] * wave_multiplier))
        
        # Apply special event modifiers
        if self.special_events["elite"] and random.random() < 0.3:
            # Elite enemy (stronger)
            speed *= 1.2
            health *= 1.5
            
        if self.special_events["horde"]:
            # Horde enemies (weaker but more numerous)
            health *= 0.7
            
        if enemy_type == "boss":
            # Boss enemies
            health *= 2.0
            # Spawn some minions around the boss
            self.spawn_minions(spawn_pos[0], spawn_pos[1])

        # Create the enemy
        enemy = Enemy(self.game, speed, health, spawn_pos[0], spawn_pos[1])
        enemy.debug_mode = self.debug_mode
        
        # Set enemy personality based on type
        if enemy_type == "basic":
            enemy.personality = random.choice(["aggressive", "cautious", "erratic", "flanker"])
        elif enemy_type == "fast":
            enemy.personality = random.choice(["aggressive", "flanker", "erratic"])
            enemy.detection_radius = 350  # Increased detection for fast enemies
        elif enemy_type == "tank":
            enemy.personality = random.choice(["aggressive", "cautious"])
            enemy.knockback_resistance = 0.8  # Tanks resist knockback
        elif enemy_type == "boss":
            enemy.personality = "aggressive"
            enemy.detection_radius = 500  # Boss has large detection radius
            enemy.knockback_resistance = 0.9  # Boss highly resists knockback
        
        # Add to enemy list
        self.enemies.append(enemy)
        self.enemies_spawned += 1
        
        # Remember spawn position to avoid clustering
        self.last_spawn_positions.append(spawn_pos)
        if len(self.last_spawn_positions) > 5:
            self.last_spawn_positions.pop(0)
            
        return enemy

    def select_enemy_type(self):
        """Select an enemy type based on weights"""
        # Calculate total weight
        total_weight = sum(self.enemy_types[enemy_type]["weight"] for enemy_type in self.enemy_types)
        
        if total_weight == 0:
            return "basic"  # Default if no weights set
            
        # Select based on weight
        r = random.randint(1, total_weight)
        current_weight = 0
        
        for enemy_type in self.enemy_types:
            current_weight += self.enemy_types[enemy_type]["weight"]
            if r <= current_weight:
                return enemy_type
                
        return "basic"  # Fallback

    def get_spawn_position(self):
        """Get spawn position based on current pattern"""
        player_x, player_y = self.game.player.x, self.game.player.y
        
        if self.current_spawn_pattern == "surrounding":
            # Spawn in a circle around the player
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(400, 600)
            x = player_x + math.cos(angle) * distance
            y = player_y + math.sin(angle) * distance
            
        elif self.current_spawn_pattern == "directional":
            # Spawn from one direction
            if not hasattr(self, 'current_direction'):
                self.current_direction = random.choice(["north", "south", "east", "west"])
                
            if self.current_direction == "north":
                x = random.randint(0, MAP_WIDTH)
                y = random.randint(0, 200)
            elif self.current_direction == "south":
                x = random.randint(0, MAP_WIDTH)
                y = random.randint(MAP_HEIGHT - 200, MAP_HEIGHT)
            elif self.current_direction == "east":
                x = random.randint(MAP_WIDTH - 200, MAP_WIDTH)
                y = random.randint(0, MAP_HEIGHT)
            else:  # west
                x = random.randint(0, 200)
                y = random.randint(0, MAP_HEIGHT)
                
        elif self.current_spawn_pattern == "corners":
            # Spawn from map corners
            corner = random.randint(0, 3)
            if corner == 0:  # Top-left
                x = random.randint(0, 300)
                y = random.randint(0, 300)
            elif corner == 1:  # Top-right
                x = random.randint(MAP_WIDTH - 300, MAP_WIDTH)
                y = random.randint(0, 300)
            elif corner == 2:  # Bottom-left
                x = random.randint(0, 300)
                y = random.randint(MAP_HEIGHT - 300, MAP_HEIGHT)
            else:  # Bottom-right
                x = random.randint(MAP_WIDTH - 300, MAP_WIDTH)
                y = random.randint(MAP_HEIGHT - 300, MAP_HEIGHT)
                
        else:  # random
            # Find a spawn position away from the player but within the map
            attempts = 0
            while attempts < 10:  # Limit attempts to prevent infinite loop
                x = random.randint(0, MAP_WIDTH - 50)
                y = random.randint(0, MAP_HEIGHT - 50)
                
                # Check distance from player
                distance = ((player_x - x) ** 2 + (player_y - y) ** 2) ** 0.5
                
                # Check distance from recent spawn positions to avoid clustering
                too_close_to_recent = False
                for pos in self.last_spawn_positions:
                    if ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5 < 150:
                        too_close_to_recent = True
                        break
                        
                if distance > 300 and not too_close_to_recent:
                    break
                    
                attempts += 1
        
        # Ensure spawn is within map bounds
        x = max(50, min(x, MAP_WIDTH - 50))
        y = max(50, min(y, MAP_HEIGHT - 50))
        
        return (x, y)

    def spawn_minions(self, boss_x, boss_y):
        """Spawn minions around a boss"""
        num_minions = random.randint(3, 5)
        
        for _ in range(num_minions):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(100, 200)
            x = boss_x + math.cos(angle) * distance
            y = boss_y + math.sin(angle) * distance
            
            # Ensure within map bounds
            x = max(50, min(x, MAP_WIDTH - 50))
            y = max(50, min(y, MAP_HEIGHT - 50))
            
            # Create minion (faster but weaker)
            speed = random.uniform(1.5, 2.5)
            health = random.randint(50, 80)
            
            minion = Enemy(self.game, speed, health, x, y)
            minion.debug_mode = self.debug_mode
            minion.personality = "aggressive"  # Minions are always aggressive
            
            self.enemies.append(minion)
            self.enemies_spawned += 1

    def draw(self, surface):
        for enemy in self.enemies:
            # Get camera-adjusted position
            camera_pos = self.game.camera.apply(enemy)
            
            # Only draw if on screen (with some margin)
            if (-100 <= camera_pos[0] <= self.game.screen.get_width() + 100 and 
                -100 <= camera_pos[1] <= self.game.screen.get_height() + 100):
                
                # Draw enemy at camera-adjusted position
                enemy.draw_with_camera(surface, camera_pos)
        
        # Draw wave information if in debug mode
        if self.debug_mode:
            font = pygame.font.SysFont(None, 24)
            
            # Wave info
            wave_text = font.render(f"Wave: {self.current_wave}", True, (255, 255, 255))
            surface.blit(wave_text, (10, 10))
            
            # Wave timer
            elapsed = time.time() - self.wave_start_time
            if self.in_wave_cooldown:
                timer_text = font.render(f"Next wave in: {(self.wave_cooldown - self.wave_timer) / 60:.1f}s", True, (255, 255, 255))
            else:
                timer_text = font.render(f"Wave time: {elapsed:.1f}s", True, (255, 255, 255))
            surface.blit(timer_text, (10, 30))
            
            # Enemy count
            count_text = font.render(f"Enemies: {len(self.enemies)}/{self.max_enemies}", True, (255, 255, 255))
            surface.blit(count_text, (10, 50))
            
            # Spawn pattern
            pattern_text = font.render(f"Pattern: {self.current_spawn_pattern}", True, (255, 255, 255))
            surface.blit(pattern_text, (10, 70))
            
            # Special events
            events = []
            for event, active in self.special_events.items():
                if active:
                    events.append(event)
            
            if events:
                events_text = font.render(f"Events: {', '.join(events)}", True, (255, 255, 0))
                surface.blit(events_text, (10, 90))
    
    def toggle_debug(self):
        """Toggle debug mode for hitbox visualization"""
        self.debug_mode = not self.debug_mode

    def get_stats(self):
        """Return statistics about enemies"""
        return {
            "current_wave": self.current_wave,
            "enemies_alive": len(self.enemies),
            "enemies_spawned": self.enemies_spawned,
            "enemies_killed": self.enemies_killed,
            "max_enemies": self.max_enemies,
            "spawn_delay": self.spawn_delay,
            "wave_time": time.time() - self.wave_start_time
        }

    def clear_all_enemies(self):
        """Remove all enemies (for level transitions, etc.)"""
        self.enemies = []

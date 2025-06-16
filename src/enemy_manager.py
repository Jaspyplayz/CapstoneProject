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
        
        # Wave system
        self.current_wave = 1
        self.wave_timer = 0
        self.wave_duration = 1800  # 30 seconds at 60 FPS
        self.wave_cooldown = 300   # 5 seconds between waves
        self.in_wave_cooldown = False
        self.wave_start_time = time.time()
        
        # Base enemy types - initial values for wave 1
        self.enemy_types = {
            "basic": {"color": (255, 0, 0), "speed": 1.5, "health": 100, "damage": 10},
            "fast": {"color": (0, 255, 0), "speed": 2.5, "health": 70, "damage": 8},
            "tank": {"color": (0, 0, 255), "speed": 0.8, "health": 180, "damage": 15}
        }
        
        # Scaling factors per wave
        self.scaling = {
            "health": 0.15,      # Health increases by 15% per wave
            "damage": 0.10,      # Damage increases by 10% per wave
            "speed": 0.05,       # Speed increases by 5% per wave
            "spawn_rate": 0.08   # Spawn rate increases by 8% per wave
        }
        
        # Wave-specific changes
        self.boss_waves = [5, 10, 15, 20]  # Waves that spawn boss enemies

    def update(self):
        # Update wave system
        self.update_wave()
        
        # Remove dead enemies
        enemies_to_remove = []
        for enemy in self.enemies:
            enemy.update()
            if not enemy.alive:
                enemies_to_remove.append(enemy)
                
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
        
        # Handle enemy spawning
        if not self.in_wave_cooldown:
            # Calculate spawn delay based on wave (gets faster as waves progress)
            current_spawn_delay = max(15, self.spawn_delay * (1 - (self.current_wave - 1) * self.scaling["spawn_rate"]))
            
            self.spawn_timer += 1
            if self.spawn_timer >= current_spawn_delay and len(self.enemies) < self.max_enemies:
                # Select enemy type with weighted probability
                enemy_type = self.select_enemy_type()
                
                # Get spawn position
                spawn_pos = self.get_spawn_position()
                if spawn_pos is not None:
                    x, y = spawn_pos
                    self.spawn_enemy(enemy_type, x, y)
                    self.spawn_timer = 0
        
        # Check for projectile collisions with player
        self.check_projectile_collisions()

    def check_projectile_collisions(self):
        """Check if any enemy projectiles hit the player"""
        for enemy in self.enemies:
            for projectile in enemy.projectiles[:]:
                if projectile.active and projectile.rect.colliderect(self.game.player.rect):
                    # Damage player
                    self.game.player.take_damage(projectile.damage)
                    
                    # Deactivate projectile
                    projectile.active = False

    def select_enemy_type(self):
        """Select enemy type with weighted probability based on current wave"""
        # Basic weights
        weights = {
            "basic": 70,
            "fast": 20,
            "tank": 10
        }
        
        # Adjust weights based on wave
        if self.current_wave >= 3:
            weights["basic"] = 60
            weights["fast"] = 25
            weights["tank"] = 15
            
        if self.current_wave >= 7:
            weights["basic"] = 50
            weights["fast"] = 30
            weights["tank"] = 20
            
        if self.current_wave >= 10:
            weights["basic"] = 40
            weights["fast"] = 35
            weights["tank"] = 25
            
        # Special case for boss waves
        if self.current_wave in self.boss_waves:
            # Increase chance of tanks on boss waves
            weights["basic"] = 30
            weights["fast"] = 30
            weights["tank"] = 40
            
            # Add boss enemy if it exists in the enemy types
            if "boss" in self.enemy_types:
                weights["boss"] = 15
                
        # Convert weights to a list for random.choices
        enemy_types = list(weights.keys())
        enemy_weights = list(weights.values())
        
        # Select and return an enemy type
        return random.choices(enemy_types, weights=enemy_weights, k=1)[0]

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
                
                # Update enemy types for the new wave
                self.update_enemy_types()
                
                # Spawn boss on boss waves
                if self.current_wave in self.boss_waves:
                    self.spawn_boss()
                    
                print(f"Wave {self.current_wave} started!")
        else:
            self.wave_timer += 1
            if self.wave_timer >= self.wave_duration:
                # End current wave
                self.in_wave_cooldown = True
                self.wave_timer = 0
                print(f"Wave {self.current_wave} completed!")

    def update_enemy_types(self):
        """Update enemy stats based on current wave"""
        # Define base stats for wave 1
        base_types = {
            "basic": {"color": (255, 0, 0), "speed": 1.5, "health": 100, "damage": 10},
            "fast": {"color": (0, 255, 0), "speed": 2.5, "health": 70, "damage": 8},
            "tank": {"color": (0, 0, 255), "speed": 0.8, "health": 180, "damage": 15}
        }
        
        # Calculate scaling factor based on current wave
        scale_factor = 1 + (self.current_wave - 1) * self.scaling["health"]
        speed_factor = 1 + (self.current_wave - 1) * self.scaling["speed"]
        damage_factor = 1 + (self.current_wave - 1) * self.scaling["damage"]
        
        # Update each enemy type
        for enemy_type, stats in base_types.items():
            self.enemy_types[enemy_type] = {
                "color": stats["color"],
                "speed": stats["speed"] * speed_factor,
                "health": int(stats["health"] * scale_factor),
                "damage": int(stats["damage"] * damage_factor)
            }
            
        # Add boss type on boss waves
        if self.current_wave in self.boss_waves:
            boss_health = int(400 * scale_factor)
            boss_damage = int(25 * damage_factor)
            
            self.enemy_types["boss"] = {
                "color": (128, 0, 128),  # Purple
                "speed": 1.0 * speed_factor,
                "health": boss_health,
                "damage": boss_damage
            }
            
        # Print stats for debugging
        print(f"Wave {self.current_wave} enemy stats:")
        for enemy_type, stats in self.enemy_types.items():
            print(f"  {enemy_type}: Health={stats['health']}, Speed={stats['speed']:.2f}, Damage={stats['damage']}")

    def spawn_boss(self):
        """Spawn a boss enemy"""
        # Get spawn position
        spawn_pos = self.get_spawn_position()
        if spawn_pos is not None:
            x, y = spawn_pos
            boss = self.spawn_enemy("boss", x, y)
            
            # Make boss bigger
            boss.width = boss.height = 60
            boss.rect = pygame.Rect(int(boss.x), int(boss.y), boss.width, boss.height)
            
            # Create a new image for the boss
            boss.image = boss.create_enemy_surface()
            boss.mask = pygame.mask.from_surface(boss.image)
            
            print(f"Boss spawned with {boss.health} health!")
            return boss
        return None

    def spawn_enemy(self, enemy_type, x, y):
        """Spawn a new enemy of the specified type"""
        # Get enemy properties from type
        properties = self.enemy_types[enemy_type]
        
        # Create enemy with the proper type
        enemy = Enemy(self.game, properties["speed"], properties["health"], enemy_type, x, y)
        
        # Set enemy color
        enemy.color = properties["color"]
        
        # Set damage
        enemy.damage = properties.get("damage", 10)
        
        # Set projectile properties based on enemy type
        if enemy_type == "basic":
            enemy.projectile_color = (255, 100, 100)  # Light red
            enemy.attack_cooldown_max = 120           # 2 seconds at 60 FPS
            enemy.projectile_speed = 5
            enemy.projectile_damage = properties.get("damage", 10) * 0.5  # Half of contact damage
            enemy.projectile_range = 600
            
        elif enemy_type == "fast":
            enemy.projectile_color = (100, 255, 100)  # Light green
            enemy.attack_cooldown_max = 90            # 1.5 seconds at 60 FPS
            enemy.projectile_speed = 7
            enemy.projectile_damage = properties.get("damage", 8) * 0.4   # Less damage
            enemy.projectile_range = 500
            
        elif enemy_type == "tank":
            enemy.projectile_color = (100, 100, 255)  # Light blue
            enemy.attack_cooldown_max = 180           # 3 seconds at 60 FPS
            enemy.projectile_speed = 4
            enemy.projectile_damage = properties.get("damage", 15) * 0.6  # More damage
            enemy.projectile_range = 700
            
        elif enemy_type == "boss":
            enemy.projectile_color = (200, 50, 200)   # Purple
            enemy.attack_cooldown_max = 60            # 1 second at 60 FPS
            enemy.projectile_speed = 6
            enemy.projectile_damage = properties.get("damage", 25) * 0.5  # High damage
            enemy.projectile_range = 800
            enemy.attack_range = 400                  # Longer attack range
        
        # Set size based on type
        if enemy_type == "basic":
            enemy.width = enemy.height = 30
        elif enemy_type == "fast":
            enemy.width = enemy.height = 25
        elif enemy_type == "tank":
            enemy.width = enemy.height = 40
        elif enemy_type == "boss":
            enemy.width = enemy.height = 60
            
        # Update rect size
        enemy.rect = pygame.Rect(int(enemy.x), int(enemy.y), enemy.width, enemy.height)
        
        # Try to load the image first
        enemy.image = enemy.load_image()
        
        # If image loading failed, create a fallback surface
        if enemy.image is None:
            enemy.image = enemy.create_enemy_surface()
            
        # Create mask for collision detection
        enemy.mask = pygame.mask.from_surface(enemy.image)
        
        # Add enemy to the list
        self.enemies.append(enemy)
        return enemy

    def get_spawn_position(self):
        """Get spawn position around the player"""
        player_x, player_y = self.game.player.x, self.game.player.y
        
        # Define minimum and maximum spawn distance from player
        min_distance = 200
        max_distance = 500
        
        # Random position around player
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(min_distance, max_distance)
        x = player_x + math.cos(angle) * distance
        y = player_y + math.sin(angle) * distance
        
        # Ensure spawn is within map bounds
        x = max(50, min(x, MAP_WIDTH - 50))
        y = max(50, min(y, MAP_HEIGHT - 50))
        
        return (x, y)

    def draw(self, surface):
        for enemy in self.enemies:
            # Get camera-adjusted position
            camera_pos = self.game.camera.apply(enemy)
            
            # Only draw if on screen (with some margin)
            if (-100 <= camera_pos[0] <= self.game.screen.get_width() + 100 and 
                -100 <= camera_pos[1] <= self.game.screen.get_height() + 100):
                
                # Draw enemy at camera-adjusted position
                enemy.draw_with_camera(surface, camera_pos)
                
                # Draw health bar
                self.draw_health_bar(surface, enemy, camera_pos)
                
                # Draw enemy type indicator (optional)
                if self.current_wave >= 5:  # Only show enemy type after wave 5
                    self.draw_enemy_type(surface, enemy, camera_pos)
                
                # Draw enemy projectiles
                for projectile in enemy.projectiles:
                    if projectile.active:
                        # Calculate projectile's camera position
                        proj_camera_x = projectile.x - self.game.camera.x
                        proj_camera_y = projectile.y - self.game.camera.y
                        proj_camera_pos = (proj_camera_x, proj_camera_y)
                        
                        # Draw projectile with camera offset
                        projectile.draw_with_camera(surface, proj_camera_pos)

    def draw_health_bar(self, surface, enemy, camera_pos):
        """Draw health bar above enemy"""
        bar_width = enemy.width
        bar_height = 5
        
        # Position above enemy
        bar_x = camera_pos[0]
        bar_y = camera_pos[1] - 10
        
        # Background (red)
        pygame.draw.rect(surface, (255, 0, 0), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health (green)
        health_width = (enemy.health / enemy.max_health) * bar_width
        pygame.draw.rect(surface, (0, 255, 0), 
                        (bar_x, bar_y, health_width, bar_height))

    def draw_enemy_type(self, surface, enemy, camera_pos):
        """Draw a small indicator of enemy type"""
        if enemy.enemy_type == "boss":
            # Draw a crown for boss
            points = [
                (camera_pos[0] + enemy.width//2, camera_pos[1] - 15),
                (camera_pos[0] + enemy.width//2 - 10, camera_pos[1] - 5),
                (camera_pos[0] + enemy.width//2 + 10, camera_pos[1] - 5)
            ]
            pygame.draw.polygon(surface, (255, 215, 0), points)  # Gold color

    def clear_all_enemies(self):
        """Remove all enemies"""
        for enemy in self.enemies:
            # Deactivate all projectiles
            for projectile in enemy.projectiles:
                projectile.active = False
        self.enemies = []

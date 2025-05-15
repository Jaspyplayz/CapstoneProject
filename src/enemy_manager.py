# EnemyManager.py
from src.constants import MAX_ENEMIES, SPAWN_DELAY, MAP_WIDTH, MAP_HEIGHT
from src.enemy import Enemy
import random
import pygame

class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_delay = SPAWN_DELAY
        self.max_enemies = MAX_ENEMIES
        self.enemy_type = []  # For future enemy type variations
        self.debug_mode = False  # Toggle for showing hitboxes

    def update(self):
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
            enemy.rect.x = enemy.x
            enemy.rect.y = enemy.y

            if not enemy.alive:
                enemies_to_remove.append(enemy)
        
        # Remove dead enemies after iteration is complete
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)

        # Handle enemy spawning
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay and len(self.enemies) < self.max_enemies:
            self.spawn_enemy()
            self.spawn_timer = 0

    def spawn_enemy(self):
        player_x, player_y = self.game.player.x, self.game.player.y

        # Find a spawn position away from the player but within the map
        while True:
            # Use MAP dimensions instead of SCREEN dimensions
            x = random.randint(0, MAP_WIDTH - 50)
            y = random.randint(0, MAP_HEIGHT - 50)

            distance = ((player_x - x) ** 2 + (player_y - y) ** 2) ** 0.5

            if distance > 300:  # Ensure enemies spawn at least 300px away from player
                break

        speed = random.uniform(1.0, 3.0)
        health = random.randint(80, 120)

        enemy = Enemy(self.game, speed, health, x, y)
        enemy.debug_mode = self.debug_mode
        self.enemies.append(enemy)

    def draw(self, surface):
        for enemy in self.enemies:
            # Get camera-adjusted position
            camera_pos = self.game.camera.apply(enemy)
            
            # Only draw if on screen (with some margin)
            if (-100 <= camera_pos[0] <= self.game.screen.get_width() + 100 and 
                -100 <= camera_pos[1] <= self.game.screen.get_height() + 100):
                
                # Draw enemy at camera-adjusted position
                enemy.draw_with_camera(surface, camera_pos)
    
    def toggle_debug(self):
        """Toggle debug mode for hitbox visualization"""
        self.debug_mode = not self.debug_mode

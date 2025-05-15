from src.constants import MAX_ENEMIES, SPAWN_DELAY, SCREEN_HEIGHT, SCREEN_WIDTH
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
            enemy.update()

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

        # Find a spawn position away from the player
        while True:
            x = random.randint(0, SCREEN_WIDTH - 50)
            y = random.randint(0, SCREEN_HEIGHT - 50)

            distance = ((player_x - x) ** 2 + (player_y - y) ** 2) ** 0.5

            if distance > 200:  # Ensure enemies spawn at least 200px away from player
                break

        speed = random.uniform(1.0, 3.0)
        health = random.randint(80, 120)

        enemy = Enemy(self.game, speed, health, x, y)
        self.enemies.append(enemy)

    def draw(self, surface):
        for enemy in self.enemies:
            enemy.draw(surface)
            
            # Draw hitboxes in debug mode
            if self.debug_mode:
                pygame.draw.rect(surface, (255, 0, 255), enemy.rect, 1)
                # Draw a point at the center for reference
                pygame.draw.circle(surface, (255, 255, 0), 
                                  (enemy.rect.centerx, enemy.rect.centery), 2)

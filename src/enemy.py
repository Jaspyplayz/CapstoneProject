import pygame
import random
import math
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, RED, GREEN

class Enemy:

    def __init__(self, game, speed, health, x = None , y = None):

        self.game = game

        #Enemy coordinate spawnpoint 
        self.x = x if x is not None else random.randint(0, SCREEN_WIDTH - 50)
        self.y = y if y is not None else random.randint(0, SCREEN_HEIGHT - 50)

        #Enemy properties
        self.width = 40
        self.height = 40
        self.speed = speed
        self.health = health
        self.max_health = health

        #Load enemies image

        self.image = self.game.assets.load_image("enemy", "enemies/basic_enemy.jpg")
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


        #movement vectors

        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = random.uniform(0, 2 * math.pi)
        self.set_velocity_from_angle()

        #Direction change timer

        self.direction_change_timer = 0
        self.direction_change_delay = random.randint(60, 120)

        #Sound effects

        self.hit_sound = "enemy_hit"
        self.death_sound = "enemy_death"

        #State

        self.alive = True
    
    def set_velocity_from_angle(self):

        self.velocity_x = math.cos(self.angle) * self.speed
        self.velocity_y = math.sin(self.angle) * self.speed

    def update(self):
        
        #If enemy is not alive then return and don't update
        if not self.alive:
            return 
        
        #handle direction changes

        self.direction_change_timer += 1

        if self.direction_change_timer >= self.direction_change_delay:
            self.change_direction()
            self.direction_change_timer = 0


        #Move based on velocity

        self.x += self.velocity_x
        self.y += self.velocity_y

        if self.x < 0:
            self.x = 0
            self.bounce_horizontal()
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.bounce_horizontal()

        if self.y < 0:
            self.y = 0
            self.bounce_vertical()
        elif self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.bounce_vertical()

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def bounce_horizontal(self):
        self.angle = math.pi - self.angle
        self.set_velocity_from_angle()
    
    def bounce_vertical(self):
        self.angle = -self.angle
        self.set_velocity_from_angle()

    def change_direction(self):

        self.angle = random.uniform(0, 2 * math.pi )
        self.set_velocity_from_angle()
        self.direction_change_delay = random.randint(60, 120)

    def seek_player(self, player_x, player_y, aggression = 0.5):

        dx = player_x - self.x
        dy = player_y - self.y
        angle_to_player = math.atan2(dy, dx)

        self.angle = (1-aggression) * self.angle + aggression * angle_to_player
        self.angle += random.uniform(-0.3, 0.3)

        self.set_velocity_from_angle()

    def take_damage(self, amount):

        if not self.alive:
            return
        
        self.health -= amount

        self.game.assets.play_sound(self.hit_sound)

        if self.health <= 0:
            self.die()

    def die(self):

        self.alive = False
        
        self.game.assets.play_sound(self.death_sound)

        self.game.score += 100

    def draw(self, surface):

        if not self.alive:
            return
        
        surface.blit(self.image, (self.x, self.y))

        health_bar_width = 10
        health_ratio = self.health / self.max_health

        pygame.draw.rect(surface, RED, (self.x+5, self.y-10, health_bar_width, 5))
        pygame.draw.rect(surface, GREEN, (self.x+5, self.y-10, health_bar_width * health_ratio, 5))

    


        
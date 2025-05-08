import pygame
import math

class Player:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = (255,0,0)
        self.speed = 5

        self.target_x = x
        self.target_y = y
        self.moving = False
    
    def set_destination(self, x, y):

        self.target_x = x
        self.target_y = y
        self.moving = True

    def update(self):

        dx = self.target_x - (self.x + self.width/2)
        dy = self.target_y - (self.y + self.height/2)

        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.speed:
            self.x = self.target_x - self.width/2
            self.y = self.target_y - self.height/2
            self.moving = False
            return
        
        dx = dx / distance * self.speed
        dy = dy / distance * self.speed

        self.x += dx
        self.y += dy

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

        if self.moving and self.target_x is not None and self.target_y is not None:
            pygame.draw.line(screen, (0,255,0), (self.x + self.width/2, self.y + self.height/2), (self.target_x, self.target_y), 1)

        
# Create a new file: src/camera.py
import pygame
class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        
    def update(self, target_x, target_y, screen_width, screen_height):
        """Update camera position to follow a target"""
        # Center the camera on the target
        self.x = target_x - screen_width // 2
        self.y = target_y - screen_height // 2
        
        # Keep camera within map bounds
        self.x = max(0, min(self.x, self.width - screen_width))
        self.y = max(0, min(self.y, self.height - screen_height))
    
    def apply(self, entity):
        """Adjust entity's drawing position based on camera"""
        return (entity.x - self.x, entity.y - self.y)
    
    def apply_rect(self, rect):
        """Adjust a rect's position based on camera"""
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

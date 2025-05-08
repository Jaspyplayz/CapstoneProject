from GameState import GameState
from MenuState import MenuState
import pygame

class PlayState(GameState):
    
    def __init__(self, game):
        super().__init__(game)
        self.options = ["Play", "Options", "Quit"]
        self.selected = 0

    def handle_events(self, events):
        
        for event in pygame.event.get():
            #Point and click right click movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.player.set_destination(mouse_x, mouse_y)

    def render(self, screen):
        
        pass


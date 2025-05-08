from GameState import GameState
from PlayState import PlayState
import pygame

class MenuState(GameState):
    
    def __init__(self, game):
        super().__init__(game)
        self.options = ["Play", "Options", "Quit"]
        self.selected = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.options[self.selected] == "Play":
                        self.game.change_state(PlayState(self.game))
                    elif self.options[self.selected] == "Quit":
                        self.game.running = False

    def render(self, screen):
        
        pass


from game_states.game_state import GameState
import pygame

class PlayState(GameState):
    
    def __init__(self, game):
        super().__init__(game)
        self.player = game.player

    def handle_events(self, events):
        
        for event in events:
            #Point and click right click movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.player.set_destination(mouse_x, mouse_y)

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.game.change_state("pause", previous_state = self)
    
    def update(self):
        self.player.update()

    def render(self, screen):
        
        screen.fill((0,0,0))

        self.player.draw(screen)


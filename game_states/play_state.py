from game_states.game_state import GameState
import pygame

class PlayState(GameState):
    
    def __init__(self, game):
        super().__init__(game)

        self.player = game.player

        self.options = ["Play", "Options", "Quit"]
        self.selected = 0

    def handle_events(self, events):
        
        for event in events:
            #Point and click right click movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.player.set_destination(mouse_x, mouse_y)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:

                    from game_states.menu_state import MenuState
                    self.game.change_state(MenuState(self.game))
    
    def update(self):
        self.player.update()

    def render(self, screen):
        
        screen.fill((0,0,0))

        self.player.draw(screen)


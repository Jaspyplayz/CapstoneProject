from game_states.game_state import GameState
import pygame

class PausedState(GameState):
    
    def __init__(self, game, previous_state):
        super().__init__(game)

        self.previous_state = previous_state

        self.options = ["Resume", "Options", "Quit to Menu", "Quit"]
        self.selected = 0

        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        self.selected_color = (255, 255, 0)
        self.normal_color = (255, 255, 255)

        self.overlay = pygame.Surface((self.game.screen.get_width(), self.game.screen.get_height()))
        self.overlay.set_alpha(120)
        self.overlay.fill((0,0,0))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.select_option()
                elif event.key == pygame.K_ESCAPE:
                    self.resume_game()

    def select_option(self):

        if self.options[self.selected] == "Resume":
            self.resume_game()
        elif self.options[self.selected] == "Options":
            pass
        elif self.options[self.selected] == "Quit to Menu":
            self.game.reset_game()
            self.game.change_state("menu")
        elif self.options[self.selected] == "Quit":
            self.game.running = False

    def resume_game(self):

        self.game.state = self.previous_state

    def update(self):

        pass

    def render(self, screen):

        self.previous_state.render(screen)

        screen.blit(self.overlay, (0,0))

        title = self.title_font.render("PAUSED", True, (255,255,255))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)

        menu_y = 300

        for i, option in enumerate(self.options):

            color = self.selected_color if i == self.selected else self.normal_color
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, menu_y + i * 60))
            screen.blit(text, text_rect)

            if i == self.selected:
                pygame.draw.circle(screen, color, (text_rect.left - 20, text_rect.centery), 7)

        
        


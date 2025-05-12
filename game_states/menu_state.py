import pygame
from game_states.game_state import GameState
from src.constants import (
    WHITE, YELLOW, STATE_PLAY, STATE_OPTIONS,
    TITLE_FONT_SIZE, DEFAULT_FONT, NORMAL_FONT_SIZE, HEADING_FONT_SIZE,
    MENU_START_Y, MENU_SPACING
)


class MenuState(GameState):
    
    def __init__(self, game):
        super().__init__(game)
        self.options = ["Play", "Options", "Quit"]
        self.selected = 0

        self.selected_color = YELLOW
        self.normal_color = WHITE

        try:
            self.font = pygame.font.Font(DEFAULT_FONT, NORMAL_FONT_SIZE)
            self.title_font = pygame.font.Font(DEFAULT_FONT, TITLE_FONT_SIZE)
            self.subtitle_font = pygame.font.Font(DEFAULT_FONT, HEADING_FONT_SIZE)
        
        except:
            self.font = pygame.font.Font(None, 48)
            self.title_font = pygame.font.Font(None, 72)
            self.subtitle_font = pygame.font.Font(None, 72)

        game.assets.play_music()


    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                    self.game.assets.sounds["hover"].play()
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                    self.game.assets.sounds["hover"].play()
                elif event.key == pygame.K_RETURN:
                    self.game.assets.sounds["select"].play()
                    self.select_option()
                    

    def select_option(self):

        if self.options[self.selected] == "Play":
            self.game.change_state(STATE_PLAY)
        elif self.options[self.selected] == "Options":
            self.game.change_state(STATE_OPTIONS)
        elif self.options[self.selected] == "Quit":
            self.game.running = False

    def update(self):

        pass

    def render(self, screen):

        screen.fill((0,0,0))

        title = self.title_font.render("League of Legends", True, (100,200,255))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)

        subtitle = self.subtitle_font.render("Main Menu", True, (80, 160, 200))
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, title_rect.bottom + 50))
        screen.blit(subtitle, subtitle_rect)

        menu_y = MENU_START_Y
        for i, option in enumerate(self.options):

            color = self.selected_color if i == self.selected else self.normal_color
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, menu_y + i * MENU_SPACING))
            screen.blit(text, text_rect)

            if i == self.selected:
                pygame.draw.circle(screen, color, (text_rect.left - 20, text_rect.centery), 7)
        
        


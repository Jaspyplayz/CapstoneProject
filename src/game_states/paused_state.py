from src.game_states.game_state import GameState
import pygame
import os
from src.constants import (
    WHITE, YELLOW, DEFAULT_FONT, NORMAL_FONT_SIZE, HEADING_FONT_SIZE,
    MENU_START_Y, MENU_SPACING, FONT_DIR, UI_ACCENT, UI_BACKGROUND
)

class PausedState(GameState):
    
    def __init__(self, game, **kwargs):
        super().__init__(game)

        self.previous_state = kwargs.get("previous_state", game.state)

        self.options = ["Resume", "Options", "Quit to Menu", "Quit"]
        self.selected = 0
        self.option_rects = []  # Store rectangles for mouse interaction

        # Use custom font
        try:
            self.font = pygame.font.Font(DEFAULT_FONT, NORMAL_FONT_SIZE)
            self.title_font = pygame.font.Font(DEFAULT_FONT, HEADING_FONT_SIZE)
            self.instruction_font = pygame.font.Font(DEFAULT_FONT, 24)
        except Exception as e:
            print(f"Error loading custom font: {e}")
            # Fallback to original font loading
            try:
                font_path = os.path.join(FONT_DIR, DEFAULT_FONT)
                self.font = pygame.font.Font(font_path, NORMAL_FONT_SIZE)
                self.title_font = pygame.font.Font(font_path, HEADING_FONT_SIZE)
                self.instruction_font = pygame.font.Font(font_path, 24)
            except Exception as e:
                print(f"Error loading fallback font: {e}")
                self.font = pygame.font.Font(None, NORMAL_FONT_SIZE)
                self.title_font = pygame.font.Font(None, HEADING_FONT_SIZE)
                self.instruction_font = pygame.font.Font(None, 24)
            
        self.selected_color = YELLOW
        self.normal_color = WHITE

        # Create semi-transparent overlay
        self.overlay = pygame.Surface((self.game.screen.get_width(), self.game.screen.get_height()))
        self.overlay.set_alpha(120)
        self.overlay.fill(UI_BACKGROUND)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                    self.game.assets.play_sound("hover")
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                    self.game.assets.play_sound("hover")
                elif event.key == pygame.K_RETURN:
                    self.select_option()
                    self.game.assets.play_sound("select")
                elif event.key == pygame.K_ESCAPE:
                    self.resume_game()
                    self.game.assets.play_sound("back")
            
            # Handle mouse movement for hover effect
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        if self.selected != i:
                            self.selected = i
                            self.game.assets.play_sound("hover")
            
            # Handle mouse clicks
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected = i
                        self.select_option()
                        self.game.assets.play_sound("select")
                        break

    def select_option(self):
        if self.options[self.selected] == "Resume":
            self.resume_game()
        elif self.options[self.selected] == "Options":
            self.game.change_state("options", previous_state=self)
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
        # Render the previous state first (game screen)
        self.previous_state.render(screen)

        # Apply semi-transparent overlay
        screen.blit(self.overlay, (0, 0))

        # Render pause title
        title = self.title_font.render("PAUSED", True, UI_ACCENT)
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)

        # Reset option rects
        self.option_rects = []
        
        # Render menu options
        menu_y = MENU_START_Y

        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected else self.normal_color
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, menu_y + i * MENU_SPACING))
            screen.blit(text, text_rect)
            
            # Store the rectangle for mouse detection (make hitbox slightly larger)
            self.option_rects.append(text_rect.inflate(40, 20))

            # Selection indicator
            if i == self.selected:
                pygame.draw.circle(screen, color, (text_rect.left - 20, text_rect.centery), 7)
                
        # Instructions
        instructions = [
            "↑↓: Navigate",
            "Enter: Select",
            "Esc: Resume Game",
            "Mouse: Click to select"
        ]
        
        instruction_y = screen.get_height() - 100
        for instruction in instructions:
            text = self.instruction_font.render(instruction, True, (180, 180, 180))
            text_rect = text.get_rect(center=(screen.get_width() // 2, instruction_y))
            screen.blit(text, text_rect)
            instruction_y += 20
            
        # Debug: Uncomment to see clickable areas
        # for rect in self.option_rects:
        #     pygame.draw.rect(screen, (255, 0, 0), rect, 1)

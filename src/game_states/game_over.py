import pygame
from src.game_states.game_state import GameState
from src.constants import (
    WHITE, YELLOW, STATE_MENU, STATE_PLAY,
    TITLE_FONT_SIZE, DEFAULT_FONT, NORMAL_FONT_SIZE, HEADING_FONT_SIZE,
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS
)

class GameOverState(GameState):
    def __init__(self, game, score=0):
        super().__init__(game)
        self.score = score
        
        # Define colors
        self.title_color = (255, 0, 0)  # Red for Game Over
        self.score_color = WHITE
        self.button_color = (70, 130, 180)  # Steel blue
        self.button_hover_color = (100, 160, 210)
        self.quit_button_color = (180, 70, 70)  # Reddish
        self.quit_button_hover_color = (210, 100, 100)
        
        # Load fonts
        try:
            self.title_font = pygame.font.Font(DEFAULT_FONT, TITLE_FONT_SIZE)
            self.score_font = pygame.font.Font(DEFAULT_FONT, HEADING_FONT_SIZE)
            self.button_font = pygame.font.Font(DEFAULT_FONT, NORMAL_FONT_SIZE)
        except:
            self.title_font = pygame.font.Font(None, 84)
            self.score_font = pygame.font.Font(None, 64)
            self.button_font = pygame.font.Font(None, 36)
        
        # Prepare text surfaces
        self.title_text = self.title_font.render("Game Over", True, self.title_color)
        
        # Button dimensions and positions
        button_width = 200
        button_height = 60
        button_spacing = 20
        
        # Create buttons
        self.buttons = {
            "retry": {
                "rect": pygame.Rect((SCREEN_WIDTH - button_width) // 2, 
                                    SCREEN_HEIGHT // 2 + 50, 
                                    button_width, button_height),
                "text": "Retry",
                "action": self.retry_game,
                "color": self.button_color,
                "hover_color": self.button_hover_color
            },
            "main_menu": {
                "rect": pygame.Rect((SCREEN_WIDTH - button_width) // 2, 
                                    SCREEN_HEIGHT // 2 + 50 + button_height + button_spacing, 
                                    button_width, button_height),
                "text": "Main Menu",
                "action": self.go_to_main_menu,
                "color": self.button_color,
                "hover_color": self.button_hover_color
            },
            "quit": {
                "rect": pygame.Rect((SCREEN_WIDTH - button_width) // 2, 
                                    SCREEN_HEIGHT // 2 + 50 + (button_height + button_spacing) * 2, 
                                    button_width, button_height),
                "text": "Quit Game",
                "action": self.quit_game,
                "color": self.quit_button_color,
                "hover_color": self.quit_button_hover_color
            }
        }
        
        # Animation variables
        self.fade_alpha = 0
        self.fade_speed = 5
        self.score_counter = 0
        self.score_speed = max(1, self.score // 100)  # Adjust speed based on score
        
        # Initialize score text
        self.update_score_text()
        
        # Track last hovered button
        self.last_hovered = None
        
        # Play game over sound if available
        try:
            self.game.assets.play_sound("game_over")
        except:
            pass
    
    def update_score_text(self):
        """Update the score text surface with the current counter value"""
        self.score_text = self.score_font.render(f"Score: {self.score_counter}", True, self.score_color)
        
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if any button was clicked
                for button_name, button in self.buttons.items():
                    if button["rect"].collidepoint(mouse_pos):
                        try:
                            self.game.assets.play_sound("select")
                        except:
                            pass
                        button["action"]()
                        
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_to_main_menu()
                elif event.key == pygame.K_RETURN:
                    self.retry_game()
    
    def update(self):
        # Handle fade in animation
        if self.fade_alpha < 255:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha > 255:
                self.fade_alpha = 255
        
        # Handle score counting animation
        if self.score_counter < self.score:
            self.score_counter += self.score_speed
            if self.score_counter > self.score:
                self.score_counter = self.score
            self.update_score_text()
    
    def render(self, screen):
        # Draw dark background
        screen.fill((20, 20, 40))
        
        # Draw title and score with fade effect
        title_alpha = min(255, self.fade_alpha * 2)
        score_alpha = max(0, min(255, (self.fade_alpha - 50) * 2))
        
        title_surface = self.title_text.copy()
        title_surface.set_alpha(title_alpha)
        
        score_surface = self.score_text.copy()
        score_surface.set_alpha(score_alpha)
        
        title_x = (SCREEN_WIDTH - self.title_text.get_width()) // 2
        score_x = (SCREEN_WIDTH - self.score_text.get_width()) // 2
        
        screen.blit(title_surface, (title_x, SCREEN_HEIGHT // 4))
        screen.blit(score_surface, (score_x, SCREEN_HEIGHT // 4 + 100))
        
        # Draw buttons with fade effect
        button_alpha = max(0, min(255, (self.fade_alpha - 100) * 2))
        mouse_pos = pygame.mouse.get_pos()
        
        for button_name, button in self.buttons.items():
            # Create button surface with transparency
            button_surface = pygame.Surface((button["rect"].width, button["rect"].height), pygame.SRCALPHA)
            
            # Determine button color (hover or normal)
            color = button["hover_color"] if button["rect"].collidepoint(mouse_pos) else button["color"]
            
            # Draw button on the surface
            pygame.draw.rect(button_surface, (*color, button_alpha), 
                          (0, 0, button["rect"].width, button["rect"].height))
            pygame.draw.rect(button_surface, (255, 255, 255, button_alpha), 
                          (0, 0, button["rect"].width, button["rect"].height), 2)  # White border
            
            # Draw button text
            text_surf = self.button_font.render(button["text"], True, (255, 255, 255))
            text_surf.set_alpha(button_alpha)
            text_rect = text_surf.get_rect(center=(button["rect"].width // 2, button["rect"].height // 2))
            button_surface.blit(text_surf, text_rect)
            
            # Draw the button surface to the screen
            screen.blit(button_surface, button["rect"].topleft)
            
            # Add hover effect - play sound when hovering over buttons
            if button["rect"].collidepoint(mouse_pos) and hasattr(self, 'last_hovered') and self.last_hovered != button_name:
                try:
                    self.game.assets.play_sound("hover")
                except:
                    pass
                self.last_hovered = button_name
            
        if not any(button["rect"].collidepoint(mouse_pos) for button in self.buttons.values()):
            self.last_hovered = None
    
    def retry_game(self):
        # Reset the game and start a new play session
        self.game.reset_game()
        self.game.change_state(STATE_PLAY)
    
    def go_to_main_menu(self):
        # Return to the main menu
        self.game.change_state(STATE_MENU)
    
    def quit_game(self):
        # Exit the game
        self.game.running = False

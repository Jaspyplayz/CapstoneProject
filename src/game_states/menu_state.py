import pygame
from src.game_states.game_state import GameState
from src.constants import (
    WHITE, YELLOW, STATE_PLAY, STATE_OPTIONS, STATE_CHAMPION_SELECT,
    TITLE_FONT_SIZE, DEFAULT_FONT, NORMAL_FONT_SIZE, HEADING_FONT_SIZE,
    MENU_START_Y, MENU_SPACING, FPS
)


class MenuState(GameState):
    
    def __init__(self, game):
        super().__init__(game)
        # Add "Champion Select" option between "Play" and "Options"
        self.options = ["Play", "Champion Select", "Options", "Quit"]
        self.selected = 0  # Keyboard selection
        self.hovered = -1  # Mouse hover (-1 means no hover)
        self.option_rects = []  # Store rectangles for mouse detection

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
        
        # Load the background image
        try:
            self.bg_image = pygame.image.load("assets/images/backgrounds/menu_bg.png").convert()
            # Scale the image to match the screen size
            self.bg_image = pygame.transform.scale(self.bg_image, 
                                                  (game.screen.get_width(), game.screen.get_height()))
        except (pygame.error, FileNotFoundError):
            print("Warning: Menu background image not found. Using solid color instead.")
            self.bg_image = None
            
        game.assets.play_music()

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
                    self.game.assets.play_sound("select")
                    self.select_option(self.selected)
            
            # Handle mouse movement for hover effect
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                old_hovered = self.hovered
                self.hovered = -1  # Reset hover
                
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.hovered = i
                        break
                
                # Play sound only if hover changed
                if old_hovered != self.hovered and self.hovered != -1:
                    self.game.assets.play_sound("hover")
            
            # Handle mouse clicks
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.game.assets.play_sound("select")
                        self.select_option(i)
                        break

    def select_option(self, option_index):
        if self.options[option_index] == "Play":
            self.game.change_state(STATE_PLAY)
        elif self.options[option_index] == "Champion Select":
            # Add this new option to navigate to the champion select screen
            self.game.change_state(STATE_CHAMPION_SELECT)
        elif self.options[option_index] == "Options":
            self.game.change_state(STATE_OPTIONS)
        elif self.options[option_index] == "Quit":
            self.game.running = False

    def update(self):
        pass

    def render(self, screen):
        # Draw the background image or fill with black if no image
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
            screen.fill((0, 0, 0))
            
        # Add a semi-transparent overlay to make text more readable if needed
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("League of Legends", True, (100, 200, 255))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)

        subtitle = self.subtitle_font.render("Main Menu", True, (80, 160, 200))
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, title_rect.bottom + 50))
        screen.blit(subtitle, subtitle_rect)

        menu_y = MENU_START_Y
        self.option_rects = []  # Reset option rects each frame
        
        for i, option in enumerate(self.options):
            # Determine color based on keyboard selection or mouse hover
            if i == self.selected or i == self.hovered:
                color = self.selected_color
            else:
                color = self.normal_color
                
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, menu_y + i * MENU_SPACING))
            screen.blit(text, text_rect)
            
            # Store the rectangle for mouse detection
            self.option_rects.append(text_rect.inflate(40, 20))  # Make hitbox larger for easier clicking

            # Only show selection indicator for keyboard selection
            if i == self.selected:
                pygame.draw.circle(screen, color, (text_rect.left - 20, text_rect.centery), 7)
                
        # Instructions
        instructions = [
            "↑↓: Navigate",
            "Enter: Select",
            "Mouse: Click to select"
        ]
        
        instruction_y = screen.get_height() - 100
        instruction_font = pygame.font.Font(None, 24)
        for instruction in instructions:
            text = instruction_font.render(instruction, True, (180, 180, 180))
            text_rect = text.get_rect(center=(screen.get_width() // 2, instruction_y))
            screen.blit(text, text_rect)
            instruction_y += 20
            
        # Debug: Uncomment to see clickable areas
        # for rect in self.option_rects:
        #     pygame.draw.rect(screen, (255, 0, 0), rect, 1)

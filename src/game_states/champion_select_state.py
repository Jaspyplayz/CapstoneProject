# src/game_states/champion_select_state.py

import pygame
from src.constants import STATE_MENU, STATE_PLAY, SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_FONT

class ChampionSelectState:
    def __init__(self, game):
        self.game = game
        
        # Font setup with custom font
        try:
            self.title_font = pygame.font.Font(DEFAULT_FONT, 60)
            self.font = pygame.font.Font(DEFAULT_FONT, 36)
            self.small_font = pygame.font.Font(DEFAULT_FONT, 24)
        except:
            print("Warning: Custom font not found. Using fallback font.")
            self.title_font = pygame.font.SysFont(None, 60)
            self.font = pygame.font.SysFont(None, 36)
            self.small_font = pygame.font.SysFont(None, 24)
        
        # Champion data
        self.champions = [
            {
                "id": "base",
                "name": "Base Hero",
                "description": "Balanced fighter with standard abilities",
                "color": (100, 100, 255),
                "abilities": ["Basic Attack", "Standard Defense", "Normal Speed"]
            },
            {
                "id": "ezreal",
                "name": "Ezreal",
                "description": "Agile mage with ranged abilities",
                "color": (50, 150, 255),
                "abilities": ["Mystic Shot (Q)", "Essence Flux (W)", "Arcane Shift (E)"]
            },
            {
                "id": "ashe",
                "name": "Ashe",
                "description": "Archer with crowd control abilities",
                "color": (200, 230, 255),
                "abilities": ["Frost Shot (Q)", "Volley (W)", "Hawk Shot (E)"]
            }
            # Add more champions as needed
        ]
        
        # Selection variables
        self.selected_index = 0
        for i, champion in enumerate(self.champions):
            if champion["id"] == self.game.selected_character:
                self.selected_index = i
                break
        
        # Layout variables
        self.portrait_size = 150
        self.portrait_spacing = 50
        self.start_x = (SCREEN_WIDTH - (len(self.champions) * (self.portrait_size + self.portrait_spacing) - self.portrait_spacing)) // 2
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to menu
                    self.game.change_state(STATE_MENU)
                    
                elif event.key == pygame.K_LEFT:
                    # Move selection left
                    self.selected_index = (self.selected_index - 1) % len(self.champions)
                    
                elif event.key == pygame.K_RIGHT:
                    # Move selection right
                    self.selected_index = (self.selected_index + 1) % len(self.champions)
                    
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Select champion and start game
                    self.select_champion()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check if clicked on any champion portrait
                    for i in range(len(self.champions)):
                        portrait_x = self.start_x + i * (self.portrait_size + self.portrait_spacing)
                        portrait_rect = pygame.Rect(portrait_x, 150, self.portrait_size, self.portrait_size)
                        
                        if portrait_rect.collidepoint(mouse_pos):
                            self.selected_index = i
                            break
                    
                    # Check if clicked on start button
                    start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                    if start_button_rect.collidepoint(mouse_pos):
                        self.select_champion()
    
    def select_champion(self):
        # Set the selected champion
        selected_champion = self.champions[self.selected_index]
        self.game.set_character(selected_champion["id"])
        
        # Start the game
        self.game.change_state(STATE_PLAY)
    
    def update(self):
        # Any animations or effects
        pass
    
    def render(self, screen):
        # Fill background
        screen.fill((20, 20, 40))
        
        # Draw title
        title_text = self.title_font.render("Champion Select", True, (255, 255, 255))
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 50))
        
        # Draw champion portraits
        for i, champion in enumerate(self.champions):
            portrait_x = self.start_x + i * (self.portrait_size + self.portrait_spacing)
            
            # Draw portrait background
            portrait_rect = pygame.Rect(portrait_x, 150, self.portrait_size, self.portrait_size)
            
            # Highlight selected champion
            if i == self.selected_index:
                # Draw selection border
                pygame.draw.rect(screen, (255, 215, 0), portrait_rect.inflate(10, 10), 3)
            
            # Draw champion color/portrait
            pygame.draw.rect(screen, champion["color"], portrait_rect)
            
            # Draw champion name
            name_text = self.font.render(champion["name"], True, (255, 255, 255))
            screen.blit(name_text, (portrait_x + self.portrait_size//2 - name_text.get_width()//2, 
                                  150 + self.portrait_size + 10))
        
        # Draw selected champion details
        selected = self.champions[self.selected_index]
        
        # Description
        desc_text = self.font.render(selected["description"], True, (255, 255, 255))
        screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, 350))
        
        # Abilities
        ability_y = 400
        for ability in selected["abilities"]:
            ability_text = self.small_font.render(f"• {ability}", True, (220, 220, 220))
            screen.blit(ability_text, (SCREEN_WIDTH//2 - ability_text.get_width()//2, ability_y))
            ability_y += 30
        
        # Draw start button
        start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(screen, (50, 150, 50), start_button_rect)
        start_text = self.font.render("Start Game", True, (255, 255, 255))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT - 100 + 15))

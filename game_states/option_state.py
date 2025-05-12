from game_states.game_state import GameState
import pygame
from src.constants import (
    WHITE, YELLOW, DEFAULT_FONT, NORMAL_FONT_SIZE, HEADING_FONT_SIZE,
    MENU_START_Y, MENU_SPACING, FONT_DIR, UI_ACCENT, UI_BACKGROUND
)
import os

class OptionsState(GameState):
    
    def __init__(self, game, **kwargs):
        super().__init__(game)
        
        # Store previous state to return to
        self.previous_state = kwargs.get("previous_state", None)
        
        # Options and their current values
        self.options = [
            {"name": "Music Volume", "value": int(game.settings.get("music_volume", 70)), "min": 0, "max": 100, "step": 10},
            {"name": "Sound Effects Volume", "value": int(game.settings.get("sfx_volume", 70)), "min": 0, "max": 100, "step": 10},
            {"name": "Fullscreen", "value": bool(game.settings.get("fullscreen", False)), "toggle": True},
            {"name": "Back"}
        ]
        
        self.selected = 0
        
        # Colors and fonts
        self.selected_color = YELLOW
        self.normal_color = WHITE
        
        try:
            font_path = os.path.join(FONT_DIR, DEFAULT_FONT)
            self.font = pygame.font.Font(font_path, NORMAL_FONT_SIZE)
            self.title_font = pygame.font.Font(font_path, HEADING_FONT_SIZE)
        except Exception as e:
            print(f"Error loading font: {e}")
            self.font = pygame.font.Font(None, 48)
            self.title_font = pygame.font.Font(None, 72)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                    self.game.assets.play_sound("hover")
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                    self.game.assets.play_sound("hover")
                elif event.key == pygame.K_LEFT:
                    self.adjust_option(-1)
                    self.game.assets.play_sound("hover")
                elif event.key == pygame.K_RIGHT:
                    self.adjust_option(1)
                    self.game.assets.play_sound("hover")
                elif event.key == pygame.K_RETURN:
                    self.select_option()
                    self.game.assets.play_sound("select")
                elif event.key == pygame.K_ESCAPE:
                    self.save_and_exit()
                    self.game.assets.play_sound("back")

    def adjust_option(self, direction):
        if self.selected < len(self.options) - 1:  # Not the "Back" option
            option = self.options[self.selected]
            
            if "toggle" in option and option["toggle"]:
                option["value"] = not option["value"]
                self.apply_setting(option["name"], option["value"])
            elif "min" in option and "max" in option:
                old_value = option["value"]
                step = option.get("step", 1)
                option["value"] = max(option["min"], min(option["max"], option["value"] + direction * step))
                
                # Only apply if value changed
                if old_value != option["value"]:
                    self.apply_setting(option["name"], option["value"])
                    return True
        return False

    def apply_setting(self, name, value):
        if name == "Music Volume":
            self.game.settings["music_volume"] = value
            self.game.assets.set_music_volume(value / 100)
        elif name == "Sound Effects Volume":
            self.game.settings["sfx_volume"] = value
            self.game.assets.set_sfx_volume(value / 100)
        elif name == "Fullscreen":
            self.game.settings["fullscreen"] = value
            self.game.toggle_fullscreen(value)

    def select_option(self):
        if self.selected == len(self.options) - 1:  # "Back" option
            self.save_and_exit()
        else:
            option = self.options[self.selected]
            if "toggle" in option and option["toggle"]:
                option["value"] = not option["value"]
                self.apply_setting(option["name"], option["value"])

    def save_and_exit(self):
        # Save settings
        if self.game.save_settings():
            # Return to previous state or menu
            if self.previous_state:
                self.game.state = self.previous_state
            else:
                self.game.change_state("menu")

    def update(self):
        pass

    def render(self, screen):
        screen.fill(UI_BACKGROUND)
        
        # Title
        title = self.title_font.render("Options", True, UI_ACCENT)
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)
        
        # Options
        menu_y = MENU_START_Y
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected else self.normal_color
            
            # Option name
            name_text = self.font.render(option["name"], True, color)
            name_rect = name_text.get_rect(midright=(screen.get_width() // 2 - 20, menu_y + i * MENU_SPACING))
            screen.blit(name_text, name_rect)
            
            # Option value (if applicable)
            if "value" in option and i < len(self.options) - 1:  # Not the "Back" option
                if "toggle" in option and option["toggle"]:
                    value_text = self.font.render("ON" if option["value"] else "OFF", True, color)
                else:
                    value_text = self.font.render(str(option["value"]), True, color)
                
                value_rect = value_text.get_rect(midleft=(screen.get_width() // 2 + 20, menu_y + i * MENU_SPACING))
                screen.blit(value_text, value_rect)
                
                # Draw slider for numeric values
                if "min" in option and "max" in option and not ("toggle" in option and option["toggle"]):
                    slider_width = 200
                    slider_height = 10
                    slider_x = value_rect.right + 20
                    slider_y = value_rect.centery - slider_height // 2
                    
                    # Background bar
                    pygame.draw.rect(screen, (80, 80, 80), 
                                    (slider_x, slider_y, slider_width, slider_height))
                    
                    # Value indicator
                    progress = (option["value"] - option["min"]) / (option["max"] - option["min"])
                    pygame.draw.rect(screen, color, 
                                    (slider_x, slider_y, int(slider_width * progress), slider_height))
                    
                    # Slider knob
                    knob_pos = (slider_x + int(slider_width * progress), value_rect.centery)
                    pygame.draw.circle(screen, WHITE, knob_pos, 8)
                    if i == self.selected:
                        pygame.draw.circle(screen, color, knob_pos, 10, 2)
            
            # Selection indicator
            if i == self.selected:
                pygame.draw.circle(screen, color, (name_rect.left - 20, name_rect.centery), 7)
                
        # Instructions
        instructions = [
            "↑↓: Navigate",
            "←→: Adjust Value",
            "Enter: Select",
            "Esc: Back"
        ]
        
        instruction_y = screen.get_height() - 100
        for instruction in instructions:
            text = pygame.font.Font(None, 24).render(instruction, True, (180, 180, 180))
            text_rect = text.get_rect(center=(screen.get_width() // 2, instruction_y))
            screen.blit(text, text_rect)
            instruction_y += 20

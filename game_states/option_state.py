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
        
        # Store UI elements for mouse interaction
        self.option_rects = []
        self.slider_rects = []
        self.toggle_rects = []
        
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
        
        # Track if user is dragging a slider
        self.dragging_slider = None

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
            
            # Mouse movement for hover effect
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle slider dragging
                if self.dragging_slider is not None:
                    idx, slider_rect, min_val, max_val = self.dragging_slider
                    self.handle_slider_drag(idx, slider_rect, mouse_pos, min_val, max_val)
                
                # Hover effect on options
                else:
                    for i, rect in enumerate(self.option_rects):
                        if rect.collidepoint(mouse_pos):
                            if self.selected != i:
                                self.selected = i
                                self.game.assets.play_sound("hover")
            
            # Mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check option text clicks
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected = i
                        self.select_option()
                        self.game.assets.play_sound("select")
                        break
                
                # Check slider clicks
                for i, rect in enumerate(self.slider_rects):
                    if rect.collidepoint(mouse_pos) and i < len(self.options) - 1:
                        option = self.options[i]
                        if "min" in option and "max" in option and not option.get("toggle", False):
                            self.dragging_slider = (i, rect, option["min"], option["max"])
                            self.handle_slider_drag(i, rect, mouse_pos, option["min"], option["max"])
                            break
                
                # Check toggle clicks
                for i, rect in enumerate(self.toggle_rects):
                    if rect.collidepoint(mouse_pos) and i < len(self.options) - 1:
                        option = self.options[i]
                        if option.get("toggle", False):
                            option["value"] = not option["value"]
                            self.apply_setting(option["name"], option["value"])
                            self.game.assets.play_sound("select")
                            break
            
            # Mouse button release
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_slider = None

    def handle_slider_drag(self, idx, slider_rect, mouse_pos, min_val, max_val):
        """Handle dragging a slider with the mouse"""
        option = self.options[idx]
        
        # Calculate relative position on slider (0.0 to 1.0)
        rel_x = max(0, min(1, (mouse_pos[0] - slider_rect.left) / slider_rect.width))
        
        # Convert to value range
        new_value = min_val + rel_x * (max_val - min_val)
        
        # Apply step if defined
        if "step" in option:
            new_value = round(new_value / option["step"]) * option["step"]
        
        # Update if changed
        if new_value != option["value"]:
            option["value"] = int(new_value)
            self.apply_setting(option["name"], option["value"])

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
        
        # Reset UI element tracking
        self.option_rects = []
        self.slider_rects = []
        self.toggle_rects = []
        
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
            
            # Store option rect for mouse interaction
            option_rect = name_rect.inflate(40, 20)
            self.option_rects.append(option_rect)
            
            # Option value (if applicable)
            if "value" in option and i < len(self.options) - 1:  # Not the "Back" option
                if "toggle" in option and option["toggle"]:
                    value_text = self.font.render("ON" if option["value"] else "OFF", True, color)
                    value_rect = value_text.get_rect(midleft=(screen.get_width() // 2 + 20, menu_y + i * MENU_SPACING))
                    screen.blit(value_text, value_rect)
                    
                    # Store toggle rect for mouse interaction
                    toggle_rect = value_rect.inflate(40, 20)
                    self.toggle_rects.append(toggle_rect)
                else:
                    value_text = self.font.render(str(option["value"]), True, color)
                    value_rect = value_text.get_rect(midleft=(screen.get_width() // 2 + 20, menu_y + i * MENU_SPACING))
                    screen.blit(value_text, value_rect)
                    
                    # Store empty rect for toggle (to maintain indices)
                    self.toggle_rects.append(pygame.Rect(0, 0, 0, 0))
                
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
                    
                    # Store slider rect for mouse interaction
                    slider_rect = pygame.Rect(slider_x - 5, slider_y - 10, slider_width + 10, slider_height + 20)
                    self.slider_rects.append(slider_rect)
                else:
                    # Store empty rect for slider (to maintain indices)
                    self.slider_rects.append(pygame.Rect(0, 0, 0, 0))
            else:
                # Store empty rects for non-interactive elements
                self.slider_rects.append(pygame.Rect(0, 0, 0, 0))
                self.toggle_rects.append(pygame.Rect(0, 0, 0, 0))
            
            # Selection indicator
            if i == self.selected:
                pygame.draw.circle(screen, color, (name_rect.left - 20, name_rect.centery), 7)
                
        # Instructions
        instructions = [
            "↑↓: Navigate",
            "←→: Adjust Value",
            "Enter: Select",
            "Esc: Back",
            "Mouse: Click to interact"
        ]
        
        instruction_y = screen.get_height() - 120
        for instruction in instructions:
            text = pygame.font.Font(None, 24).render(instruction, True, (180, 180, 180))
            text_rect = text.get_rect(center=(screen.get_width() // 2, instruction_y))
            screen.blit(text, text_rect)
            instruction_y += 20
            
        # Debug: Uncomment to visualize clickable areas
        # for rect in self.option_rects:
        #     pygame.draw.rect(screen, (255, 0, 0), rect, 1)
        # for rect in self.slider_rects:
        #     pygame.draw.rect(screen, (0, 255, 0), rect, 1)
        # for rect in self.toggle_rects:
        #     pygame.draw.rect(screen, (0, 0, 255), rect, 1)

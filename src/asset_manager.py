# asset_manager.py
import os
import pygame
from src.constants import (
    ASSET_DIR, IMAGE_DIR, SOUND_DIR, FONT_DIR,
    DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME
)

class AssetManager:
    """A simple asset manager to load and store game resources."""
    
    def __init__(self):
        # Set up asset directories
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.asset_dir = os.path.join(self.base_dir, ASSET_DIR)
        self.image_dir = os.path.join(self.asset_dir, IMAGE_DIR)
        self.sound_dir = os.path.join(self.asset_dir, SOUND_DIR)
        self.font_dir = os.path.join(self.asset_dir, FONT_DIR)
        
        # Create directories if they don't exist
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.sound_dir, exist_ok=True)
        os.makedirs(self.font_dir, exist_ok=True)
        os.makedirs(os.path.join(self.sound_dir, "ui"), exist_ok=True)
        
        # Dictionaries to store loaded assets
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.music_tracks = {}
        
        # Volume settings
        self.music_volume = DEFAULT_MUSIC_VOLUME
        self.sfx_volume = DEFAULT_SFX_VOLUME
        
        # Initialize mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        print(f"Asset Manager initialized. Base directory: {self.asset_dir}")
        print(f"Sound directory: {self.sound_dir}")
        print(f"Sound directory exists: {os.path.exists(self.sound_dir)}")
        print(f"UI sound directory exists: {os.path.exists(os.path.join(self.sound_dir, 'ui'))}")
        
        # Ensure required sound files exist
        self.ensure_sound_files_exist()
        
        pygame.mixer.music.set_volume(self.music_volume)

    def ensure_sound_files_exist(self):
        """Create placeholder sound files if they don't exist."""
        # Create UI sound directory
        ui_sound_dir = os.path.join(self.sound_dir, "ui")
        os.makedirs(ui_sound_dir, exist_ok=True)
        
        # Check if required sound files exist, create empty ones if not
        required_sounds = {
            "click.wav": ui_sound_dir,
            "hover.wav": ui_sound_dir,
            "select.wav": ui_sound_dir,
            "menu_music.mp3": self.sound_dir,
            "game_music.mp3": self.sound_dir
        }
        
        for filename, directory in required_sounds.items():
            filepath = os.path.join(directory, filename)
            if not os.path.exists(filepath):
                print(f"Creating placeholder sound file: {filepath}")
                try:
                    # Create a minimal valid sound file
                    if filename.endswith('.wav'):
                        # Create a silent WAV file (1 second)
                        import wave
                        import struct
                        
                        with wave.open(filepath, 'w') as wf:
                            wf.setnchannels(1)  # Mono
                            wf.setsampwidth(2)  # 2 bytes per sample
                            wf.setframerate(44100)  # 44.1 kHz
                            for i in range(44100):  # 1 second of silence
                                wf.writeframes(struct.pack('h', 0))
                    
                    elif filename.endswith('.mp3'):
                        # Create an empty file for MP3
                        # Note: Creating a valid MP3 is complex, so we'll just create an empty file
                        # You'll need to replace this with actual MP3 files later
                        with open(filepath, 'w') as f:
                            f.write('')
                        print(f"Warning: Created empty MP3 file {filepath}. Replace with real MP3.")
                except Exception as e:
                    print(f"Failed to create placeholder sound file {filepath}: {e}")

    def set_music_volume(self, volume):
        """Set the music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        print(f"Music volume set to {self.music_volume}")

    def set_sfx_volume(self, volume):
        """Set the sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        # Apply volume to all loaded sound effects
        for sound in self.sounds.values():
            if sound is not None:
                try:
                    sound.set_volume(self.sfx_volume)
                except Exception as e:
                    print(f"Error setting sound volume: {e}")
        print(f"SFX volume set to {self.sfx_volume}")

    def preload_common_assets(self):
        """Preload commonly used assets to avoid loading delays during gameplay."""
        from src.constants import (
            DEFAULT_FONT, NORMAL_FONT_SIZE, SMALL_FONT_SIZE, 
            TITLE_FONT_SIZE, HEADING_FONT_SIZE
        )
        
        print("Preloading common assets...")
        
        # Load common UI images
        self.load_image("ui_button", "ui/button.png")
        self.load_image("ui_panel", "ui/panel.png")
        self.load_image("logo", "ui/logo.png")
        self.load_image("menu_bg", "backgrounds/menu_bg.png", convert_alpha=False)
        
        # Load common UI sounds with better error reporting
        print("Loading UI sounds...")
        click_path = os.path.join(self.sound_dir, "ui/click.wav")
        hover_path = os.path.join(self.sound_dir, "ui/hover.wav")
        select_path = os.path.join(self.sound_dir, "ui/select.wav")
        
        print(f"Click sound exists: {os.path.exists(click_path)}")
        print(f"Hover sound exists: {os.path.exists(hover_path)}")
        print(f"Select sound exists: {os.path.exists(select_path)}")
        
        self.load_sound("click", "ui/click.wav")
        self.load_sound("hover", "ui/hover.wav")
        self.load_sound("select", "ui/select.wav")
        
        # Apply current SFX volume to all sounds
        for sound in self.sounds.values():
            if sound is not None:
                sound.set_volume(self.sfx_volume)
        
        # Print loaded sounds for debugging
        print(f"Loaded sounds: {list(self.sounds.keys())}")
        
        # Load common fonts at different sizes
        try:
            self.load_font("main", DEFAULT_FONT, SMALL_FONT_SIZE)
            self.load_font("main", DEFAULT_FONT, NORMAL_FONT_SIZE)
            self.load_font("main", DEFAULT_FONT, HEADING_FONT_SIZE)
            self.load_font("main", DEFAULT_FONT, TITLE_FONT_SIZE)
        except Exception as e:
            print(f"Error loading fonts: {e}")
        
        # Load common music
        try:
            self.load_music("menu_music.mp3")
            self.music_tracks["menu_music"] = "menu_music.mp3"
            self.music_tracks["game_music"] = "game_music.mp3"
        except Exception as e:
            print(f"Error preloading music: {e}")
        
        print("Common assets preloaded successfully")

    def load_image(self, name, filename, convert_alpha=True):
        """Load an image and store it in the images dictionary."""
        if name in self.images:
            return self.images[name]
        
        try:
            filepath = os.path.join(self.image_dir, filename)
            image = pygame.image.load(filepath)
            
            if convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
                
            self.images[name] = image
            return image
            
        except Exception as e:
            print(f"Error loading image '{filename}': {e}")
            # Create a placeholder for missing images
            surf = pygame.Surface((64, 64))
            surf.fill((255, 0, 255))  # Magenta for missing texture
            self.images[name] = surf
            return surf
    
    def load_sound(self, name, filename):
        """Load a sound effect and store it in the sounds dictionary."""
        if name in self.sounds:
            return self.sounds[name]
        
        try:
            filepath = os.path.join(self.sound_dir, filename)
            print(f"Loading sound: {filepath}")
            
            if not os.path.exists(filepath):
                print(f"Sound file does not exist: {filepath}")
                self.sounds[name] = None
                return None
                
            sound = pygame.mixer.Sound(filepath)
            sound.set_volume(self.sfx_volume)  # Apply current volume setting
            self.sounds[name] = sound
            print(f"Successfully loaded sound: {name}")
            return sound
            
        except Exception as e:
            print(f"Error loading sound '{filename}': {e}")
            self.sounds[name] = None
            return None
    
    def play_sound(self, name):
        """Play a sound by name."""
        if name in self.sounds and self.sounds[name] is not None:
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"Error playing sound '{name}': {e}")
        else:
            print(f"Sound '{name}' not found or not loaded properly")
    
    def load_music(self, filename):
        """Load and play background music."""
        try:
            filepath = os.path.join(self.sound_dir, filename)
            if not os.path.exists(filepath):
                print(f"Music file does not exist: {filepath}")
                return False
                
            pygame.mixer.music.load(filepath)
            return True
            
        except Exception as e:
            print(f"Error loading music '{filename}': {e}")
            return False
    
    def play_music(self, track_name=None, loops=-1):
        """Play the specified music track or the currently loaded one."""
        try:
            if track_name:
                # Load the track if a name is provided
                if track_name in self.music_tracks:
                    filename = self.music_tracks[track_name]
                    self.load_music(filename)
                else:
                    self.load_music(track_name)
            
            # Check if music is loaded before playing
            pygame.mixer.music.play(loops)
            print(f"Playing music track: {track_name if track_name else 'current track'}")
        except Exception as e:
            print(f"Error playing music: {e}")
            # Try to recover by loading a default track
            try:
                if "menu_music" in self.music_tracks:
                    print("Attempting to play default menu music...")
                    self.load_music(self.music_tracks["menu_music"])
                    pygame.mixer.music.play(loops)
            except:
                print("Could not recover music playback")

    
    def stop_music(self):
        """Stop the currently playing music."""
        pygame.mixer.music.stop()
    
    def load_font(self, name, filename, size):
        """Load a font and store it in the fonts dictionary."""
        key = f"{name}_{size}"
        if key in self.fonts:
            return self.fonts[key]
        
        try:
            filepath = os.path.join(self.font_dir, filename)
            font = pygame.font.Font(filepath, size)
            self.fonts[key] = font
            return font
            
        except Exception as e:
            print(f"Error loading font '{filename}': {e}")
            # Fall back to default font
            font = pygame.font.Font(None, size)
            self.fonts[key] = font
            return font
    
    def get_font(self, name, size):
        """Get a loaded font or load it if not available."""
        key = f"{name}_{size}"
        if key in self.fonts:
            return self.fonts[key]
        
        # Try to load the font file
        return self.load_font(name, f"{name}.ttf", size)

# setup_assets.py
import os

def create_asset_directories():
    # Define base directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.join(base_dir, "assets")
    
    # Define subdirectories
    directories = [
        os.path.join(asset_dir, "images"),
        os.path.join(asset_dir, "images", "ui"),
        os.path.join(asset_dir, "images", "backgrounds"),
        os.path.join(asset_dir, "images", "characters"),
        os.path.join(asset_dir, "images", "items"),
        os.path.join(asset_dir, "sounds"),
        os.path.join(asset_dir, "sounds", "ui"),
        os.path.join(asset_dir, "sounds", "music"),
        os.path.join(asset_dir, "sounds", "sfx"),
        os.path.join(asset_dir, "fonts")
    ]
    
    # Create each directory
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

if __name__ == "__main__":
    create_asset_directories()
    print("Asset directories created successfully!")

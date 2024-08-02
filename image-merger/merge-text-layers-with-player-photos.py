from PIL import Image
import os
import re

def normalize_name(name):
    """ Normalize the player name to ensure consistent formatting. """
    name = name.lower().replace(" ", "-")
    name = re.sub(r"[-]+?$", "", name)  # Remove trailing hyphens
    return name

def extract_player_info(filename):
    """ Extract player name and pose from the filename. """
    parts = filename.split('-')
    player_name = parts[0]
    pose = '-'.join(parts[2:])[:-4]  # Remove '.png' from the pose
    return player_name, pose

def load_player_photos(directory):
    player_photos = {}
    for filename in os.listdir(directory):
        if filename.endswith(".png") and '-' in filename:
            player_name, pose = extract_player_info(filename)
            normalized_name = normalize_name(player_name)
            if normalized_name not in player_photos:
                player_photos[normalized_name] = []
            player_photos[normalized_name].append((Image.open(os.path.join(directory, filename)), pose))
    print(f"Loaded {len(player_photos)} players' photos.")
    return player_photos

def load_text_layers(directory):
    text_layers = {}
    for filename in os.listdir(directory):
        if filename.startswith("text layer-") and filename.endswith(".png"):
            player_name = filename.replace("text layer-", "").replace(".png", "")
            normalized_name = normalize_name(player_name)
            text_layers[normalized_name] = Image.open(os.path.join(directory, filename))
    print(f"Loaded text layers for {len(text_layers)} players.")
    return text_layers

def enhance_opacity(image, factor=1.0):
    """ Enhance the opacity of an image. """
    if image.mode == 'RGBA':
        r, g, b, alpha = image.split()
        alpha = alpha.point(lambda p: p * factor)
        return Image.merge('RGBA', (r, g, b, alpha))
    return image

def sanitize_path(input_path):
    """ Sanitize the file path by handling both paths with escaped spaces and quoted paths. """
    # First, strip any leading and trailing quotes
    sanitized = input_path.strip('\'"')

    # Then, replace backslash-space combinations with a space
    sanitized = sanitized.replace("\\ ", " ").strip()

    print(f"final path = {sanitized}")

    # Check if the path exists
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

# User input for directories, with path sanitization
player_photos_dir = sanitize_path(input("Enter the file directory for the PLAYER photos: "))
text_layers_dir = sanitize_path(input("Enter the file directory for the TEXT layers: "))
output_dir = sanitize_path(input("Enter the directory where you want the images to output: "))

player_photos = load_player_photos(player_photos_dir)
text_layers = load_text_layers(text_layers_dir)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

unmatched_photos = set(player_photos.keys())
unmatched_texts = set(text_layers.keys())

count = 0
for player_name, photos in player_photos.items():
    text_layer = text_layers.get(player_name)
    if text_layer:
        # Enhance the opacity of the text layer
        enhanced_text_layer = enhance_opacity(text_layer, factor=1.5)  # Adjust factor as needed

        for photo, pose in photos:
            # Start with the enhanced text layer
            combined_image = enhanced_text_layer.copy()
            # Paste the player photo on top of the text layer
            combined_image.paste(photo, (0, 0), photo)
            output_filename = f"{player_name}-{pose}-with-text-layer.png"
            output_path = os.path.join(output_dir, output_filename)
            combined_image.save(output_path)
            print(f"Saved combined image at {output_path}")
            count += 1
        unmatched_photos.discard(player_name)
        unmatched_texts.discard(player_name)
    else:
        print(f"No text layer found for player: {player_name}")

if count == 0:
    print("No images were generated. Please check the input directories and file naming conventions.")
else:
    print(f"Generated {count} images.")

if unmatched_photos:
    print("\nUnmatched photo names:")
    print(unmatched_photos)
else:
    print("\nAll player photos matched successfully with text layers.")

if unmatched_texts:
    print("\nUnmatched text layer names:")
    print(unmatched_texts)
else:
    print("\nAll text layers matched successfully with player photos.")

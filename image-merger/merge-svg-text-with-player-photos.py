"""
------------------------------------------------------------------------------------------
This script is designed to combine vector SVG text layers with raster PNG player photos 
and output the combined image as a high-quality PDF. It's specifically tailored for 
creating print-ready player cards with player photos overlaid on top of stylized text.

Functionality:
1. Normalizes player names to ensure consistency across file naming.
2. Loads player photos (PNG format) and SVG text layers from specified directories.
3. For each player, combines their photo with the corresponding SVG text layer.
4. Outputs the combined image as a PDF, maintaining the vector quality of the text.

Key Points of Adjustment:
- `player_photos_dir`, `text_layers_dir`, `output_dir`: Directories for player photos, 
  text layers, and output. Change these according to your file structure.
- `pdf_width`, `pdf_height`: Dimensions of the output PDF. Adjust these values based on 
  the desired physical size of the print output.
- `svg_width_in`, `svg_height_in`: Dimensions of the SVG artboard, as obtained from a 
  source like Adobe Illustrator. Update these to match the actual size of your SVG text layers.
- The script assumes that the player photos are sized correctly for the PDF dimensions. 
  If this is not the case, additional code for resizing the photos may be necessary.
- The positioning of the SVG and the photo within the PDF is set to start at the top-left 
  corner (0, 0 coordinates). Adjust the placement logic in the script if a different 
  alignment is required.

Usage Notes:
- Ensure the Python Imaging Library (PIL), svglib, and ReportLab libraries are installed.
- The script is designed for batch processing multiple players. File naming conventions 
  should be consistent for seamless operation.
- The script prints status messages to the console for tracking progress and identifying 
  any potential mismatches or missing files.

------------------------------------------------------------------------------------------
"""
from PIL import Image
import os
import re
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from io import BytesIO
from reportlab.lib.utils import ImageReader

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
    """ Load player photos from the specified directory. """
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

def load_text_layers_svg(directory):
    """ Load SVG text layers from the specified directory. """
    text_layers = {}
    for filename in os.listdir(directory):
        if filename.startswith("text layer-") and filename.endswith(".svg"):
            player_name = filename.replace("text layer-", "").replace(".svg", "")
            normalized_name = normalize_name(player_name)
            text_layers[normalized_name] = os.path.join(directory, filename)
    print(f"Loaded text layers for {len(text_layers)} players.")
    return text_layers

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

def pil_image_to_reportlab(image):
    """ Convert PIL Image to a format compatible with ReportLab, preserving transparency. """
    image_buffer = BytesIO()
    image.save(image_buffer, format='PNG')
    return image_buffer

# User input for directories, with path sanitization
player_photos_dir = sanitize_path(input("Enter the file directory for the PLAYER photos: "))
text_layers_dir = sanitize_path(input("Enter the file directory for the TEXT layers: "))
output_dir = sanitize_path(input("Enter the directory where you want the images to output: "))

# Load player photos and SVG text layers
player_photos = load_player_photos(player_photos_dir)
text_layers = load_text_layers_svg(text_layers_dir)

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Set the PDF dimensions to the desired size
pdf_width = 2.5867 * inch  # in inches
pdf_height = 3.62138 * inch  # in inches

count = 0  # Counter for the number of images generated
for player_name, photos in player_photos.items():
    svg_text_path = text_layers.get(player_name)
    if svg_text_path:
        for photo, pose in photos:
            output_filename = f"{player_name}-{pose}-with-text-layer.pdf"
            output_path = os.path.join(output_dir, output_filename)

            # Create a new canvas for each PDF
            c = canvas.Canvas(output_path, pagesize=(pdf_width, pdf_height))

            # Load and draw the SVG text layer directly onto the PDF
            drawing = svg2rlg(svg_text_path)
            renderPDF.draw(drawing, c, 0, 0)  # Draw the SVG on the PDF

            # Convert the PIL image to a format compatible with ReportLab
            image_stream = pil_image_to_reportlab(photo)
            c.drawImage(ImageReader(image_stream), 0, 0, width=pdf_width, height=pdf_height)

            # Save the PDF
            c.save()
            print(f"Saved combined image as PDF at {output_path}")
            count += 1
    else:
        print(f"No text layer found for player: {player_name}")

print(f"Generated {count} images.")
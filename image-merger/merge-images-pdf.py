from PIL import Image
import os
import itertools
import functools
import fitz  # PyMuPDF
import io

def sanitize_path(input_path):
    """ Sanitize the file path to handle both quoted paths and paths with escaped spaces. """
    sanitized = input_path.strip('\'"')
    sanitized = sanitized.replace("\\ ", " ")
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

def inches_to_pixels(width_in_inches, height_in_inches, dpi=1200):
    """ Convert dimensions in inches to pixels. """
    width_in_pixels = int(width_in_inches * dpi)
    height_in_pixels = int(height_in_inches * dpi)
    return width_in_pixels, height_in_pixels

def load_variations(path, replicate_to_match=None):
    """ Load images or PDFs from a given directory or a single file. """
    print(f"Processing path: {path}")
    path = sanitize_path(path)
    images, filenames = [], []

    if os.path.isfile(path):
        print("Path is a file. Loading image or PDF...")
        if path.lower().endswith('.pdf'):
            # Store the path for PDF files
            images = [path] * (replicate_to_match if replicate_to_match else 1)
            filenames = [os.path.basename(path)] * (replicate_to_match if replicate_to_match else 1)
        else:
            try:
                with Image.open(path) as image:
                    images = [image.copy()] * (replicate_to_match if replicate_to_match else 1)
                    filenames = [os.path.basename(path)] * (replicate_to_match if replicate_to_match else 1)
            except IOError as e:
                print(f"Error opening file: {e}")
                raise IOError(f"Could not open file: {path}")

    elif os.path.isdir(path):
        print("Path is a directory. Loading images and PDFs from directory...")
        files = os.listdir(path)
        print(f"Found {len(files)} files. Filtering image and PDF files...")
        valid_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.pdf'))]
        print(f"Found {len(valid_files)} valid files.")

        for file in valid_files:
            file_path = os.path.join(path, file)
            if file.lower().endswith('.pdf'):
                # Store the path for PDF files
                images.append(file_path)
                filenames.append(file)
            else:
                try:
                    with Image.open(file_path) as img:
                        images.append(img.copy())
                        filenames.append(file)
                        print(f"Loaded file: {file}")
                except IOError as e:
                    print(f"Error opening file: {file}, Error: {e}")

    else:
        print("Path is not valid.")
        raise FileNotFoundError(f"Path is not a valid file or directory: {path}")

    return images, filenames

def generate_combinations(layers, filenames, output_dir):
    """ Generate all combinations of images or PDFs from given layers. """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    target_width, target_height = inches_to_pixels(2.5867, 3.6214)

    layer_lengths = [len(layer) for layer in layers]
    total_combinations = functools.reduce(lambda x, y: x * y, layer_lengths)
    print("\nCalculating total combinations...")
    print("Total combinations = " + ' x '.join([str(length) for length in layer_lengths]))
    print(f"Total combinations to generate: {total_combinations}")

    count = 1
    for combination in itertools.product(*layers):
        combined_filenames = [
            os.path.splitext(filenames[layer_index][img_index])[0]
            for layer_index, img_index in enumerate(
                [layers[layer_index].index(img) for layer_index, img in enumerate(combination)]
            )
        ]
        
        # Create a new PDF to hold the combined result
        new_pdf = fitz.open()
        pdf_page = new_pdf.new_page(pno=0, width=target_width, height=target_height)

        for img in combination:
            if isinstance(img, str) and img.lower().endswith('.pdf'):
                # Handle PDF files
                overlay_pdf = fitz.open(img)
                for page in overlay_pdf:
                    pdf_page.show_pdf_page(pdf_page.rect, overlay_pdf, page.number)
            else:
                # Handle raster images
                img_bytes_io = io.BytesIO()
                img_resized = img.resize((target_width, target_height), Image.ANTIALIAS)
                img_resized.save(img_bytes_io, format='PNG')
                img_bytes_io.seek(0)
                pdf_page.insert_image(pdf_page.rect, stream=img_bytes_io.read())

        output_filename = "_".join(combined_filenames) + f"_{count}.pdf"
        new_pdf.save(os.path.join(output_dir, output_filename))
        new_pdf.close()
        print(f"Generating file {count} of {total_combinations}: {output_filename}")
        count += 1

# Main execution part
numLayers = input("Enter the number of layers: ")
outputInput = sanitize_path(input("Where do you want the images to output: "))
layerPaths = [sanitize_path(input(f'Enter the folder (or file) path for layer {i + 1}: ')) for i in range(int(numLayers))]
num_images_in_layers = [len(os.listdir(path)) if os.path.isdir(path) else 1 for path in layerPaths]

layersPath, all_filenames = [], []
for i, path in enumerate(layerPaths):
    print(f"Working on Layer {i + 1}...")
    replicate_count = None if not os.path.isfile(path) or i == len(layerPaths) - 1 else num_images_in_layers[i + 1]
    images, filenames = load_variations(path, replicate_count)
    layersPath.append(images)
    all_filenames.append(filenames)

merge_method = input("Enter 'MERGE' for a 1-for-1 merge of corresponding images or 'COMBINE' to generate all combinations: ").lower()
if merge_method == 'merge' and len(layersPath) == 2 and len(layersPath[0]) == len(layersPath[1]):
    # Code for merging layers (not included in this update as it requires separate handling)
    print("DUh doy idk what to do here")
elif merge_method == 'combine':
    generate_combinations(layersPath, all_filenames, outputInput)
else:
    print("Sorry, that wasn't an appropriate response. Do better next time")

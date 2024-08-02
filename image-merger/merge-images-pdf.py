from PIL import Image
import os
import itertools
import functools
import fitz  # PyMuPDF
import io

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
        
        new_pdf = fitz.open()
        first_layer = combination[0]
        if isinstance(first_layer, Image.Image):
            pdf_width, pdf_height = first_layer.width, first_layer.height
        else:
            with fitz.open(first_layer) as first_pdf:
                pdf_width, pdf_height = first_pdf[0].rect.width, first_pdf[0].rect.height
        pdf_page = new_pdf.new_page(pno=0, width=pdf_width, height=pdf_height)

        for img in combination:
            if isinstance(img, str) and img.lower().endswith('.pdf'):
                overlay_pdf = fitz.open(img)
                if len(overlay_pdf) > 0:
                    page = overlay_pdf[0]
                    # Check for text or drawings to determine if the page is blank
                    if page.get_text("text") or page.get_drawings():
                        pdf_page.show_pdf_page(pdf_page.rect, overlay_pdf, 0)
                    else:
                        print(f"Skipping empty or blank PDF: {img}")
            else:
                img_bytes_io = io.BytesIO()
                img.save(img_bytes_io, format='PNG')
                img_bytes_io.seek(0)
                pdf_page.insert_image(pdf_page.rect, stream=img_bytes_io.read())

        output_filename = "_".join(combined_filenames) + f"_{count}.pdf"
        new_pdf.save(os.path.join(output_dir, output_filename), garbage=4, deflate=True)
        new_pdf.close()
        print(f"Generating file {count} of {total_combinations}: {output_filename}")
        count += 1

def merge_layers(layer1, filenames1, layer2, filenames2, output_dir):
    """ Merge two layers of images or PDFs in a 1-for-1 fashion with concatenated filenames. """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, (item1, item2) in enumerate(zip(layer1, layer2)):
        output_filename = f"{os.path.splitext(filenames1[i])[0]}_-_{os.path.splitext(filenames2[i])[0]}.pdf"
        new_pdf = fitz.open()

        # Load first layer
        if isinstance(item1, str) and item1.lower().endswith('.pdf'):
            with fitz.open(item1) as pdf1:
                pdf_width, pdf_height = pdf1[0].rect.width, pdf1[0].rect.height
        else:
            pdf_width, pdf_height = item1.width, item1.height

        # Create new PDF page
        pdf_page = new_pdf.new_page(pno=0, width=pdf_width, height=pdf_height)

        # Insert first layer
        if isinstance(item1, Image.Image):
            img_bytes_io = io.BytesIO()
            item1.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)
            pdf_page.insert_image(pdf_page.rect, stream=img_bytes_io.read())
        elif isinstance(item1, str) and item1.lower().endswith('.pdf'):
            with fitz.open(item1) as pdf1:
                pdf_page.show_pdf_page(pdf_page.rect, pdf1, 0)

        # Insert second layer
        if isinstance(item2, Image.Image):
            img_bytes_io = io.BytesIO()
            item2.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)
            pdf_page.insert_image(pdf_page.rect, stream=img_bytes_io.read(), overlay=True)
        elif isinstance(item2, str) and item2.lower().endswith('.pdf'):
            with fitz.open(item2) as pdf2:
                pdf_page.show_pdf_page(pdf_page.rect, pdf2, 0, overlay=True)

        new_pdf.save(os.path.join(output_dir, output_filename), garbage=4, deflate=True)
        new_pdf.close()
        print(f'Merged file {i + 1} saved as {output_filename}.')

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
    merge_layers(layersPath[0], all_filenames[0], layersPath[1], all_filenames[1], outputInput)
elif merge_method == 'combine':
    generate_combinations(layersPath, all_filenames, outputInput)
else:
    print("Sorry, that didn't work. If you're doing a merge, make sure it's an equal number of files. If you're doing a combine, idk figure it out.")

from PIL import Image
import os
import itertools
import fitz  # PyMuPDF
import io
from tqdm import tqdm

def print_welcome_message():
    welcome_text = """
    ╔════════════════════════════════════════════════════════════════════╗
    ║                   Welcome to AthletiFi Card Merger                 ║
    ╚════════════════════════════════════════════════════════════════════╝

    This script combines background and player components for AthletiFi cards.
    It can work with 2 or 3 layers of PDFs or images, allowing you to:

    1. Merge layers in a 1-to-1 fashion
    2. Generate all possible combinations of layers

    Please ensure your files are organized in separate folders for each layer.
    For best results, use high-resolution PDFs or PNG files with transparency.

    Let's get started!
    """
    print(welcome_text)

def sanitize_path(input_path):
    """
    Sanitize the file path by handling both paths with escaped spaces and quoted paths.
    
    Args:
    input_path (str): The input file path to sanitize.
    
    Returns:
    str: The sanitized file path.
    
    Raises:
    FileNotFoundError: If the sanitized path is not a valid file or directory.
    """
    sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

def load_variations(path, replicate_to_match=None):
    """
    Load images or PDFs from a given directory or a single file.
    
    Args:
    path (str): The path to the file or directory to load.
    replicate_to_match (int, optional): Number of times to replicate the file if it's a single file.
    
    Returns:
    tuple: A tuple containing two lists - items (file paths) and filenames.
    """
    print(f"Processing path: {path}")
    path = sanitize_path(path)
    items, filenames = [], []

    if os.path.isfile(path):
        print("Path is a file. Loading image or PDF...")
        items = [path] * (replicate_to_match or 1)
        filenames = [os.path.basename(path)] * (replicate_to_match or 1)
    elif os.path.isdir(path):
        print("Path is a directory. Loading images and PDFs from directory...")
        valid_files = [file for file in os.listdir(path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.pdf'))]
        print(f"Found {len(valid_files)} valid files.")

        for file in valid_files:
            file_path = os.path.join(path, file)
            items.append(file_path)
            filenames.append(file)
    else:
        raise FileNotFoundError(f"Path is not a valid file or directory: {path}")

    return items, filenames

def generate_combinations(layers, filenames, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    num_layers = len(layers)
    if num_layers not in [2, 3]:
        raise ValueError("This script supports only 2 or 3 layers.")

    total_combinations = 1
    for layer in layers:
        total_combinations *= len(layer)
    print(f"\nTotal combinations to generate: {total_combinations}")

    combinations = itertools.product(*[range(len(layer)) for layer in layers])

    for count, combination in enumerate(tqdm(combinations, total=total_combinations), 1):
        combined_filenames = [os.path.splitext(filenames[i][idx])[0] for i, idx in enumerate(combination)]

        new_pdf = fitz.open()

        # Use the first layer to determine PDF dimensions
        with fitz.open(layers[0][combination[0]]) as first_pdf:
            pdf_width, pdf_height = first_pdf[0].rect.width, first_pdf[0].rect.height

        pdf_page = new_pdf.new_page(width=pdf_width, height=pdf_height)

        # Insert layers
        for i, idx in enumerate(combination):
            item = layers[i][idx]
            with fitz.open(item) as overlay_pdf:
                if overlay_pdf.page_count > 0:
                    # Check if the page is empty by looking for any content
                    page = overlay_pdf[0]
                    if page.get_text() or page.get_drawings() or page.get_images():
                        pdf_page.show_pdf_page(pdf_page.rect, overlay_pdf, 0)
                    else:
                        print(f"Note: Empty PDF detected: {item}. Using transparent layer.")
                else:
                    print(f"Note: PDF with no pages detected: {item}. Using transparent layer.")

        output_filename = "_".join(combined_filenames)[:200] + f"_{count}.pdf"
        new_pdf.save(os.path.join(output_dir, output_filename), garbage=4, deflate=True)
        new_pdf.close()

def merge_layers(layer1, filenames1, layer2, filenames2, output_dir):
    """
    Merge two layers of PDFs in a 1-for-1 fashion with concatenated filenames.
    
    Args:
    layer1 (list): List of file paths for the first layer.
    filenames1 (list): List of filenames for the first layer.
    layer2 (list): List of file paths for the second layer.
    filenames2 (list): List of filenames for the second layer.
    output_dir (str): Directory to save the merged PDFs.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    total_files = min(len(layer1), len(layer2))
    for i in tqdm(range(total_files), desc="Merging layers"):
        output_filename = f"{os.path.splitext(filenames1[i])[0]}_-_{os.path.splitext(filenames2[i])[0]}.pdf"
        new_pdf = fitz.open()

        # Determine PDF dimensions from first layer
        with fitz.open(layer1[i]) as pdf1:
            pdf_width, pdf_height = pdf1[0].rect.width, pdf1[0].rect.height

        pdf_page = new_pdf.new_page(width=pdf_width, height=pdf_height)

        # Insert layers
        for item in [layer1[i], layer2[i]]:
            with fitz.open(item) as pdf:
                if len(pdf) > 0:
                    pdf_page.show_pdf_page(pdf_page.rect, pdf, 0)

        new_pdf.save(os.path.join(output_dir, output_filename), garbage=4, deflate=True)
        new_pdf.close()

def main():
    print_welcome_message()
    try:
        # Get user input
        numLayers = int(input("Enter the number of layers (2 or 3): "))
        if numLayers not in [2, 3]:
            raise ValueError("This script supports only 2 or 3 layers.")

        outputInput = sanitize_path(input("Where do you want the images to output: "))
        layerPaths = [sanitize_path(input(f'Enter the folder (or file) path for layer {i + 1}: ')) for i in range(numLayers)]

        layersPath, all_filenames = [], []
        for i, path in enumerate(layerPaths):
            print(f"Working on Layer {i + 1}...")
            replicate_count = None if not os.path.isfile(path) or i == len(layerPaths) - 1 else len(os.listdir(layerPaths[i + 1]))
            items, filenames = load_variations(path, replicate_count)
            layersPath.append(items)
            all_filenames.append(filenames)

        # Determine merge method
        # merge_method = input("Enter 'MERGE' for a 1-for-1 merge of corresponding images or 'COMBINE' to generate all combinations: ").lower()
        print("\nWhat would you like to do?")
        print("1. MERGE - Perform a 1-for-1 merge of corresponding images")
        print("2. COMBINE - Generate all possible combinations of layers")

        while True:
            choice = input("Enter your choice (1 or 2): ")
            if choice == '1':
                merge_method = 'merge'
                break
            elif choice == '2':
                merge_method = 'combine'
                break
            else:
                print("Invalid input. Please enter 1 or 2.")
        if merge_method == 'merge' and numLayers == 2 and len(layersPath[0]) == len(layersPath[1]):
            merge_layers(layersPath[0], all_filenames[0], layersPath[1], all_filenames[1], outputInput)
        elif merge_method == 'combine':
            generate_combinations(layersPath, all_filenames, outputInput)
        else:
            print("Invalid input or unequal number of files for merge operation.")
        print_concluding_message()
    except Exception as e:
        import traceback
        print(f"An error occurred: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())

def print_concluding_message():
    concluding_message = """
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                   AthletiFi Card Merger - Process Complete!                ║
    ╚════════════════════════════════════════════════════════════════════════════╝

    ┌──────────────────────────────────────────────────────────────────────────┐
    │ Congratulations! Your AthletiFi cards have been successfully generated.   │
    └──────────────────────────────────────────────────────────────────────────┘

    Next Steps:
    1. Check the output directory to verify all cards have been created correctly.
    2. Review a sample of the generated cards for quality assurance.
    3. Proceed with any post-processing steps (e.g., adding QR codes, final touches).

    Thank you for using the AthletiFi Card Merger - the core of our card creation process!
    """
    print(concluding_message)

if __name__ == "__main__":
    main()
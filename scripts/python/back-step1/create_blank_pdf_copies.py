import os
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import time
import sys

def print_welcome_message():
    welcome_text = """
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║         Welcome to AthletiFi Blank PDF Copies Generator (BACK)             ║
    ╚════════════════════════════════════════════════════════════════════════════╝

    This script helps you create blank PDF copies of existing PDF files, maintaining
    the original dimensions. It's part of the AthletiFi player card generation process. 
    It's intended to create blank PDF copies of existing player photo/text layer PDFs, 
    which will serve as placeholders for the QR codes in the final back design.

    ┌──────────────────────────────────────────┐
    │           Before You Begin:              │
    └──────────────────────────────────────────┘
    1. Ensure you have completed the front card generation process, including:
       ✦ Processing player photos
       ✦ Creating and merging text layers
       ✦ Combining backgrounds and player components
    2. Have the directory path of your original player photo/text layer PDFs ready.
       These should be the PDFs created from the "Merge Text Layers with Player Photos" step.
    3. Decide on an output directory for the blank PDF copies.
    4. Make sure you have the necessary permissions to read from and write to these directories.

    ┌──────────────────────────────────────────┐
    │                 Important:               │
    └──────────────────────────────────────────┘
    ✦ This script will create blank PDF files with the same dimensions and names as the originals.
    ✦ These blank PDFs are crucial for maintaining consistent file naming between front and back designs.
    ✦ The blank PDFs will later be combined with backgrounds and replaced with QR codes in subsequent steps.
    ✦ This script does not modify the original files in any way.

    Let's begin creating the blank PDF copies for your card backs!
    """
    print(welcome_text)

def print_concluding_message():
    concluding_message = """
    ┌──────────────────────────────────────────┐
    │               Process Complete!          │
    └──────────────────────────────────────────┘
    All blank PDFs have been successfully created.

    ┌──────────────────────────────────────────┐
    │               Next Steps:                │
    └──────────────────────────────────────────┘
    1. Verify that all blank PDFs have been created in the output directory.
       The number of blank PDFs should match the number of original player photo/text layer PDFs.

    2. Proceed with the next steps in the back card generation process:
       a. Use these blank PDFs to generate combinations with the background PDFs.
       b. Rename the combined files to match the front card sequence.
       c. Render borders in blue and add them to the cards.
       d. Add database records to properly link to QR codes.
       e. Generate and format QR codes.
       f. Merge QR codes with the blank card backs.
       g. Reintroduce any deleted design elements and add bleed if necessary.

    3. Always validate that the back PDFs correspond correctly to the front PDFs
       using the validateFrontBackCorresponds.py script.

    Remember: These blank PDFs are placeholders. They ensure that the back cards
    maintain the same naming convention and sequence as the front cards, which is
    crucial for proper matching in the final product.

    Thank you for using the AthletiFi Blank PDF Copies Generator!
    """
    print(concluding_message)

def sanitize_path(input_path):
    """
    Sanitize the file path by handling both paths with escaped spaces and quoted paths.
    """
    sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

def create_blank_template(width, height):
    writer = PdfWriter()
    writer.add_blank_page(width=width, height=height)
    return writer

def duplicate_blank_pdf(template, output_path):
    with open(output_path, 'wb') as output_file:
        template.write(output_file)

def get_pdf_dimensions(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        page = reader.pages[0]
        return page.mediabox.width, page.mediabox.height

def loading_animation():
    animation = "|/-\\"
    idx = 0
    while True:
        yield animation[idx]
        idx = (idx + 1) % len(animation)

def main():
    print_welcome_message()

    # Prompt for directories
    original_directory = input("Enter the path to the directory containing the original player photo/text layer PDFs: ")
    output_directory = input("Enter the path where you want to save the blank PDFs for card backs: ")

    try:
        # Sanitize and verify directories
        original_directory = sanitize_path(original_directory)
        output_directory = sanitize_path(output_directory)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    if not os.path.exists(output_directory):
        print(f"The directory {output_directory} does not exist. Creating it now...")
        os.makedirs(output_directory)

    # Get dimensions from the first PDF in the original directory
    pdf_files = [f for f in os.listdir(original_directory) if f.endswith('.pdf')]
    if not pdf_files:
        print("Error: No PDF files found in the original directory.")
        return
    
    # Process each file in the original directory
    total_files = len(pdf_files)
    loader = loading_animation()
    for i, filename in enumerate(pdf_files, 1):
        original_path = os.path.join(original_directory, filename)
        output_path = os.path.join(output_directory, filename)
        
        # Get dimensions for this specific PDF
        width, height = get_pdf_dimensions(original_path)
        
        # Create a blank template with these dimensions
        template = create_blank_template(width, height)
        
        # Create the blank PDF
        duplicate_blank_pdf(template, output_path)
        
        # Update loading animation
        sys.stdout.write(f"\rProcessing: {next(loader)} {i}/{total_files} " +
                         f"({i/total_files*100:.1f}%)")
        sys.stdout.flush()
        time.sleep(0.1)  # Small delay to make the animation visible

    print("\nAll blank PDFs have been created.")
    print_concluding_message()

if __name__ == "__main__":
    main()

# OLD UNSTYLIZED VERSION BELOW (THIS VERSION SHOULD WORK IF THE ABOVE DOES NOT)

# import os
# import PyPDF2
# from PyPDF2 import PdfReader, PdfWriter
# import time
# import sys

# def sanitize_path(input_path):
#     """
#     Sanitize the file path by handling both paths with escaped spaces and quoted paths.
#     """
#     sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
#     if os.path.exists(sanitized):
#         return sanitized
#     else:
#         raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

# def create_blank_template(width, height):
#     writer = PdfWriter()
#     writer.add_blank_page(width=width, height=height)
#     return writer

# def duplicate_blank_pdf(template, output_path):
#     with open(output_path, 'wb') as output_file:
#         template.write(output_file)

# def get_pdf_dimensions(pdf_path):
#     with open(pdf_path, 'rb') as file:
#         reader = PdfReader(file)
#         page = reader.pages[0]
#         return page.mediabox.width, page.mediabox.height

# def loading_animation():
#     animation = "|/-\\"
#     idx = 0
#     while True:
#         yield animation[idx]
#         idx = (idx + 1) % len(animation)

# def main():
#     # Prompt for directories
#     original_directory = input("Enter the path to the directory containing the original PDFs: ")
#     output_directory = input("Enter the path where you want to save the blank PDFs: ")

#     try:
#         # Sanitize and verify directories
#         original_directory = sanitize_path(original_directory)
#         output_directory = sanitize_path(output_directory)
#     except FileNotFoundError as e:
#         print(f"Error: {e}")
#         return

#     if not os.path.exists(output_directory):
#         print(f"The directory {output_directory} does not exist. Creating it now...")
#         os.makedirs(output_directory)

#     # Get dimensions from the first PDF in the original directory
#     pdf_files = [f for f in os.listdir(original_directory) if f.endswith('.pdf')]
#     if not pdf_files:
#         print("Error: No PDF files found in the original directory.")
#         return
    
#     # Process each file in the original directory
#     total_files = len(pdf_files)
#     loader = loading_animation()
#     for i, filename in enumerate(pdf_files, 1):
#         original_path = os.path.join(original_directory, filename)
#         output_path = os.path.join(output_directory, filename)
        
#         # Get dimensions for this specific PDF
#         width, height = get_pdf_dimensions(original_path)
        
#         # Create a blank template with these dimensions
#         template = create_blank_template(width, height)
        
#         # Create the blank PDF
#         duplicate_blank_pdf(template, output_path)
        
#         # Update loading animation
#         sys.stdout.write(f"\rProcessing: {next(loader)} {i}/{total_files} " +
#                          f"({i/total_files*100:.1f}%)")
#         sys.stdout.flush()
#         time.sleep(0.1)  # Small delay to make the animation visible

#     print("\nAll blank PDFs have been created.")

# if __name__ == "__main__":
#     main()
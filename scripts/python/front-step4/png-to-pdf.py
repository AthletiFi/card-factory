import os
import io
from PIL import Image
import fitz  # PyMuPDF
from tqdm import tqdm

def print_welcome_message():
    welcome_text = """
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                 Welcome to AthletiFi PNG to PDF Converter!                 ║
    ╚════════════════════════════════════════════════════════════════════════════╝

    This script converts PNG background files to PDF format, in preparation for 
    integration into the final card designs.

    ┌──────────────────────────────────────────┐
    │           Before You Begin:              │
    └──────────────────────────────────────────┘
    1. Ensure you have prepared your background PNG files.
    2. Have a blank PDF template ready (this will be used for dimensions).
    3. Decide on an output directory for the converted PDF files.

    ┌──────────────────────────────────────────┐
    │                 Important:               │
    └──────────────────────────────────────────┘
    ✦ This script preserves transparency in the PNG files.
    ✦ The output PDFs will have the same dimensions as the provided blank PDF template.
    ✦ The script applies compression to optimize the output PDF files.
    ✦ Original PNG files are not modified; new PDF files are created.

    Let's begin converting your PNG backgrounds to PDF format!
    """
    print(welcome_text)

def print_concluding_message():
    concluding_message = """
    ┌──────────────────────────────────────────┐
    │               Process Complete!          │
    └──────────────────────────────────────────┘
    All PNG backgrounds have been successfully converted to PDF format.

    ┌──────────────────────────────────────────┐
    │               Next Steps:                │
    └──────────────────────────────────────────┘
    1. Verify that all PDF files have been created in the output directory.
       The number of PDFs should match the number of original PNG files.

    2. Check a few of the generated PDFs to ensure the dimensions are correct 
    (should match the blank PDF template).

    3. You can now proceed with the next steps in the card generation process:
       ✦ For front designs: Combine these background PDFs with player photos and text layers.
       ✦ For back designs: Use these as base layers before adding QR codes and other elements.

    4. Remember to keep your original PNG files as backups.

    Thank you for using the AthletiFi PNG to PDF Converter!
    If you encounter any issues or need assistance, please refer to the main
    AthletiFi Card Artwork Generation Instructions or contact the development team.
    """
    print(concluding_message)

def sanitize_path(input_path):
    """Sanitize the file path by handling both paths with escaped spaces and quoted paths."""
    sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

def png_to_pdf(input_dir, output_dir, blank_pdf_path):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the blank PDF to get dimensions
    with fitz.open(blank_pdf_path) as blank_pdf:
        width, height = blank_pdf[0].rect.width, blank_pdf[0].rect.height

    # Get list of PNG files
    png_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]

    # Process each PNG in the input directory
    for filename in tqdm(png_files, desc="Converting PNGs to PDFs"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.pdf')

        # Open the PNG
        with Image.open(input_path) as img:
            # Create a new PDF
            pdf = fitz.open()
            page = pdf.new_page(width=width, height=height)

            # Convert PIL Image to PNG bytes (preserving transparency)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG', optimize=True, compress_level=9)
            img_bytes.seek(0)

            # Insert the image into the PDF
            page.insert_image(page.rect, stream=img_bytes.getvalue())

            # Save the PDF with compression
            pdf.save(output_path, garbage=4, deflate=True, clean=True)
            pdf.close()

    print(f"Conversion complete. {len(png_files)} files processed.")

def main():
    print_welcome_message()

    # Prompt for paths
    input_dir = sanitize_path(input("Enter the path to the directory containing PNG backgrounds: "))
    output_dir = sanitize_path(input("Enter the path to the output directory for PDFs: "))
    blank_pdf_path = sanitize_path(input("Enter the path to the blank PDF file: "))

    # Run the conversion
    png_to_pdf(input_dir, output_dir, blank_pdf_path)

    print_concluding_message()

if __name__ == "__main__":
    main()

# OLD UNSTYLIZED VERSION BELOW (THIS VERSION SHOULD WORK IF THE ABOVE DOES NOT)

import os
import io
from PIL import Image
import fitz  # PyMuPDF
from tqdm import tqdm

def sanitize_path(input_path):
    """Sanitize the file path by handling both paths with escaped spaces and quoted paths."""
    sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

def png_to_pdf(input_dir, output_dir, blank_pdf_path):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the blank PDF to get dimensions
    with fitz.open(blank_pdf_path) as blank_pdf:
        width, height = blank_pdf[0].rect.width, blank_pdf[0].rect.height

    # Get list of PNG files
    png_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]

    # Process each PNG in the input directory
    for filename in tqdm(png_files, desc="Converting PNGs to PDFs"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.pdf')

        # Open the PNG
        with Image.open(input_path) as img:
            # Create a new PDF
            pdf = fitz.open()
            page = pdf.new_page(width=width, height=height)

            # Convert PIL Image to PNG bytes (preserving transparency)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG', optimize=True, compress_level=9)
            img_bytes.seek(0)

            # Insert the image into the PDF
            page.insert_image(page.rect, stream=img_bytes.getvalue())

            # Save the PDF with compression
            pdf.save(output_path, garbage=4, deflate=True, clean=True)
            pdf.close()

    print(f"Conversion complete. {len(png_files)} files processed.")

# Prompt for paths
input_dir = sanitize_path(input("Enter the path to the directory containing PNG backgrounds: "))
output_dir = sanitize_path(input("Enter the path to the output directory for PDFs: "))
blank_pdf_path = sanitize_path(input("Enter the path to the blank PDF file: "))

# Run the conversion
png_to_pdf(input_dir, output_dir, blank_pdf_path)

# OLD UNSTYLIZED VERSION BELOW (THIS VERSION SHOULD WORK IF THE ABOVE DOES NOT)

# import os
# import io
# from PIL import Image
# import fitz  # PyMuPDF
# from tqdm import tqdm

# def sanitize_path(input_path):
#     """Sanitize the file path by handling both paths with escaped spaces and quoted paths."""
#     sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
#     if os.path.exists(sanitized):
#         return sanitized
#     else:
#         raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

# def png_to_pdf(input_dir, output_dir, blank_pdf_path):
#     # Ensure output directory exists
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # Open the blank PDF to get dimensions
#     with fitz.open(blank_pdf_path) as blank_pdf:
#         width, height = blank_pdf[0].rect.width, blank_pdf[0].rect.height

#     # Get list of PNG files
#     png_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]

#     # Process each PNG in the input directory
#     for filename in tqdm(png_files, desc="Converting PNGs to PDFs"):
#         input_path = os.path.join(input_dir, filename)
#         output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.pdf')

#         # Open the PNG
#         with Image.open(input_path) as img:
#             # Create a new PDF
#             pdf = fitz.open()
#             page = pdf.new_page(width=width, height=height)

#             # Convert PIL Image to PNG bytes (preserving transparency)
#             img_bytes = io.BytesIO()
#             img.save(img_bytes, format='PNG', optimize=True, compress_level=9)
#             img_bytes.seek(0)

#             # Insert the image into the PDF
#             page.insert_image(page.rect, stream=img_bytes.getvalue())

#             # Save the PDF with compression
#             pdf.save(output_path, garbage=4, deflate=True, clean=True)
#             pdf.close()

#     print(f"Conversion complete. {len(png_files)} files processed.")

# # Prompt for paths
# input_dir = sanitize_path(input("Enter the path to the directory containing PNG backgrounds: "))
# output_dir = sanitize_path(input("Enter the path to the output directory for PDFs: "))
# blank_pdf_path = sanitize_path(input("Enter the path to the blank PDF file: "))

# # Run the conversion
# png_to_pdf(input_dir, output_dir, blank_pdf_path)
import os
import re

def sanitize_path(input_path):
    sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

def replace_spaces_with_hyphens(directory):
    renamed_files = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if ' ' in filename:
                old_path = os.path.join(root, filename)
                new_filename = filename.replace(' ', '-')
                new_path = os.path.join(root, new_filename)
                
                # Rename the file
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")
                renamed_files += 1
    
    return renamed_files

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║        Welcome to the AthletiFi Filename Space Replacer!           ║
    ╚════════════════════════════════════════════════════════════════════╝

    This script will replace all spaces in filenames with hyphens.
    This is useful for preparing files for upload to S3 or other systems
    that may have issues with spaces in filenames.

    Please provide the directory containing the files you want to process.
    """)

    while True:
        directory = input("Enter the directory path containing the files: ")
        try:
            sanitized_directory = sanitize_path(directory)
            print(f"\nProcessing files in: {sanitized_directory}")
            renamed_count = replace_spaces_with_hyphens(sanitized_directory)
            print(f"\nProcess completed. {renamed_count} file(s) renamed.")
            break
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Please try again with a valid directory path.")

    print("\nThank you for using the AthletiFi Filename Space Replacer!")

if __name__ == "__main__":
    main()
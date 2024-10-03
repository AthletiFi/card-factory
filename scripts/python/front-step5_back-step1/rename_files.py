import os
import re
from collections import defaultdict
import shutil

def print_welcome_message():
    welcome_text = """
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                 Welcome to AthletiFi Card File Renamer                     ║
    ╚════════════════════════════════════════════════════════════════════════════╝

    This script is a crucial component in the AthletiFi player card generation process.
    It helps maintain consistency in file naming across different stages of card creation.

    ┌──────────────────────────────────────────┐
    │           Script Capabilities:           │
    └──────────────────────────────────────────┘
    1. Rename newly generated files to the standard naming convention
    2. Fix number sequence of generated player card BACKS to match FRONTS

    ┌──────────────────────────────────────────┐
    │           Before You Begin:              │
    └──────────────────────────────────────────┘
    1. Ensure you have the necessary permissions to rename files in the directories.
    2. For option 1: Have a directory with newly generated PDF files ready.
    3. For option 2: Prepare two directories:
       ✦ One with correctly named files (e.g., front cards)
       ✦ One with files to be renamed (e.g., back cards)

    ┌──────────────────────────────────────────┐
    │                 Important:               │
    └──────────────────────────────────────────┘
    ✦ This script will rename files directly. Ensure you have backups if needed.
    ✦ The script handles various naming patterns used in different card generations.
    ✦ For option 2, make sure you select the correct directories to avoid mistakes.

    Let's begin organizing your AthletiFi card files!
    """
    print(welcome_text)

def print_concluding_message(success):
    if success:
        concluding_message = """
        ┌──────────────────────────────────────────┐
        │               Process Complete!          │
        └──────────────────────────────────────────┘
        The file renaming process has been completed successfully.

        ┌──────────────────────────────────────────┐
        │               Next Steps:                │
        └──────────────────────────────────────────┘
        1. Verify that all files have been renamed correctly in the output directory.
        2. Check that the naming consistency aligns with your expectations:
           - For new files: Ensure they follow the standard naming convention.
           - For back cards: Confirm that their sequence matches the front cards.

        3. If you renamed back cards, proceed with the next steps in your workflow:
           - Merge QR codes with the renamed back card files.
           - Add any additional design elements or bleed as necessary.

        4. Always validate the correspondence between front and back cards
           using the validateFrontBackCorresponds.py script if available.

        Thank you for using the AthletiFi Card File Renamer!
        """
    else:
        concluding_message = """
        ┌──────────────────────────────────────────┐
        │              Process FAILED              │
        └──────────────────────────────────────────┘
        The file renaming process encountered errors and could not be completed.

        ┌──────────────────────────────────────────┐
        │               Next Steps:                │
        └──────────────────────────────────────────┘
        1. Review the error messages provided above.
        2. Check that the directory paths you provided are correct and accessible.
        3. Ensure you have the necessary permissions to access and modify the files.
        4. Try running the script again after addressing any issues.

        If you continue to experience problems, please refer to the main
        AthletiFi Card Artwork Generation Instructions.
        """
    print(concluding_message)

def sanitize_path(input_path):
    # Remove quotes and leading/trailing whitespace
    sanitized = input_path.strip().strip('\'"')
    # Replace escaped spaces with regular spaces
    sanitized = sanitized.replace("\\ ", " ")
    # Handle parentheses by removing any backslashes before them
    sanitized = sanitized.replace("\\(", "(").replace("\\)", ")")
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

def get_file_info(filename):
    patterns = [
        # Pattern 1 and 2
        re.compile(r'(Bronze|Silver) v2 - (.+?)_(CMYK|RGB)?_?(.+?)-(\d+)-with-text-layer_.+?_(\d+)\.pdf'),
        # Pattern 3
        re.compile(r'(Bronze|Silver) v2 - (.+?)_(CMYK|RGB)_(.+?)-(\d+)-with-text-layer_.+?vector border with bleed_(\d+)\.pdf'),
        # Pattern 4
        re.compile(
            r'(?P<edition>Bronze v[12]|Silver v[12]|Galaxy|Dragon Purple|Dragon Red|Universe Nebula|Space) - '
            r'(?P<background_name>[A-Za-z ]+)_'
            r'(?P<player_name>.+?)-'
            r'(?P<pose_number>\d+)-'
            r'(?P<pose_type>running|shooting|standing)-pose-'
            r'print-with-text-layer_NEW (rectangle )?'
            r'(?P<border_style>v[12] [A-Za-z]+ Border)_vector border [a-z]+_'
            r'(?P<edition_serial_number>\d+).pdf'
        ),
        # Pattern 5
        re.compile(r'(.+?)[-_](\d+)[-_](Bronze|Silver|Galaxy|Dragon Purple|Dragon Red|Universe Nebula|Space)[-_](.+?)[-_](\d+)\.pdf', re.IGNORECASE),
        # Pattern 6
        re.compile(r'(Bronze|Silver) v2 - ([A-Za-z ]+)_(.+?)-(\d+)-with-text-layer_(\d+)\.pdf')
    ]
    
    for pattern in patterns:
        match = pattern.match(filename)
        if match:
            if isinstance(match.groups()[0], str):
                return match.groups()
            else:
                return match.groupdict()
    
    return None

def format_player_name(name):
    return name  # Keep the name as is, including spaces and hyphens

def get_file_key(file_info):
    if isinstance(file_info, tuple):
        # For patterns 1, 2, 3, 5, 6
        return f"{file_info[1]}_{file_info[-2]}"  # player_name_pose_number
    elif isinstance(file_info, dict):
        # For pattern 4
        return f"{file_info['player_name']}_{file_info['pose_number']}"
    else:
        return None

def rename_new_files(directory):
    pattern1 = re.compile(r'(Bronze|Silver) v2 - (.+?)_CMYK_(.+?)-(\d+)-with-text-layer_CMYK_.+?_(\d+)\.pdf')
    pattern2 = re.compile(r'(Bronze|Silver) v2 - (.+?)_(.+?)-(\d+)-with-text-layer_digital vector border .+?_(\d+)_RGB\.pdf')
    pattern3 = re.compile(r'(Bronze|Silver) v2 - (.+?)_(CMYK|RGB)_(.+?)-(\d+)-with-text-layer_.+?vector border with bleed_(\d+)\.pdf')
    pattern4 = re.compile(
        r'(?P<edition>Bronze v[12]|Silver v[12]|Galaxy|Dragon Purple|Dragon Red|Universe Nebula|Space) - '
        r'(?P<background_name>[A-Za-z ]+)_'
        r'(?P<player_name>.+?)-'
        r'(?P<pose_number>\d+)-'
        r'(?P<pose_type>running|shooting|standing)-pose-'
        r'print-with-text-layer_NEW (rectangle )?'
        r'(?P<border_style>v[12] [A-Za-z]+ Border)_vector border [a-z]+_'
        r'(?P<edition_serial_number>\d+).pdf'
    )
    pattern5 = re.compile(r'(.+?)[-_](\d+)[-_](Bronze|Silver|Galaxy|Dragon Purple|Dragon Red|Universe Nebula|Space)[-_](.+?)[-_](\d+)\.pdf', re.IGNORECASE)
    pattern6 = re.compile(r'(Bronze|Silver) v2 - ([A-Za-z ]+)_(.+?)-(\d+)-with-text-layer_(\d+)\.pdf')

    player_sequence = defaultdict(lambda: 1)
    serial_ids = defaultdict(int)

    # First pass: collect all files and sort them
    all_files = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith('.pdf'):
                all_files.append((root, filename))
    
    # Sort files by player name and original sequence number
    all_files.sort(key=lambda x: (x[1].split('_')[1], int(x[1].split('_')[-1].split('.')[0])))

    # Second pass: rename files
    for root, filename in all_files:
        old_path = os.path.join(root, filename)
        match1 = pattern1.match(filename)
        match2 = pattern2.match(filename)
        match3 = pattern3.match(filename)
        match4 = pattern4.match(filename)
        match5 = pattern5.match(filename)
        match6 = pattern6.match(filename)

        if match1:
            edition, theme, name, player_number, serial_number = match1.groups()
            new_filename = f"{format_player_name(name)}-{player_number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
            player_sequence[name] += 1
        elif match2:
            edition, theme, name, player_number, serial_number = match2.groups()
            new_filename = f"{format_player_name(name)}-{player_number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
            player_sequence[name] += 1
        elif match4:
            data = match4.groupdict()
            player_name = format_player_name(data['player_name'])
            pose_type = data['pose_type']
            edition = data['edition']
            serial_ids[data['player_name']] += 1
            new_filename = f"{player_name}_{serial_ids[data['player_name']]}_{pose_type}_{edition}_front.pdf"
        elif match3:
            edition, theme, color_profile, name, player_number, serial_number = match3.groups()
            new_filename = f"{format_player_name(name)}-{player_number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
            player_sequence[name] += 1
        elif match5:
            name, number, edition, theme, sequence = match5.groups()
            formatted_name = format_player_name(name)
            new_filename = f"{formatted_name}-{number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
            player_sequence[name] += 1
        elif match6:
            edition, theme, name, player_number, serial_number = match6.groups()
            new_filename = f"{format_player_name(name)}-{player_number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
            player_sequence[name] += 1
        else:
            print(f"Skipping file with unrecognized pattern: {filename}")
            continue

        new_path = os.path.join(root, new_filename)
        os.rename(old_path, new_path)
        print(f"Renamed PDF: {filename} -> {new_filename}")

def fix_numbering(correct_dir, incorrect_dir):
    correct_files = defaultdict(list)
    incorrect_files = defaultdict(list)

    # Get the correct file names
    for filename in os.listdir(correct_dir):
        if filename.lower().endswith('.pdf'):
            file_info = get_file_info(filename)
            if file_info:
                key = get_file_key(file_info)
                correct_files[key].append((filename, file_info))

    # Get the incorrect file names
    for filename in os.listdir(incorrect_dir):
        if filename.lower().endswith('.pdf'):
            file_info = get_file_info(filename)
            if file_info:
                key = get_file_key(file_info)
                incorrect_files[key].append((filename, file_info))

    print(f"Found {len(correct_files)} unique correct file keys and {len(incorrect_files)} unique incorrect file keys.")

    # Rename incorrect files
    for key in incorrect_files:
        if key in correct_files:
            for i, (incorrect_filename, incorrect_info) in enumerate(sorted(incorrect_files[key])):
                if i < len(correct_files[key]):
                    correct_filename, correct_info = correct_files[key][i]
                    old_path = os.path.join(incorrect_dir, incorrect_filename)
                    new_path = os.path.join(incorrect_dir, correct_filename)
                    shutil.move(old_path, new_path)
                    print(f"Renamed: {incorrect_filename} -> {correct_filename}")
                else:
                    print(f"Warning: No matching correct file for {incorrect_filename}")
        else:
            print(f"Warning: No matching correct files for key {key}")
            print(f"  Incorrect file: {incorrect_files[key][0][0]}")
            closest_match = min(correct_files.keys(), key=lambda x: len(set(x.split('_')) ^ set(key.split('_'))))
            print(f"  Closest matching correct key: {closest_match}")
            print(f"  Example correct file: {correct_files[closest_match][0][0]}")

    print("File renaming completed.")

def main():
    print_welcome_message()

    print("""
    What would you like to do?

    1. Rename newly generated files to the standard naming convention
    2. Fix number sequence of generated player card BACKS which do not match the sequence of the initial generation for FRONTs
    """)
    
    choice = input("Enter your choice (1 or 2): ")

    success = False
    try:
        if choice == '1':
            print("\nFor renaming newly generated files:")
            print("Requirements: A directory containing PDF files to be renamed.")
            while True:
                directory = input("Enter the directory path containing the PDF files: ")
                try:
                    sanitized_directory = sanitize_path(directory)
                    print(f"Processing files in: {sanitized_directory}")
                    rename_new_files(sanitized_directory)
                    success = True
                    break
                except FileNotFoundError as e:
                    print(f"Error: {e}")
                    print("Please try again.")
        elif choice == '2':
            print("\nFor fixing numbering of generated player card BACKS which do not match the sequence of the initial generation for FRONTs:")
            print("Requirements:")
            print("1. Directory containing correctly named files (e.g., front cards)")
            print("2. Directory containing incorrectly named files to be renamed (e.g., back cards)")
            print("\nWARNING: Files in the incorrectly named directory will be renamed!")
            
            correct_dir = input("Enter the directory path containing CORRECTLY named files: ")
            incorrect_dir = input("Enter the directory path containing files to be RENAMED: ")
            
            try:
                correct_dir = sanitize_path(correct_dir)
                incorrect_dir = sanitize_path(incorrect_dir)
                fix_numbering(correct_dir, incorrect_dir)
                success = True
            except FileNotFoundError as e:
                print(f"Error: {e}")
        else:
            print("Invalid choice. Please run the script again and select 1 or 2.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print_concluding_message(success)

if __name__ == "__main__":
    main()

# OLD UNSTYLIZED VERSION BELOW (THIS VERSION SHOULD WORK IF THE ABOVE DOES NOT)

# import os
# import re
# from collections import defaultdict
# import shutil

# def sanitize_path(input_path):
#     sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
#     if os.path.exists(sanitized):
#         return sanitized
#     else:
#         raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

# def get_file_info(filename):
#     patterns = [
#         # Pattern 1 and 2
#         re.compile(r'(Bronze|Silver) v2 - (.+?)_(CMYK|RGB)?_?(.+?)-(\d+)-with-text-layer_.+?_(\d+)\.pdf'),
#         # Pattern 3
#         re.compile(r'(Bronze|Silver) v2 - (.+?)_(CMYK|RGB)_(.+?)-(\d+)-with-text-layer_.+?vector border with bleed_(\d+)\.pdf'),
#         # Pattern 4
#         re.compile(
#             r'(?P<edition>Bronze v[12]|Silver v[12]|Galaxy|Dragon Purple|Dragon Red|Universe Nebula|Space) - '
#             r'(?P<background_name>[A-Za-z ]+)_'
#             r'(?P<player_name>.+?)-'
#             r'(?P<pose_number>\d+)-'
#             r'(?P<pose_type>running|shooting|standing)-pose-'
#             r'print-with-text-layer_NEW (rectangle )?'
#             r'(?P<border_style>v[12] [A-Za-z]+ Border)_vector border [a-z]+_'
#             r'(?P<edition_serial_number>\d+).pdf'
#         ),
#         # Pattern 5
#         re.compile(r'(.+?)[-_](\d+)[-_](Bronze|Silver|Galaxy|Dragon Purple|Dragon Red|Universe Nebula|Space)[-_](.+?)[-_](\d+)\.pdf', re.IGNORECASE),
#         # Pattern 6
#         re.compile(r'(Bronze|Silver) v2 - ([A-Za-z ]+)_(.+?)-(\d+)-with-text-layer_(\d+)\.pdf')
#     ]
    
#     for pattern in patterns:
#         match = pattern.match(filename)
#         if match:
#             if isinstance(match.groups()[0], str):
#                 return match.groups()
#             else:
#                 return match.groupdict()
    
#     return None

# def format_player_name(name):
#     # parts = name.replace('-', ' ').split()
#     # return ' '.join(part.capitalize() for part in parts)
#     return name  # Keep the name as is, including spaces and hyphens


# def get_file_key(file_info):
#     if isinstance(file_info, tuple):
#         # For patterns 1, 2, 3, 5, 6
#         return f"{file_info[1]}_{file_info[-2]}"  # player_name_pose_number
#     elif isinstance(file_info, dict):
#         # For pattern 4
#         return f"{file_info['player_name']}_{file_info['pose_number']}"
#     else:
#         return None

# def rename_new_files(directory):
#     pattern1 = re.compile(r'(Bronze|Silver) v2 - (.+?)_CMYK_(.+?)-(\d+)-with-text-layer_CMYK_.+?_(\d+)\.pdf')
#     pattern2 = re.compile(r'(Bronze|Silver) v2 - (.+?)_(.+?)-(\d+)-with-text-layer_digital vector border .+?_(\d+)_RGB\.pdf')
#     pattern3 = re.compile(r'(Bronze|Silver) v2 - (.+?)_(CMYK|RGB)_(.+?)-(\d+)-with-text-layer_.+?vector border with bleed_(\d+)\.pdf')
#     pattern4 = re.compile(
#         r'(?P<edition>Bronze v[12]|Silver v[12]|Galaxy|Dragon Purple|Dragon Red|Universe Nebula|Space) - '
#         r'(?P<background_name>[A-Za-z ]+)_'
#         r'(?P<player_name>.+?)-'
#         r'(?P<pose_number>\d+)-'
#         r'(?P<pose_type>running|shooting|standing)-pose-'
#         r'print-with-text-layer_NEW (rectangle )?'
#         r'(?P<border_style>v[12] [A-Za-z]+ Border)_vector border [a-z]+_'
#         r'(?P<edition_serial_number>\d+).pdf'
#     )
#     pattern5 = re.compile(r'(.+?)[-_](\d+)[-_](Bronze|Silver|Galaxy|Dragon Purple|Dragon Red|Universe Nebula|Space)[-_](.+?)[-_](\d+)\.pdf', re.IGNORECASE)
#     pattern6 = re.compile(r'(Bronze|Silver) v2 - ([A-Za-z ]+)_(.+?)-(\d+)-with-text-layer_(\d+)\.pdf')

#     player_sequence = defaultdict(lambda: 1)
#     serial_ids = defaultdict(int)

#     # First pass: collect all files and sort them
#     all_files = []
#     for root, dirs, files in os.walk(directory):
#         for filename in files:
#             if filename.lower().endswith('.pdf'):
#                 all_files.append((root, filename))
    
#     # Sort files by player name and original sequence number
#     all_files.sort(key=lambda x: (x[1].split('_')[1], int(x[1].split('_')[-1].split('.')[0])))

#     # Second pass: rename files
#     for root, filename in all_files:
#         old_path = os.path.join(root, filename)
#         match1 = pattern1.match(filename)
#         match2 = pattern2.match(filename)
#         match3 = pattern3.match(filename)
#         match4 = pattern4.match(filename)
#         match5 = pattern5.match(filename)
#         match6 = pattern6.match(filename)

#         if match1:
#             edition, theme, name, player_number, serial_number = match1.groups()
#             new_filename = f"{format_player_name(name)}-{player_number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
#             player_sequence[name] += 1
#         elif match2:
#             edition, theme, name, player_number, serial_number = match2.groups()
#             new_filename = f"{format_player_name(name)}-{player_number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
#             player_sequence[name] += 1
#         elif match4:
#             data = match4.groupdict()
#             player_name = format_player_name(data['player_name'])
#             pose_type = data['pose_type']
#             edition = data['edition']
#             serial_ids[data['player_name']] += 1
#             new_filename = f"{player_name}_{serial_ids[data['player_name']]}_{pose_type}_{edition}_front.pdf"
#         elif match3:
#             edition, theme, color_profile, name, player_number, serial_number = match3.groups()
#             new_filename = f"{format_player_name(name)}-{player_number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
#             player_sequence[name] += 1
#         elif match5:
#             name, number, edition, theme, sequence = match5.groups()
#             formatted_name = format_player_name(name)
#             new_filename = f"{formatted_name}-{number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
#             player_sequence[name] += 1
#         elif match6:
#             edition, theme, name, player_number, serial_number = match6.groups()
#             new_filename = f"{format_player_name(name)}-{player_number}-{edition}-{theme}-{player_sequence[name]:02d}.pdf"
#             player_sequence[name] += 1
#         else:
#             print(f"Skipping file with unrecognized pattern: {filename}")
#             continue

#         new_path = os.path.join(root, new_filename)
#         os.rename(old_path, new_path)
#         print(f"Renamed PDF: {filename} -> {new_filename}")

# def fix_numbering(correct_dir, incorrect_dir):
#     correct_files = defaultdict(list)
#     incorrect_files = defaultdict(list)

#     # Get the correct file names
#     for filename in os.listdir(correct_dir):
#         if filename.lower().endswith('.pdf'):
#             file_info = get_file_info(filename)
#             if file_info:
#                 key = get_file_key(file_info)
#                 correct_files[key].append((filename, file_info))

#     # Get the incorrect file names
#     for filename in os.listdir(incorrect_dir):
#         if filename.lower().endswith('.pdf'):
#             file_info = get_file_info(filename)
#             if file_info:
#                 key = get_file_key(file_info)
#                 incorrect_files[key].append((filename, file_info))

#     print(f"Found {len(correct_files)} unique correct file keys and {len(incorrect_files)} unique incorrect file keys.")

#     # Rename incorrect files
#     for key in incorrect_files:
#         if key in correct_files:
#             for i, (incorrect_filename, incorrect_info) in enumerate(sorted(incorrect_files[key])):
#                 if i < len(correct_files[key]):
#                     correct_filename, correct_info = correct_files[key][i]
#                     old_path = os.path.join(incorrect_dir, incorrect_filename)
#                     new_path = os.path.join(incorrect_dir, correct_filename)
#                     shutil.move(old_path, new_path)
#                     print(f"Renamed: {incorrect_filename} -> {correct_filename}")
#                 else:
#                     print(f"Warning: No matching correct file for {incorrect_filename}")
#         else:
#             print(f"Warning: No matching correct files for key {key}")
#             print(f"  Incorrect file: {incorrect_files[key][0][0]}")
#             closest_match = min(correct_files.keys(), key=lambda x: len(set(x.split('_')) ^ set(key.split('_'))))
#             print(f"  Closest matching correct key: {closest_match}")
#             print(f"  Example correct file: {correct_files[closest_match][0][0]}")

#     print("File renaming completed.")

# def main():
#     print("""
#     ╔════════════════════════════════════════════════════════════════════╗
#     ║               Welcome to the AthletiFi Card Renamer!               ║
#     ╚════════════════════════════════════════════════════════════════════╝

#     What would you like to do?

#     1. Rename newly generated files to the standard naming convention
#     2. Fix number sequence of generated player card BACKS which do not match the sequence of the initial generation for FRONTs
#     """)
    
#     choice = input("Enter your choice (1 or 2): ")

#     if choice == '1':
#         print("\nFor renaming newly generated files:")
#         print("Requirements: A directory containing PDF files to be renamed.")
#         while True:
#             directory = input("Enter the directory path containing the PDF files: ")
#             try:
#                 sanitized_directory = sanitize_path(directory)
#                 print(f"Processing files in: {sanitized_directory}")
#                 rename_new_files(sanitized_directory)
#                 break
#             except FileNotFoundError as e:
#                 print(f"Error: {e}")
#                 print("Please try again.")
#     elif choice == '2':
#         print("\nFor fixing numbering of generated player card BACKS which do not match the sequence of the initial generation for FRONTs:")
#         print("Requirements:")
#         print("1. Directory containing correctly named files (e.g., front cards)")
#         print("2. Directory containing incorrectly named files to be renamed (e.g., back cards)")
#         print("\nWARNING: Files in the incorrectly named directory will be renamed!")
        
#         correct_dir = input("Enter the directory path containing CORRECTLY named files: ")
#         incorrect_dir = input("Enter the directory path containing files to be RENAMED: ")
        
#         try:
#             correct_dir = sanitize_path(correct_dir)
#             incorrect_dir = sanitize_path(incorrect_dir)
#             fix_numbering(correct_dir, incorrect_dir)
#         except FileNotFoundError as e:
#             print(f"Error: {e}")
#     else:
#         print("Invalid choice. Please run the script again and select 1 or 2.")

# if __name__ == "__main__":
#     main()
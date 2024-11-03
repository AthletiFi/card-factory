import re
import csv
import os

def sanitize_path(input_path):
    sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

def parse_filename(filename):
    # Store original filename
    original_filename = filename
    
    patterns = [
        # New pattern
        re.compile(r'([A-Za-z\' ]+)-([A-Za-z\' ]+)-(\d+)-(Bronze|Silver)-(.+?)-(\d+)\.pdf'),
        # Old patterns
        re.compile(r'(Bronze|Silver) v2 - (.+?)_(CMYK|RGB)?_?(.+?)-(\d+)-with-text-layer_.+?_(\d+)\.pdf'),
        re.compile(r'(Bronze|Silver) v2 - (.+?)_(CMYK|RGB)_(.+?)-(\d+)-with-text-layer_.+?vector border with bleed_(\d+)\.pdf'),
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
        re.compile(r'(.+?)[-_](\d+)[-_](Bronze|Silver|Galaxy|Dragon Purple|Dragon Red|Universe Nebula|Space)[-_](.+?)[-_](\d+)\.pdf', re.IGNORECASE),
        re.compile(r'(Bronze|Silver) v2 - ([A-Za-z ]+)_(.+?)-(\d+)-with-text-layer_(\d+)\.pdf')
    ]
    
    for pattern in patterns:
        match = pattern.match(filename)
        if match:
            if isinstance(match.groupdict(), dict) and match.groupdict():
                # Handle named groups
                data = match.groupdict()
                full_name = data.get('player_name', '')
                names = full_name.split('-', 1) if '-' in full_name else [full_name, '']
                first_name = names[0]
                last_name = names[1] if len(names) > 1 else ""
            else:
                # Handle unnamed groups for new pattern (first_name-last_name-number-edition-theme-serial)
                groups = match.groups()
                if len(groups) == 6 and groups[3] in ['Bronze', 'Silver']:  # New pattern
                    first_name = groups[0]
                    last_name = groups[1]
                    jersey_number = groups[2]
                    edition = groups[3]
                    theme = groups[4]
                    serial_number = groups[5]
                elif len(groups) == 6:  # Most old patterns
                    edition = groups[0]
                    theme = groups[1]
                    full_name = groups[3]
                    names = full_name.split('-', 1) if '-' in full_name else [full_name, '']
                    first_name = names[0]
                    last_name = names[1] if len(names) > 1 else ""
                    jersey_number = groups[4]
                    serial_number = groups[5]
                else:  # Other old patterns
                    full_name = groups[2] if len(groups) > 2 else ''
                    names = full_name.split('-', 1) if '-' in full_name else [full_name, '']
                    first_name = names[0]
                    last_name = names[1] if len(names) > 1 else ""
                    jersey_number = groups[4] if len(groups) > 4 else ''
                    edition = groups[0] if groups[0] in ['Bronze', 'Silver'] else ''
                    theme = groups[1] if groups[1] not in ['Bronze', 'Silver'] else ''
                    serial_number = groups[-1]

            # Convert filename to webp and replace spaces with hyphens
            webp_filename = original_filename.rsplit('.', 1)[0] + '.webp'
            webp_filename = webp_filename.replace(' ', '-')

            return {
                'first_name': first_name,
                'last_name': last_name,
                'jersey_number': jersey_number,
                'edition': edition,
                'theme': theme,
                'serial_number': serial_number,
                'original_filename': original_filename,
                'webp_filename': webp_filename
            }
    
    return None

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║           Welcome to the AthletiFi Card Filename Parser!           ║
    ╚════════════════════════════════════════════════════════════════════╝

    This script will parse your AthletiFi card filenames and extract key information.
    
    Requirements:
    1. A CSV file containing a list of your card filenames (PDF format).
    2. The CSV should have a header row and the filenames in the first column.

    The script will generate a new CSV file named 'parsed_card_data.csv' with the 
    extracted information, including:
    ✦ First Name
    ✦ Last Name
    ✦ Jersey Number
    ✦ Edition (Bronze/Silver)
    ✦ Theme
    ✦ Serial Number
    ✦ Original Filename (PDF)
    ✦ WebP Filename (converted to .webp and with spaces replaced by hyphens)
    
    Let's get started!
    """)

    while True:
        csv_path = input("\nPlease enter the path to the CSV file containing PDF filenames: ")
        try:
            sanitized_csv_path = sanitize_path(csv_path)
            print(f"\nProcessing file: {sanitized_csv_path}")
            break
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Please try again with a valid file path.")

    # Read filenames from the CSV file
    filenames = []
    with open(sanitized_csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row if there is one
        for row in reader:
            filenames.append(row[0])  # Assuming the filenames are in the first column

    # Parse filenames and store results
    parsed_data = []
    for filename in filenames:
        result = parse_filename(filename)
        if result:
            parsed_data.append(result)
        else:
            print(f"Warning: Unable to parse filename: {filename}")

    # Write parsed data to a CSV file for easy viewing and further processing
    output_csv_path = 'parsed_card_data.csv'
    fieldnames = ['first_name', 'last_name', 'jersey_number', 'edition', 'theme', 'serial_number', 'original_filename', 'webp_filename']
    
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in parsed_data:
            writer.writerow(row)

    print(f"\nParsing complete! {len(parsed_data)} filenames processed.")
    print(f"Results have been written to: {output_csv_path}")
    print("\nThank you for using the AthletiFi Card Filename Parser!")

if __name__ == "__main__":
    main()
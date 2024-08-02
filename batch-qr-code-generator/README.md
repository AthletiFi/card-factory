# AthletiFi Batch QR Code Generator

## Overview

The Batch QR Code Generator is a Node.js application that generates QR codes in bulk from a list of URLs provided in a CSV file. This tool is designed to generate QR codes for the print version of AthletiFi Player Cards, linking them to their digital counterparts.

## Requirements

- Node.js: The runtime environment required to execute the script.
- npm: To manage the project's dependencies.
- CSV File: A CSV file containing URLs and filenames for QR code generation. The file should have columns named 'qrcode_url' (or 'qr_code_url' or 'url') and 'card_filename'.

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/AthletiFi/card-factory.git
   ```

2. Navigate to the `batch-qr-code-generator` directory and install dependencies:

   ```sh
   cd card-factory/batch-qr-code-generator
   npm install
   ```

## Usage

1. **Set Up**: Prepare a CSV file with a list of URLs and corresponding filenames. Ensure each row contains a URL (under 'qrcode_url', 'qr_code_url', or 'url' column) and a filename (under 'card_filename' column).

2. Place the CSV file in the `batch-qr-code-generator` directory.

3. **Run the Script**: Execute the script by running:

   ```sh
   node batch-generate-qr.js
   ```

4. **Enter the CSV file path**: When prompted, enter the file path for your CSV file. If the file is in the current directory, you can just enter the filename (e.g., `Summer-Select-24_qr_code_ids.csv`).

5. The script will generate QR codes and save them as SVG files in the `qr_codes` directory. Each QR code will be named to match its corresponding card filename (with .svg extension).

## Customization

You can customize the appearance and properties of the QR codes by editing the `options.json` file in the src directory. You can also generate your own `options.json` file by visiting [https://qr-code-styling.com/](https://qr-code-styling.com/).

## Troubleshooting

- CSV Format Issues: Ensure your CSV has the correct column headers ('qrcode_url' or 'qr_code_url' or 'url', and 'card_filename').
- Module Not Found Errors: If you encounter module-related errors, try reinstalling the dependencies with `npm install`.
- Output Directory Issues: The script will create a `qr_codes` directory if it doesn't exist. Ensure you have write permissions in the current directory.

For any other issues or questions, please open an [issue](https://github.com/AthletiFi/card-factory/issues).

## License

This script is part of the `card-factory` repository and is licensed under the BSD 3-Clause License. For full license details, see the [LICENSE](LICENSE) file in the main repository.
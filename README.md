# AthletiFi Player Card Generation

## Overview

Thee `card-factory` serves as the central hub for the development and maintenance of tools and scripts that are used in the creation process of AthletiFi digital player cards.  This project contains the scripts, assets, and instructions necessary for the generation process. It provides a structured workflow for creating both digital and print versions of player cards, including front and back designs.

## Directory Structure

- `assets/`: Contains all static assets for card generation
  - `actions/`: Adobe actions for Illustrator and Photoshop
  - `backgrounds/`: Card background files in PDF and PNG formats
  - `borders/`: Card border files for digital and print versions
  - `csv/`: Example CSV files for player information
  - `fonts/`: Custom fonts used in card designs
  - `templates/`: Adobe Illustrator templates for text layers
- `scripts/`: Houses all scripts used in the card generation process
  - `adobe/`: Scripts for Adobe products (Illustrator, Photoshop)
  - `node/`: Node.js scripts for QR code generation
  - `python/`: Python scripts for various data processing tasks
  - `shell/`: Shell scripts for image processing
- `docs/`: Detailed documentation for each part of the process

## Prerequisites

- Adobe Illustrator
- Adobe Photoshop
- Python
- Node.js
- ImageMagick
- cwebp

## Setup

1. Install all prerequisites mentioned above
2. Clone this repository to your local machine
3. Install Python dependencies: `pip install -r scripts/python/requirements.txt`
4. Install Node.js dependencies:

   ```shell
   cd scripts/node/batch-qr-code-generator
   npm install
   ```

## Usage

The card generation process is divided into multiple steps, each utilizing different scripts and tools. For detailed instructions on each step, please refer to the documentation in the `docs/` directory:

- [Process Overview](docs/overview.md)
- [Front Card Generation](docs/front-card-generation.md)
- [Back Card Generation](docs/back-card-generation.md)
- [Tools and Scripts](docs/tools-and-scripts.md)

## Workflow Summary

1. Process player photos (Adobe Photoshop)
2. Create text layers (Adobe Illustrator)
3. Merge text layers with player photos
4. Prepare backgrounds
5. Combine background and player components
6. Add borders for digital and print versions
7. Add trim marks (print version only)
8. Convert to PNG and WebP (digital version only)
9. Generate and add QR codes (for card backs)
10. Format QR codes in Illustrator
11. Add QR codes to card backs
12. Add trim marks to card backs

Each of these steps involves specific scripts and actions, detailed in the documentation.

## Troubleshooting

For common issues and their solutions, see our [Troubleshooting Guide](docs/troubleshooting.md).

## Contributing

We welcome contributions to improve the card generation process. Please ensure you update relevant documentation when making changes.

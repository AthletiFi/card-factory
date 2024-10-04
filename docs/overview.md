# AthletiFi Player Card Generation Process Overview

## Introduction

The AthletiFi player card generation process is a multi-step workflow that creates both digital and print versions of player cards. This document provides a high-level overview of the entire process, from initial player photo processing to the final card output.

## Process Flow

1. **Front Card Generation**
   a. Process player photos: Use Photoshop to cut out players, apply auto-adjustments, add texture and clarity, and position within a specific safe box on a standardized canvas.
   b. Create text layers: Use Illustrator to create dynamic text boxes for player names and numbers, importing data from a CSV file and generating SVG files for each player's text layers.
   c. Merge text layers with player photos: Combine the SVG text layers with corresponding player photo PNGs, outputting individual PDFs for each player.
   d. Prepare backgrounds: Create a blank PDF template with correct dimensions, then convert background design PNGs to PDFs, ensuring proper positioning and transparency.
   e. Combine background and player components: Merge the background PDFs with player photo + text layer PDFs, then rename files following a standard naming convention.
   f. Add borders for digital and print versions: Overlay specific border designs onto the combined background/player PDFs, creating separate versions for digital and print cards.
   g. Add trim marks (print version only): Use an Illustrator action to adjust the artboard size, extend artwork to the bleed area, add trim marks and save the file with proper print specifications.

2. **Back Card Generation**
   a. Make player photos blank and generate background combos: Create blank versions of player photo/text layer PDFs, combine with background designs, ensuring naming consistency with front card files.
   b. Render borders blue and add to cards: Modify vector borders to a blue color scheme, add QR frame background, then overlay onto back card designs using an Illustrator script.
   c. Add database records to link QR codes: Generate and execute SQL queries to add or update database records, ensuring proper linking between physical cards and digital profiles.
   d. Generate QR codes: Process CSV data to prepare QR code information, then use a Node.js script to batch generate QR codes as SVG files.
   e. Format QR codes in Illustrator: Apply styling to QR codes using an Illustrator action, converting the formatted QR codes from SVG to PDF format.
   f. Add QR codes to card backs: Use an Illustrator script to overlay the formatted QR code PDFs onto the back card designs.
   g. Add trim marks: Apply the same Illustrator action used for front cards to adjust the artboard size, extend artwork to the bleed area, add trim marks, and save with proper print specifications.

## Key Components

- **Player Photos**: High-quality images of players, processed to fit the card design.
- **Text Layers**: Player names and numbers, formatted according to card specifications.
- **Backgrounds**: Various design options for card backgrounds.
- **Borders**: Specific designs for digital and print versions of the cards.
- **QR Codes**: Unique codes linking to each player's digital profile.

## Tools and Technologies

- Adobe Photoshop: For photo processing and editing
- Adobe Illustrator: For text layout, card design, and final assembly
- Python: For various data processing and file manipulation tasks
- Node.js: For QR code generation
- ImageMagick and cwebp: For image conversion and optimization

## Output

The process produces two main types of output:

1. **Digital Cards**: High-resolution PNG and optimized WebP files for digital distribution and display.
2. **Print Cards**: High-quality PDF files with trim marks and bleed areas, ready for professional printing.

## Database Integration

The process includes steps to ensure each physical card is linked to the corresponding digital profile in the AthletiFi database, facilitating seamless integration between the physical and digital aspects of the AthletiFi platform.

## Customization and Scalability

This process is designed to handle bulk card generation while allowing for customization of individual cards. It can be scaled to accommodate varying numbers of players and different card designs.

For detailed instructions on each step of the process, please refer to the following documents:

- [Front Card Generation](front-card-generation.md)
- [Back Card Generation](back-card-generation.md)
- [Tools and Scripts](tools-and-scripts.md)
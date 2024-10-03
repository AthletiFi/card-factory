const readline = require('readline');
const fs = require('fs');
const { generateQRFromCSV } = require('./src/index');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to check if the input is a valid path
const isValidPath = (path) => {
  path = path.trim().replace(/^['"](.+)['"]$/, '$1');
  const pathRegex = /\.csv$/i;
  return pathRegex.test(path);
};

function printWelcomeMessage() {
    console.log(`
╔════════════════════════════════════════════════════════════════════════════╗
║             Welcome to AthletiFi QR Code Batch Generator                   ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│ This tool generates QR codes for AthletiFi player cards, linking each    │
│ card to its unique digital experience.                                   │
└──────────────────────────────────────────────────────────────────────────┘

Key Features:
✦ Generates SVG QR codes from URLs provided in a CSV file
✦ Automatically names QR codes to match corresponding player card filenames
✦ Uses custom styling options for visually appealing QR codes

Please follow the prompts to begin generating your QR codes.
    `);
}

function printConcludingMessage(totalGenerated) {
    console.log(`
╔════════════════════════════════════════════════════════════════════════════╗
║                   QR Code Batch Generation Complete                        ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│ All QR codes have been successfully generated and saved.                 │
└──────────────────────────────────────────────────────────────────────────┘

Total QR codes generated: ${totalGenerated}

Next Steps:
1. Check the 'qr_codes' directory for all generated SVG files.
2. Verify that each QR code corresponds to the correct player card.
3. Proceed with integrating these QR codes into your player card designs.

Thank you for using the AthletiFi QR Code Batch Generator!
    `);
}

async function main() {
    printWelcomeMessage();

    rl.question('Please enter the path to your CSV file: ', async (csvFilePath) => {
        csvFilePath = csvFilePath.trim().replace(/^['"](.+)['"]$/, '$1');

        if (!isValidPath(csvFilePath)) {
            console.error(`Error: The input '${csvFilePath}' is not a valid path for a CSV file.`);
            rl.close();
            return;
        }

        if (!fs.existsSync(csvFilePath)) {
            console.error(`Error: ${csvFilePath} does not exist.`);
            rl.close();
            return;
        }

        try {
            const totalGenerated = await generateQRFromCSV(csvFilePath);
            printConcludingMessage(totalGenerated);
        } catch (error) {
            console.error(`An error occurred while generating QR codes: ${error.message}`);
        } finally {
            rl.close();
        }
    });
}

main();
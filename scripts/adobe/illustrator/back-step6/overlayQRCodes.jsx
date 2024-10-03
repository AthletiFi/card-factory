// QR Code Overlay Script for Adobe Illustrator (Player Card Backs)
#target illustrator

// Updated intro function
function showIntro() {
    alert(
        "----------------------------------------\n" +
        "QR Code Overlay Script for Player Card Backs\n" +
        "----------------------------------------\n\n" +
        "Welcome to the QR Code Overlayer! This script is designed to overlay\n" +
        "QR codes onto the backs of the print version of AthletiFi player cards.\n\n" +
        "Requirements:\n" +
        "1. A folder containing the back designs of player cards (PDFs)\n" +
        "2. A folder containing the formatted QR code PDFs\n" +
        "3. An output folder for the combined PDFs\n\n" +
        "The script will:\n" +
        "✦ Match each back design with its corresponding QR code\n" +
        "✦ Overlay the QR code on the card back\n" +
        "✦ Save new PDFs with '_QR' appended to the filename\n\n" +
        "Ensure that your QR codes are properly formatted and sized before running\n" +
        "this script.\n\n" +
        "Let's complete the final step of your player card creation!"
    );
}

// Updated function to normalize filenames for comparison
function normalizeFilename(filename) {
    // Decode URL-encoded characters first
    var decoded = decodeURI(filename);
    return decoded.replace(/[-\s]/g, '_')  // Replace hyphens and spaces with underscores
                  .replace(/__+/g, '_')    // Replace multiple underscores with a single one
                  .replace(/_qr\.pdf$/i, '.pdf')  // Remove '_qr' before '.pdf'
                  .toLowerCase();
}

// Main script
try {
    // Show intro
    showIntro();

    // Select folders containing back designs and QR code PDFs
    var backFolder = Folder.selectDialog("Select folder with player card back PDFs");
    var qrFolder = Folder.selectDialog("Select folder with QR code PDFs");
    var outputFolder = Folder.selectDialog("Select output folder for combined PDFs");

    if (!backFolder || !qrFolder || !outputFolder) {
        throw new Error("Folder selection cancelled. Please run the script again and select all required folders.");
    }

    // Get all PDF files in both folders
    var backFiles = backFolder.getFiles("*.pdf");
    var qrFiles = qrFolder.getFiles("*.pdf");

    // Create a map of normalized QR filenames to actual QR files
    var qrFileMap = {};
    for (var i = 0; i < qrFiles.length; i++) {
        var normalizedName = normalizeFilename(qrFiles[i].name);
        qrFileMap[normalizedName] = qrFiles[i];
    }

    // Process each back design file
    var processedCount = 0;
    var errorCount = 0;
    for (var i = 0; i < backFiles.length; i++) {
        var backFile = backFiles[i];
        var normalizedBackName = normalizeFilename(backFile.name);
        
        // Find matching QR code file
        var qrFile = qrFileMap[normalizedBackName];

        if (qrFile) {
            // Open the back design PDF
            var doc = app.open(backFile);

            // Place the QR code PDF
            var qrItem = doc.placedItems.add();
            qrItem.file = qrFile;

            // Set the position to [0, doc.height] to place it directly on top of the background
            qrItem.position = [0, doc.height];

            // Save and close the document
            var saveOptions = new PDFSaveOptions();
            var saveFile = new File(outputFolder + "/" + backFile.name.replace(".pdf", "_QR.pdf"));
            doc.saveAs(saveFile, saveOptions);
            doc.close();

            processedCount++;
        } else {
            errorCount++;
            alert("No matching QR code found for: " + backFile.name + "\nNormalized name: " + normalizedBackName);
        }
    }

    // Show completion message
    alert(
        "----------------------------------------\n" +
        "Player Card Backs Processing Complete\n" +
        "----------------------------------------\n\n" +
        "✦ Total back designs processed: " + backFiles.length + "\n" +
        "✦ Successfully overlaid QR codes: " + processedCount + "\n" +
        "✦ Errors (no matching QR code): " + errorCount + "\n\n" +
        "New PDFs with overlaid QR codes have been saved in the selected output folder.\n" +
        "These files are now ready for final review and printing.\n\n" +
        "Next steps:\n" +
        "1. Review the generated PDFs to ensure QR codes are correctly positioned.\n" +
        "2. Proceed with printing or digital distribution as needed.\n\n" +
        "Thank you for using the QR Code Overlay Script for Player Card Backs!"
    );

} catch (e) {
    alert("An error occurred: " + e.message + "\nPlease check your file names and folder structure, then try again.");
}
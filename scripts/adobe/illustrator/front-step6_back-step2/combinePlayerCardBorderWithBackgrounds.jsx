#target illustrator

// Function to show introduction
function showIntro() {
    alert(
        "----------------------------------------\n" +
        "Border Overlay Script for Player Cards\n" +
        "----------------------------------------\n\n" +
        "Welcome to the Border Overlayer! This script is designed to add\n" +
        "borders to both the fronts and backs of AthletiFi player cards.\n\n" +
        "Requirements:\n" +
        "1. A folder containing player card designs (PDFs)\n" +
        "2. A border PDF file (front or back, depending on your current task)\n" +
        "3. An output folder for the combined PDFs\n\n" +
        "The script will:\n" +
        "✦ Add the border to each card design\n" +
        "✦ Allow you to adjust the offset if needed\n" +
        "✦ Save new PDFs in the specified output folder\n\n" +
        "Ensure that your border file is properly formatted and sized before running\n" +
        "this script.\n\n" +
        "Let's add the finishing touch to your player cards!"
    );
}

// Function to combine border with background
function combineBorderWithBackground(backgroundFile, borderFile, outputFolder, xOffset, yOffset) {
    var backgroundDoc = app.open(backgroundFile);
    
    // Place the border file
    var borderItem = backgroundDoc.placedItems.add();
    borderItem.file = borderFile;
    
    // Ensure the border covers the entire artboard
    borderItem.width = backgroundDoc.width;
    borderItem.height = backgroundDoc.height;
    
    // Move the border to the correct position
    borderItem.transform(app.getTranslationMatrix(xOffset, -yOffset));
    
    // Move border to top layer
    borderItem.move(backgroundDoc, ElementPlacement.PLACEATBEGINNING);
    
    // Save as PDF
    var outputFile = new File(outputFolder + "/" + backgroundFile.name);
    var saveOptions = new PDFSaveOptions();
    saveOptions.compatibility = PDFCompatibility.ACROBAT5;
    saveOptions.generateThumbnails = true;
    saveOptions.preserveEditability = true;
    
    backgroundDoc.saveAs(outputFile, saveOptions);
    
    // Close the document
    backgroundDoc.close(SaveOptions.DONOTSAVECHANGES);
}

// Function to perform a dummy operation
function performDummyOperation(borderFile) {
    // Create a new document
    var dummyDoc = app.documents.add();
    
    // Place the border file
    var borderItem = dummyDoc.placedItems.add();
    borderItem.file = borderFile;
    
    // Close the document without saving
    dummyDoc.close(SaveOptions.DONOTSAVECHANGES);
}

// Function to prompt user for offset values
function promptForOffset() {
    var setOffset = confirm("Would you like to set a custom offset for the border?\nClick OK to set custom offset, or Cancel to use default (0,0).");
    if (setOffset) {
        var xOffset = parseFloat(prompt("Enter X offset (in points):", "0"));
        var yOffset = parseFloat(prompt("Enter Y offset (in points):", "0"));
        return { x: xOffset, y: yOffset };
    }
    return { x: 0, y: 0 };
}

// Function to check if offset is correct
function checkOffset(backgroundFile, borderFile, xOffset, yOffset) {
    var testDoc = app.open(backgroundFile);
    
    // Place the border file
    var borderItem = testDoc.placedItems.add();
    borderItem.file = borderFile;
    
    // Ensure the border covers the entire artboard
    borderItem.width = testDoc.width;
    borderItem.height = testDoc.height;
    
    // Move the border to the correct position
    borderItem.transform(app.getTranslationMatrix(xOffset, -yOffset));
    
    // Move border to top layer
    borderItem.move(testDoc, ElementPlacement.PLACEATBEGINNING);
    
    // Fit artboard to window
    app.executeMenuCommand('fitall');
    
    // Redraw the screen to ensure the changes are visible
    app.redraw();
    
    // Prompt user to check offset
    var isOffsetCorrect = confirm("Please check if the border is correctly positioned.\nClick Yes if it's good, or No to adjust.");
    
    // Close the document without saving
    testDoc.close(SaveOptions.DONOTSAVECHANGES);
    
    return isOffsetCorrect;
}

// Main script
function main() {
    // Show introduction
    showIntro();

    // Prompt user for folders
    var backgroundFolder = Folder.selectDialog("Select folder with player card PDFs");
    var borderFile = File.openDialog("Select border PDF file");
    var outputFolder = Folder.selectDialog("Select output folder for combined PDFs");
    
    if (backgroundFolder != null && borderFile != null && outputFolder != null) {
        // Perform dummy operation to initialize Illustrator
        performDummyOperation(borderFile);
        
        var offset;
        var isOffsetCorrect = false;
        var backgroundFiles = backgroundFolder.getFiles("*.pdf");
        
        if (backgroundFiles.length === 0) {
            alert("No PDF files found in the selected folder.");
            return;
        }
        
        do {
            offset = promptForOffset();
            
            // Check offset with the first file
            isOffsetCorrect = checkOffset(backgroundFiles[0], borderFile, offset.x, offset.y);
            
            if (!isOffsetCorrect) {
                alert("Border position not correct. Please try again with different offset values.");
            }
        } while (!isOffsetCorrect);
        
        // Process all PDF files in the background folder
        var processedCount = 0;
        var errorCount = 0;
        for (var i = 0; i < backgroundFiles.length; i++) {
            try {
                combineBorderWithBackground(backgroundFiles[i], borderFile, outputFolder, offset.x, offset.y);
                processedCount++;
            } catch (e) {
                alert("Error processing file " + backgroundFiles[i].name + ": " + e);
                errorCount++;
            }
            $.sleep(100); // Short pause between operations
        }
        
        alert(
            "----------------------------------------\n" +
            "Border Addition Complete\n" +
            "----------------------------------------\n\n" +
            "✦ Total cards processed: " + backgroundFiles.length + "\n" +
            "✦ Successfully added borders: " + processedCount + "\n" +
            "✦ Errors: " + errorCount + "\n\n" +
            "New PDFs with borders have been saved in the selected output folder.\n" +
            "These files are now ready for the next step in your workflow.\n\n" +
            "Next steps:\n" +
            "1. Review the generated PDFs to ensure borders are correctly positioned.\n" +
            "2. Proceed with the next step in your card creation process.\n\n" +
            "Thank you for using the Border Overlay Script!"
        );
    } else {
        alert("Operation cancelled. Please select all required folders and files.");
    }
}

// Run the script
main();
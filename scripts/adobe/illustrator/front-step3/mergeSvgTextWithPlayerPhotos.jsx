#target illustrator

function promptForFolder(message) {
    return Folder.selectDialog(message);
}

function combineImages(svgFolderPath, pngFolderPath, outputFolderPath) {
    var svgFiles = Folder(svgFolderPath).getFiles("*.svg");
    $.writeln("Found " + svgFiles.length + " SVG files");
    var errorMessages = [];

    for (var i = 0; i < svgFiles.length; i++) {
        try {
            var svgFile = svgFiles[i];
            var playerName = decodeURI(svgFile.name);
            $.writeln("Processing: " + playerName);

            var playerPngs = findPlayerPngs(pngFolderPath, playerName);
            $.writeln("Found " + playerPngs.length + " matching PNG files");

            if (playerPngs.length === 0) {
                var warningMsg = "Warning: No matching PNG found for " + playerName;
                $.writeln(warningMsg);
                errorMessages.push(warningMsg);
                continue;
            }

            for (var j = 0; j < playerPngs.length; j++) {
                var pngFile = playerPngs[j];

                // Open SVG file
                var doc = app.open(svgFile);

                // Place PNG image
                var placedImage = doc.placedItems.add();
                placedImage.file = new File(pngFile);

                // Align the placed image with the artboard
                placedImage.width = doc.width;
                placedImage.height = doc.height;
                placedImage.position = [0, doc.height];

                // Export to PDF
                var pdfFileName = getPdfFileName(pngFile);
                var pdfFile = new File(outputFolderPath + "/" + pdfFileName);
                var pdfSaveOpts = new PDFSaveOptions();
                pdfSaveOpts.preserveEditability = true;
                doc.saveAs(pdfFile, pdfSaveOpts);

                // Close the document
                doc.close(SaveOptions.DONOTSAVECHANGES);
            }
        } catch (e) {
            var errorMsg = "Error processing " + playerName + ": " + e.message;
            $.writeln(errorMsg);
            $.writeln("Error stack: " + e.stack);
            errorMessages.push(errorMsg);
        }
    }

    if (errorMessages.length > 0) {
        alert("The following errors occurred:\n\n" + errorMessages.join("\n"));
    }
}

function findPlayerPngs(pngFolderPath, playerName) {
    var allPngFiles = Folder(pngFolderPath).getFiles("*.png");
    var playerPngs = [];
    
    // Remove "text layer-" prefix and file extension from SVG name
    var svgPlayerName = playerName.replace("text layer-", "").replace(".svg", "");
    
    // Split the SVG player name into parts
    var svgNameParts = svgPlayerName.split("-");
    
    for (var i = 0; i < allPngFiles.length; i++) {
        var file = allPngFiles[i];
        var fileName = decodeURI(file.name);
        
        // Remove file extension from PNG name
        var pngPlayerName = fileName.replace(".png", "");
        
        // Check if all parts of the SVG name are in the PNG name
        var allPartsMatch = true;
        for (var j = 0; j < svgNameParts.length; j++) {
            if (pngPlayerName.toLowerCase().indexOf(svgNameParts[j].toLowerCase()) === -1) {
                allPartsMatch = false;
                break;
            }
        }
        
        if (allPartsMatch) {
            playerPngs.push(file);
        }
    }
    
    return playerPngs;
}

function getPdfFileName(pngFile) {
    var pngFileName = decodeURI(pngFile.name);
    if (pngFileName.indexOf("-pose-print.png") !== -1) {
        return pngFileName.replace("-pose-print.png", "-pose-print-with-text-layer.pdf");
    } else {
        return pngFileName.replace(".png", "-with-text-layer.pdf");
    }
}

try {
    // Prompt user for folder paths
    var svgFolderPath = promptForFolder("Select the folder containing SVG files");
    var pngFolderPath = promptForFolder("Select the folder containing PNG files");
    var outputFolderPath = promptForFolder("Select the output folder for combined PDF files");

    if (svgFolderPath && pngFolderPath && outputFolderPath) {
        combineImages(svgFolderPath, pngFolderPath, outputFolderPath);
        alert("Process completed. Please check the output folder for results and review any error messages.");
    } else {
        alert("Process cancelled. Please make sure to select all required folders.");
    }
} catch (e) {
    alert("An error occurred: " + e.message);
    $.writeln("Error: " + e.message);
    $.writeln("Error stack: " + e.stack);
}
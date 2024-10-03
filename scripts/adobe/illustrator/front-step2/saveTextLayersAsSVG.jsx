/*
  Adobe Illustrator Script: Export Text Layers as SVG
  This script exports text layers for AthletiFi Digital Player Cards, including player number.
  It handles both single PlayerNumber and dual PlayerNumberA/B scenarios.
  Each SVG file is named based on the player's first name, last name, and number.
  The script exports to SVG, ensuring text appears consistently in all environments.
  The exported SVGs will have the same dimensions as the single artboard in the Illustrator file.
  All types of images and linked files are removed before export.
  The original Illustrator document remains unmodified as the script does not save any changes.
*/

#target illustrator

function exportDatasetsAsSVG() {
    var doc = app.activeDocument;
    var dataSets = doc.dataSets;
    var vars = doc.variables;

    // Prompt user for save location
    var folderPath = Folder.selectDialog("Choose a folder to save the SVG files");
    if (folderPath == null) return; // Exit if user cancels folder selection

    // Function to get the content of a global variable by name
    function getGlobalVariableContent(varName) {
        for (var i = 0; i < vars.length; i++) {
            if (vars[i].name === varName) {
                return (vars[i].pageItems.length > 0) ? vars[i].pageItems[0].contents : "Not linked";
            }
        }
        return null; // Return null if variable not found
    }

    // Function to remove all types of images and linked files
    function removeAllImages() {
        // Remove placed items (linked images)
        for (var i = doc.placedItems.length - 1; i >= 0; i--) {
            doc.placedItems[i].remove();
        }
        
        // Remove raster items
        for (var i = doc.rasterItems.length - 1; i >= 0; i--) {
            doc.rasterItems[i].remove();
        }
        
        // Remove image variables
        for (var i = vars.length - 1; i >= 0; i--) {
            if (vars[i].kind === VariableKind.IMAGE) {
                vars[i].remove();
            }
        }
        
        // Remove any remaining linked files
        if (doc.links && typeof doc.links.length !== 'undefined') {
            for (var i = doc.links.length - 1; i >= 0; i--) {
                try {
                    doc.links[i].remove();
                } catch(e) {
                    // If removal fails, just log it and continue
                    $.writeln("Failed to remove link: " + e);
                }
            }
        }
    }

    // Iterate through each dataset
    for (var i = 0; i < dataSets.length; i++) {
        dataSets[i].display();

        // Retrieve contents of the global variables
        var playerFirstName = getGlobalVariableContent("PlayerFirstName");
        var playerLastName = getGlobalVariableContent("PlayerLastName");
        
        // Check for PlayerNumber or PlayerNumberA
        var playerNumber = getGlobalVariableContent("PlayerNumber");
        if (playerNumber === null) {
            playerNumber = getGlobalVariableContent("PlayerNumberA");
        }

        // If no player number found, use a placeholder
        if (playerNumber === null) {
            playerNumber = "NoNumber";
        }

        // Construct the file name for the SVG export
        var filename = "text layer-" + playerFirstName + "-" + playerLastName + "-" + playerNumber + ".svg";
        var file = new File(folderPath + "/" + filename);

        // Remove all types of images and linked files
        removeAllImages();

        // Define SVG export options
        var exportOptions = new ExportOptionsSVG();
        exportOptions.cssProperties = SVGCSSPropertyLocation.STYLEATTRIBUTES;
        exportOptions.fontType = SVGFontType.OUTLINEFONT;
        exportOptions.coordinatePrecision = 3;
        exportOptions.documentEncoding = SVGDocumentEncoding.UTF8;
        exportOptions.svgMinify = true;
        exportOptions.svgId = SVGIdType.SVGIDUNIQUE;
        exportOptions.artboardRange = "1"; // Assuming there is only one artboard

        // Export to SVG
        doc.exportFile(file, ExportType.SVG, exportOptions);
    }

    alert("SVG export complete. Files saved to: " + folderPath);
}

exportDatasetsAsSVG(); // Run the function to start the export process
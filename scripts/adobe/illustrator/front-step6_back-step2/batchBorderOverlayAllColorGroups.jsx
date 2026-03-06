#target illustrator

// Batch Border Overlay - runs all 6 border colors in one go

var BASE = "/Users/qisforq/Code/athletifi-code/card-factory";
var BORDER_DIR = BASE + "/assets/borders/global_united_fc/print_borders";
var STEP5 = BASE + "/working/step5-output";
var OUTPUT = BASE + "/working/step6-output";

var runs = [
    { color: "blue",   border: "global_united_fc-print_vector_border_blue.pdf" },
    { color: "gold",   border: "global_united_fc-print_vector_border_gold.pdf" },
    { color: "black",  border: "global_united_fc-print_vector_border_black.pdf" },
    { color: "red",    border: "global_united_fc-print_vector_border_red.pdf" },
    { color: "bronze", border: "global_united_fc-print_vector_border_bronze.pdf" },
    { color: "silver", border: "global_united_fc-print_vector_border_silver.pdf" }
];

function combineBorderWithBackground(backgroundFile, borderFile, outputFolder, xOffset, yOffset) {
    var backgroundDoc = app.open(backgroundFile);
    
    // Get artboard bounds [left, top, right, bottom]
    var artRect = backgroundDoc.artboards[0].artboardRect;
    var artWidth = artRect[2] - artRect[0];
    var artHeight = artRect[1] - artRect[3];
    
    var borderItem = backgroundDoc.placedItems.add();
    borderItem.file = borderFile;
    
    // Size to artboard
    borderItem.width = artWidth;
    borderItem.height = artHeight;
    
    // Position at artboard origin (top-left)
    borderItem.position = [artRect[0] + xOffset, artRect[1] - yOffset];
    
    borderItem.move(backgroundDoc, ElementPlacement.PLACEATBEGINNING);
    
    var outputFile = new File(outputFolder + "/" + backgroundFile.name);
    var saveOptions = new PDFSaveOptions();
    saveOptions.compatibility = PDFCompatibility.ACROBAT5;
    saveOptions.generateThumbnails = true;
    saveOptions.preserveEditability = true;
    
    backgroundDoc.saveAs(outputFile, saveOptions);
    backgroundDoc.close(SaveOptions.DONOTSAVECHANGES);
}

// Prompt for offset once
var xOffset = 0;
var yOffset = 0;
var setCustom = confirm("Set a custom border offset?\n\nClick OK to enter values, or Cancel to use default (0,0).");
if (setCustom) {
    var xInput = prompt("Enter X offset (positive = right):", "0");
    var yInput = prompt("Enter Y offset (positive = down):", "0");
    if (xInput !== null) xOffset = parseFloat(xInput) || 0;
    if (yInput !== null) yOffset = parseFloat(yInput) || 0;
}

// Process first file and check
alert("Using offset: X=" + xOffset + ", Y=" + yOffset + "\n\nThe first file will be processed. Check the output, then confirm to continue with the rest.");

var totalProcessed = 0;
var totalErrors = 0;

for (var r = 0; r < runs.length; r++) {
    var run = runs[r];
    var cardFolder = new Folder(STEP5 + "/" + run.color);
    var borderFile = new File(BORDER_DIR + "/" + run.border);
    var outputFolder = new Folder(OUTPUT);
    
    if (!cardFolder.exists) {
        $.writeln("Card folder not found: " + cardFolder.fsName);
        continue;
    }
    if (!borderFile.exists) {
        $.writeln("Border file not found: " + borderFile.fsName);
        continue;
    }
    
    var backgroundFiles = cardFolder.getFiles("*.pdf");
    $.writeln("=== " + run.color + ": " + backgroundFiles.length + " files ===");
    
    for (var i = 0; i < backgroundFiles.length; i++) {
        try {
            combineBorderWithBackground(backgroundFiles[i], borderFile, outputFolder, xOffset, yOffset);
            totalProcessed++;
            
            if (r === 0 && i === 0) {
                var proceed = confirm("First file processed: " + backgroundFiles[i].name + "\n\nCheck the output in:\n" + OUTPUT + "\n\nClick OK to continue with all remaining files, or Cancel to stop and adjust offset.");
                if (!proceed) {
                    alert("Stopped after 1 file. You can re-run with a different offset.");
                    totalProcessed = -1;
                    break;
                }
            }
        } catch (e) {
            $.writeln("Error: " + backgroundFiles[i].name + " - " + e);
            totalErrors++;
        }
        $.sleep(100);
    }
    if (totalProcessed === -1) break;
}

if (totalProcessed > 0) alert(
    "Batch Border Overlay Complete!\n\n" +
    "Successfully processed: " + totalProcessed + "\n" +
    "Errors: " + totalErrors
);

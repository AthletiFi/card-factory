#target photoshop

var inputFolder = Folder.selectDialog("Select the folder with PDFs to convert");
var outputFolder = Folder.selectDialog("Select the folder to save PNGs");

if (inputFolder != null && outputFolder != null) {
    var fileList = inputFolder.getFiles("*.pdf");

    for (var i = 0; i < fileList.length; i++) {
        var doc = open(fileList[i]);

        var pngOptions = new PNGSaveOptions();
        pngOptions.compression = 9; // Set to maximum compression level while maintaining lossless quality

        var outputFile = new File(outputFolder + "/" + fileList[i].name.replace(/\.pdf$/i, ".png"));
        doc.saveAs(outputFile, pngOptions, true, Extension.LOWERCASE);

        doc.close(SaveOptions.DONOTSAVECHANGES);
    }

    alert("Conversion complete!");
} else {
    alert("Operation cancelled.");
}

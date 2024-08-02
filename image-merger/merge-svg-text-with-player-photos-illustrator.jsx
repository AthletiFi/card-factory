#target illustrator

function combineImages(svgFolderPath, pngFolderPath, outputFolderPath) {
  var svgFiles = Folder(svgFolderPath).getFiles("*.svg");

  for (var i = 0; i < svgFiles.length; i++) {
      var svgFile = svgFiles[i];
      var playerName = decodeURI(svgFile.name).replace("text layer-", "").replace(".svg", "").replace(/-/g, ' ');

      // Check if the player is David Calderon or Nacho Aliaga
      if (playerName !== "David Calderon" && playerName !== "Nacho Aliaga") {
          continue; // Skip this file if it's not for one of the specified players
      }

      var playerPngs = findPlayerPngs(pngFolderPath, playerName);

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
  }
}

function findPlayerPngs(pngFolderPath, playerName) {
    var allPngFiles = Folder(pngFolderPath).getFiles("*.png");
    var playerPngs = [];
    for (var i = 0; i < allPngFiles.length; i++) {
        var file = allPngFiles[i];
        var fileName = decodeURI(file.name); // Decode the URI to handle spaces

        // Create a regex pattern that matches the player name
        var regexSafePlayerName = playerName.replace(/\s+/g, '\\s+');
        var regexPattern = regexSafePlayerName + "-\\d+-.*-pose-print\\.png";
        var regex = new RegExp(regexPattern);

        // alert("Regex pattern: " + regexPattern); // Debugging

        if (regex.test(fileName)) {
            playerPngs.push(file);
        }
    }
    return playerPngs;
}

function getPdfFileName(pngFile) {
    return decodeURI(pngFile.name).replace("-pose-print.png", "-pose-print-with-text-layer.pdf");
}

// Set your folder paths here
var svgFolderPath = "/Volumes/OWC Envoy Pro Elektron/AthletiFi/Print Cards/Print components - NEW PDFs/Stage 1 - Combine Components/v2 Bronze/Text Layers SVG";
var pngFolderPath = "/Volumes/OWC Envoy Pro Elektron/AthletiFi/Print Cards/Print components - NEW PDFs/Stage 1 - Combine Components/v2 Bronze/v2 Bronze Players";
var outputFolderPath = "/Volumes/OWC Envoy Pro Elektron/AthletiFi/Print Cards/Print components - NEW PDFs/Stage 1 - Combine Components/v2 Bronze/v2 Bronze Players w text";

combineImages(svgFolderPath, pngFolderPath, outputFolderPath);

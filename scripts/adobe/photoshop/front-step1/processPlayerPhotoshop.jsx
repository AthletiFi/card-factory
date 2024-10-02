#target photoshop

// Define the canvas dimensions
var canvasWidth = 3150;
var canvasHeight = 4350;

// Define the safe box dimensions
var safeTop = 940;
var safeBottom = 3140;
var safeLeft = 540;
var safeRight = 2610;

// Calculate safe box width and height
var safeWidth = safeRight - safeLeft;
var safeHeight = safeBottom - safeTop;

function processCurrentDocument() {
    var doc = app.activeDocument;
    
    // Trim transparent pixels
    doc.trim(TrimType.TRANSPARENT);
    
    // Resize canvas to specified dimensions
    doc.resizeCanvas(canvasWidth, canvasHeight, AnchorPosition.MIDDLECENTER);
    
    var layer = doc.activeLayer;
    
    // Calculate scale factor to fit within safe box
    var currentWidth = layer.bounds[2].value - layer.bounds[0].value;
    var currentHeight = layer.bounds[3].value - layer.bounds[1].value;
    var widthRatio = safeWidth / currentWidth;
    var heightRatio = safeHeight / currentHeight;
    var scaleFactor = Math.min(widthRatio, heightRatio);
    
    // Resize the layer to fit within safe box
    layer.resize(scaleFactor * 100, scaleFactor * 100, AnchorPosition.MIDDLECENTER);
    
    // Calculate the center of the safe box
    var safeCenterX = safeLeft + safeWidth / 2;
    var safeCenterY = safeTop + safeHeight / 2;
    
    // Move the layer to center it within the safe box
    var layerCenterX = (layer.bounds[0].value + layer.bounds[2].value) / 2;
    var layerCenterY = (layer.bounds[1].value + layer.bounds[3].value) / 2;
    layer.translate(safeCenterX - layerCenterX, safeCenterY - layerCenterY);
    
    // Convert to Smart Object
    executeAction(stringIDToTypeID("newPlacedLayer"), undefined, DialogModes.NO);
    
    // Apply Layer Styles (Drop Shadow)
    var idsetd = charIDToTypeID( "setd" );
    var desc3 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
        var ref1 = new ActionReference();
        var idPrpr = charIDToTypeID( "Prpr" );
        var idLefx = charIDToTypeID( "Lefx" );
        ref1.putProperty( idPrpr, idLefx );
        var idLyr = charIDToTypeID( "Lyr " );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idTrgt = charIDToTypeID( "Trgt" );
        ref1.putEnumerated( idLyr, idOrdn, idTrgt );
    desc3.putReference( idnull, ref1 );
    var idT = charIDToTypeID( "T   " );
        var desc4 = new ActionDescriptor();
        var idScl = charIDToTypeID( "Scl " );
        var idPrc = charIDToTypeID( "#Prc" );
        desc4.putUnitDouble( idScl, idPrc, 416.700000 );
        var idDrSh = charIDToTypeID( "DrSh" );
            var desc5 = new ActionDescriptor();
            var idenab = charIDToTypeID( "enab" );
            desc5.putBoolean( idenab, true );
            var idMd = charIDToTypeID( "Md  " );
            var idBlnM = charIDToTypeID( "BlnM" );
            var idNrml = charIDToTypeID( "Nrml" );
            desc5.putEnumerated( idMd, idBlnM, idNrml );
            var idClr = charIDToTypeID( "Clr " );
                var desc6 = new ActionDescriptor();
                var idRd = charIDToTypeID( "Rd  " );
                desc6.putDouble( idRd, 0.000000 );
                var idGrn = charIDToTypeID( "Grn " );
                desc6.putDouble( idGrn, 0.000000 );
                var idBl = charIDToTypeID( "Bl  " );
                desc6.putDouble( idBl, 0.000000 );
            var idRGBC = charIDToTypeID( "RGBC" );
            desc5.putObject( idClr, idRGBC, desc6 );
            var idOpct = charIDToTypeID( "Opct" );
            var idPrc = charIDToTypeID( "#Prc" );
            desc5.putUnitDouble( idOpct, idPrc, 45.000000 );
            var iduglg = charIDToTypeID( "uglg" );
            desc5.putBoolean( iduglg, true );
            var idlagl = charIDToTypeID( "lagl" );
            var idAng = charIDToTypeID( "#Ang" );
            desc5.putUnitDouble( idlagl, idAng, 90.000000 );
            var idDstn = charIDToTypeID( "Dstn" );
            var idPxl = charIDToTypeID( "#Pxl" );
            desc5.putUnitDouble( idDstn, idPxl, 4.000000 );
            var idCkmt = charIDToTypeID( "Ckmt" );
            var idPxl = charIDToTypeID( "#Pxl" );
            desc5.putUnitDouble( idCkmt, idPxl, 20.000000 );
            var idblur = charIDToTypeID( "blur" );
            var idPxl = charIDToTypeID( "#Pxl" );
            desc5.putUnitDouble( idblur, idPxl, 120.000000 );
            var idNose = charIDToTypeID( "Nose" );
            var idPrc = charIDToTypeID( "#Prc" );
            desc5.putUnitDouble( idNose, idPrc, 0.000000 );
            var idAntA = charIDToTypeID( "AntA" );
            desc5.putBoolean( idAntA, false );
            var idTrnS = charIDToTypeID( "TrnS" );
                var desc7 = new ActionDescriptor();
                var idNm = charIDToTypeID( "Nm  " );
                desc7.putString( idNm, "Linear" );
            var idShpC = charIDToTypeID( "ShpC" );
            desc5.putObject( idTrnS, idShpC, desc7 );
            var idlayerConceals = stringIDToTypeID( "layerConceals" );
            desc5.putBoolean( idlayerConceals, true );
        var idDrSh = charIDToTypeID( "DrSh" );
        desc4.putObject( idDrSh, idDrSh, desc5 );
    var idLefx = charIDToTypeID( "Lefx" );
    desc3.putObject( idT, idLefx, desc4 );
    executeAction( idsetd, desc3, DialogModes.NO );
}

// Process the currently open document
processCurrentDocument();
# Front Card Generation Process

The front card generation process for AthletiFi player cards involves a series of precise steps, from photo processing to final output. This guide details each stage, ensuring consistent, high-quality card production for both digital and print formats.

## 1. Process Player Photos

### 1.1 Prepare Photos

- Cut out the players so they are against a transparent background.
- Ensure all player photos are saved as PNGs and named using the convention `<First Name>-<Last Name>-<JerseyNumber>`.

> [!NOTE]  
> Pay attention to players who have double first names or double last names (e.g., Anderson Rodriguez Dinarte has the first name Anderson, but Daisy Grace Kerrigan has the first name Daisy Grace).

### 1.2 Set Up Photoshop

- Add needed scripts and actions:
  - If it is not already in the scripts menu, load the [processPlayerPhotoshop.jsx](../scripts/adobe/photoshop/front-step1/processPlayerPhotoshop.jsx) script into Photoshop by adding it into `/Applications/Adobe Photoshop 2024/Presets/Scripts/`. You can find this script in the `scripts/adobe/photoshop/front-step1/` directory of the project.
  - If it is not already in your actions panel, load the needed action from the [Step1-ProcessPlayerPhotos.atn](../assets/actions/photoshop/front-step1/Step1-ProcessPlayerPhotos.atn) action set. To load the action:
    1. Open the Actions panel in Photoshop ('Window' > 'Actions').
    2. Click the menu icon in the top right corner of the Actions panel.
    3. Select "Load Actions".
    4. Navigate to the `assets/actions/photoshop/front-step1/` directory and select `Step1-ProcessPlayerPhotos.atn`.

### 1.3 Batch Process Photos

1. Go to 'File' > 'Automate' > 'Batch'.
2. Choose the folder with player photos as the source.
3. Set Destination to a new folder of your choosing.
4. Choose 'TouchUpAndResizePlayers' action in the `Step1-ProcessPlayerPhotos` set, which does the following:
   - Sets Auto Levels
   - Sets Auto Tone
   - Sets Auto Contrast
   - Sets Auto Curves
   - Applies Camera Raw Filter:
     - Texture: 20
     - Clarity: 10
   - Applies the `ProcessPlayerPhotoshop.jsx` script, which does the following:
     - Convert layer to smart object ('Layer' > 'Smart Objects' > 'Convert to Smart Object')
     - Set layer style and add drop shadow:
       - Opacity 65%
       - distance 4 px
       - Spread 20%
       - Size 78 px
     - Make the canvas size Width 3150 x Height 4350
     - Set guides to frame the safe box for players on the canvas:
       - Top: Y: 940px (e.g. 940 pixels down starting from the top)
       - Bottom: Y: 3140px (e.g. 3140 pixels from the top)
       - Left: X: 540px (e.g. 540 pixels from the left)
       - Right: X: 2610px (e.g. 2,610 pixels from the left)
     - Resize player to fit in safe box
     - Merge with a new empty layer to flatten, then save as PNG
5. Run the batch process.

### 1.4 Alternative Manual Process

If 'TouchUpAndResizePlayers' action is unavailable:

1. Manually apply the auto levels and Camera Raw filter settings as described in [step 1.3](#13-batch-process-photos).
2. Run the [batchProcessPlayersPhotoshop.jsx](../scripts/adobe/photoshop/front-step1/batchProcessPlayersPhotoshop.jsx) script:
   - Go to 'File' > 'Scripts' > 'Browse' and navigate to the script location.
   - When prompted, select the folder containing your player photos.
The script will automatically process each image using the same settings as `ProcessPlayerPhotoshop.jsx` and output it with the prefix 'Resized_'.

## 2. Create Text Layers

### 2.1 Prepare Player Data

1. Create a CSV with a list of all of the players who you are generating card artwork for with the headers `PlayerFirstName,PlayerLastName,PlayerNumber`.
2. If you're doing the 3D effect for the player number, make the CSV with these headers: `PlayerFirstName,PlayerLastName,PlayerNumberA,PlayerNumberB` (both player numbers should have the same value).

### 2.2 Set Up Illustrator Template

1. Decide if you want to create a new Text Layers Template AI file or use existing ones. The following variations currently exist in the `assets/templates/front-step2/` directory:
   - [Text Layers Template-For Double Digits and long last names.ai](../assets/templates/front-step2/Text%20Layers%20Template-For%20Double%20Digits%20and%20long%20last%20names.ai)
   - [Text Layers Template-For Double Digits.ai](../assets/templates/front-step2/Text%20Layers%20Template-For%20Double%20Digits.ai)
   - [Text Layers Template-For Single Digits and long last names.ai](../assets/templates/front-step2/Text%20Layers%20Template-For%20Single%20Digits%20and%20long%20last%20names.ai)
   - [Text Layers Template-For Single Digits.ai](../assets/templates/front-step2/Text%20Layers%20Template-For%20Single%20Digits.ai)
2. If using an existing file, wipe the old variable data first:
   - Open the chosen "Text Layers Template" file in Illustrator.
   - Open 'Window' > 'Variables' to open the Variables panel.
   - If you see existing variables and datasets, remove the old data:
     - Click on the menu hamburger icon (three horizontal lines) in the Variables panel.
     - Select "Delete Data Set" for each existing dataset:
       - Use "Next Data Set" to cycle through all datasets.
       - For each dataset, select "Delete Data Set" from the menu.
       - Repeat until all old datasets are removed.
     - Delete the variable definitions as well, by selecting each variable and click the "Delete Variable" button (trash can icon) at the bottom of the panel.

### 2.3 Create Dynamic Text Boxes (for new templates)

1. Create a new illustrator file that are at the same dimensions as the card artwork:
   - Width: 2.5867 in
   - Height: 3.6214 in

2. Create text boxes for the dynamic content:
   - Select the Type Tool (T)
   - Click and drag on the artboard to create a text box for the player's first name
   - Type a placeholder text like "First Name"
   - Repeat this process to create separate text boxes for:
     - Last Name
     - Player Number (create this twice for the 3D effect)

### 2.4 Import CSV Data

1. In the Variables panel, click the menu icon (three horizontal lines)
2. Select "Import"
3. Navigate to your CSV file and select it
4. In the Import Options dialog:
   - Check "Use first row for Variable Names"
   - Ensure "Comma" is selected as the delimiter
   - Click OK

### 2.5 Link Text Boxes to Variables

1. For each text box you want to update dynamically:
   - Select the text box

> [!TIP]  
> :memo: **Pro tip 1**: If it is difficult to select the text box because it is behind another element, open the layers window and click on the circle to the right of the layer name, and that will select it.
> [!TIP]  
> :memo: **Pro tip 2**: Name all of the layers by the property of the text they are supposed to represent (e.g. PlayerNumberA)

   - In the Variables panel, find the variable that is supposed to link to this textbox (e.g. PlayerFirstName)
   - In the Variables panel, click the menu hamburger icon (three horizontal lines) and then click the "Make Text Dynamic" button. You should now See the Objects column list the name of the layer for that text box
   - Name the variable to match your CSV headers:
     - For first name: Variable is "PlayerFirstName" and Object is also "PlayerFirstName"
     - For last name: Variable is "PlayerLastName" and Object is also "PlayerLastName"
     - For player number, you have to make two variables. "PlayerNumberA" for one and "PlayerNumberB" for the other
2. Verify your setup. In the Variables panel, use the "Previous Data Set" and "Next Data Set" options to cycle through your data.

### 2.6 Generate SVG Files

1. Run the [saveTextLayersAsSVG](../scripts/adobe/illustrator/front-step2/saveTextLayersAsSVG.jsx) script:
   - Go to 'File' > 'Scripts' > 'Other Script…'
   - Navigate to the `scripts/adobe/illustrator/front-step2/` directory and select `saveTextLayersAsSVG.jsx`.
2. When prompted, choose a destination to save the SVG files.
3. Repeat as necessary if you have single digits, double digits, long last names, etc (there are different text layer template files for each of these).

## 3. Merge Text Layers with Player Photos

### 3.1 Prepare Files

1. Ensure all player photos are in PNG format.
2. In order for the merge script to work, the PNGs and text layers must follow a precise naming structure. The text layers will already be in the correct structure if you ran  [saveTextLayersAsSVG](../scripts/adobe/illustrator/front-step2/saveTextLayersAsSVG.jsx). Please ensure to name the PNG files consistently, following one of these patterns: 
   - `[PlayerFirstName] [PlayerLastName]-[Number]-[running,shooting or standing]-pose-print.png`
   - `[PlayerFirstName] [PlayerLastName]-[Number].png`
3. Place all player photo PNGs in a single folder.
4. Ensure you have a folder containing all the SVG files from the [Create Text Layers](#2-create-text-layers) step.

### 3.2 Run Merge Script

1. Open Adobe Illustrator and go to 'File' > 'Scripts' > 'Other Script…' and select the [mergeSvgTextWithPlayerPhotos.jsx](../scripts/adobe/illustrator/front-step3/mergeSvgTextWithPlayerPhotos.jsx) script.
2. When prompted, select the folder with SVG files, the folder with PNG files and the output folder for combined PDF files. The script will run automatically, combining each SVG file with its corresponding PNG file(s) and saving the result as a PDF in the output folder.

### 3.3 Review Output

- Review a few of the generated PDFs to make sure the text layers are correctly positioned over the player photos.

> [!IMPORTANT]  
> The script matches SVG files to PNG files based on the player's name, so ensure your file naming is consistent.

## 4. Prepare Backgrounds

### 4.1 Create Blank PDF Template

For your convenience, there is already a [blank.pdf](../assets/templates/front-step4/blank.pdf) in the `assets/templates/front-step4/` directory. However, if you need to recreate it, follow these instructions:

1. Use a PDF creation tool (e.g., Adobe Illustrator, InDesign, or online tools) to create a blank PDF with the following dimensions:
   - Width: 3.875 inches (2300 pixels at 800 DPI)
   - Height: 2.875 inches (3100 pixels at 800 DPI)
2. Make sure the PDF is transparent
3. Save this as [blank.pdf](../assets/templates/front-step4/blank.pdf) in the `assets/templates/front-step4/` directory.

### 4.2 Prepare Background PNG Files

1. Ensure your background designs are saved as high-resolution PNG files with transparency where needed.
2. Place these PNG files in the `assets/backgrounds/png/front-step4/` directory.
3. Make sure the PNG files have descriptive names (e.g., "Bronze v2 - Dark Blue.png", "Silver v2 - Space.png").

### 4.3 Combine Blank PDF with Background PNGs

1. Run the [png_to_pdf.py](../scripts/python/front-step4/png-to-pdf.py) script:
   - Navigate to the `scripts/python/front-step4/` directory in a terminal or command prompt.
   - Run the following command:

   ```shell
   python3 png_to_pdf.py
   ```

2. When prompted, provide:
   - The path to the `assets/backgrounds/png/front-step4/` directory containing your PNG background files.
   - The path where you want the resulting PDF files to be saved (e.g., `assets/backgrounds/pdf/bronze/front-step4/` or `assets/backgrounds/pdf/silver/front-step4/`).
   - The path to your "blank.pdf" file in the `assets/templates/front-step4/` directory.
The script will process each PNG file, creating a corresponding PDF with the correct dimensions and preserving transparency.

3. Verify results to ensure the dimensions are correct (3.875 x 2.875 inches) and the background is correctly positioned.

> [!IMPORTANT]  
> The script matches SVG files to PNG files based on the player's name, so ensure your file naming is consistent.

## 5. Combine Background and Player Components

This step involves combining the background layer with the player photo + text layer. The border layer can normally be combined in this step as well, but PyMuPDF (the library used for PDF processing in [merge-images-pdf.py](../scripts/python/front-step5_back-step1/merge-images-pdf.py)) is unable to handle gradients properly. Therefore, we will add the border in a subsequent step.

### 5.1 Organize Components

1. Organize your components into separate folders:
   - Background PDF files (in PDF format) - prepared in [step 4](#4-prepare-backgrounds)
   - Player photos with text layers (in PDF format) - prepared in [step 3](#3-merge-text-layers-with-player-photos)
2. If you have multiple editions (e.g., Silver and Bronze), organize these components into separate subfolders for each edition.

### 5.2 Generate Combinations

1. Run the `merge-images-pdf.py` script:
   - Navigate to the `scripts/python/front-step5_back-step1/` directory in your terminal or command prompt.
   - Run the following command:

   ```shell
   python3 merge-images-pdf.py
   ```

2. When prompted, provide the following information:
   - Number of layers: 2
   - Output directory: path to your desired output folder for digital cards
   - Layer 1 path: path to the directory containing background PDFs
   - Layer 2 path: path to the directory containing player photos with text PDFs

3. When prompted, choose the 'COMBINE' option

### 5.3 Rename Files

1. In the same `scripts/python/front-step5_back-step1/` directory, run the `rename_files.py` script:

   ```shell
   python3 rename_files.py
   ```

2. Choose the option `Rename newly generated files to the standard naming convention`
3. Enter the path to the folder with the PDFs you just generated

> [!NOTE]  
> This script is capable of handling nested folders while keeping track of the sequencing, so if you have the cards split between editions in separate folders (e.g. a folder for Bronze and a folder for Silver), you do not need to combine them for this step. The script will rename all the files accordingly.

The script will automatically detect and handle the following file naming conventions:

- Cards with CMYK Color Profile specified:
  - Input: `<Edition> v2 - <Theme>CMYK<FirstName>-<LastName>-<PlayerNumber>-with-text-layer_CMYK_<edition> vector border with bleed_<serialNumber>.pdf`
  - Output: `<FirstName>-<LastName>-<PlayerNumber>-<Edition>-<Theme>_print-<serialNumberByPlayer>.pdf`
- Cards with RGB Profile specified:
  - Input: `<Edition> v2 - <Theme><FirstName>-<LastName>-<PlayerNumber>-with-text-layer_digital vector border <edition><serialNumber>_RGB.pdf`
  - Output: `<FirstName>-<LastName>-<PlayerNumber>-<Edition>-<Theme>_digital-<serialNumberByPlayer>.pdf`
- Cards from the previous process (VSA-23):
  - Input: `<Edition> - <BackgroundName>_<PlayerName>-<PoseNumber>-<PoseType>-pose-print-with-text-layer_NEW <BorderStyle>vector border <edition><EditionSerialNumber>.pdf`
  - Output: `<PlayerName><SerialID><PoseType>_<Edition>_front.pdf`
- Simplified Bronze/Silver format:
  - Input: `<Edition> v2 - <Theme>_<PlayerName>-<PlayerNumber>-with-text-layer_<serialNumber>.pdf`
  - Output: `<PlayerName>-<PlayerNumber>-<Edition>-<Theme>-<serialNumberByPlayer>.pdf`

## 6. Add Border for Digital and Print Versions

Now that we have the Player Photo combined with the Background image, all that is left to do is add the border. We'll use an Illustrator script to automate this process for both digital and print versions.

### 6.1 Prepare Files

1. Ensure all combined player/background PDFs from Step 5 are in a single folder. If you have different editions (e.g. Bronze and Silver) you will have to run this script separately for each edition.
2. Locate the appropriate border files for your club. These are found in:
   `assets/borders/<club_name>/`
   Where `<club_name>` is the name of the club you're generating cards for (e.g., 'athletifi_select' or 'coventry_sa').
3. Ensure you have the correct border files for both digital and print versions, and for the different editions (e.g. Bronze and Silver).
4. If the border files for your club do not exist, follow these steps to create them:
   a. First, create a new folder for the club in the [borders directory](../assets/borders), and add folders for `digital_borders`, `print_borders`, and for the `back_border` (this will be used later in [step 2 of the back card generation process](./back-card-generation.md#2-render-borders-blue-and-add-to-cards)):

      ```plaintext
      assets/borders/<club_name>/
                              ├── back_border/
                              ├── digital_borders/
                              └── print_borders/
      ```

   b. Choose an existing border file as a template (e.g., from [athletifi_select](../assets/borders/athletifi_select/) or [coventry_sa](../assets/borders/coventry_sa/)).
   c. Open the file in Adobe Illustrator.
   d. You'll notice two layers: 'Border' and 'Club Logo'.
   e. Find an existing vectorized version of the logo for the club you're generating cards for.
   f. Import this logo into the Illustrator file and place it in the 'Club Logo' layer.
   g. Adjust the size of the new logo to match the size of the previous club logo.
   h. Position the new logo to roughly match the position of the previous logo.
   i. Delete the previous club logo.
   j. Save this as a new PDF file following the naming convention:
      `<club_name>-<digital/print>_vector_border_<edition>.pdf`

   k. Save the digital version in the 'digital_borders' folder and the print version in the 'print_borders' folder.
   l. Repeat this process for both digital and print versions, and for each edition (bronze/silver).

### 6.2 Apply Borders

1. Open Adobe Illustrator and go to 'File' > 'Scripts' > 'Other Script…'
2. Navigate to the `scripts/adobe/illustrator/front-step6_back-step2/` directory and select [combinePlayerCardBorderWithBackgrounds.jsx](../scripts/adobe/illustrator/front-step6_back-step2/combinePlayerCardBorderWithBackgrounds.jsx).
3. When prompted by the script:
   - Select the folder containing your combined player/background PDFs from [step 5](#5-combine-background-and-player-components).
   - Choose the appropriate border PDF file (digital or print version) from the respective directory mentioned in [step 6.1](#61-prepare-files).
   - Select an output folder for the final combined PDFs.
   - When prompted to set a custom offset, start with the default (0,0) unless you notice alignment issues.
   - The script will then ask if you want to set a custom offset or use the default (0,0). Set an offset of your choosing or use the default.
   - When prompted to check the alignment of the border on the first file, ensure that the border was properly overlaid in the correct position. If it was, you can click yes to continue the batch. If it was not, click no so you can try a new offset.
   - Once you've confirmed the correct offset, the script will automatically process all remaining PDFs in the selected folder, adding the border to each one using the confirmed offset.
4. Repeat the process for both digital and print versions, for each edition (e.g. digital bronze border, digital silver border, print bronze border, print silver border)
5. Review a few of the generated PDFs to ensure the border is correctly applied. Verify that the dimensions are still correct (3.875 x 2.875 inches).

## 7. Add Trim Marks (Print Version Only)

For both the front and the backs, instead of printing at 2.5" x 3.5", which is standard trading card size, we will actually be printing at 2.625" x 3.625". This means that we need to add an additional bleed of 0.125" (1/8") to bring the total to 2.875" x 3.875". Since we have actually generated these player cards using the dimensions of 2.875" x 3.875" already, all we need to do is change the document setup so that the Artboard is now set to 2.625" x 3.625" with a bleed of 0.125".

In Illustrator the bleed is set by clicking on 'File' > 'Document Setup…' and setting a bleed on that menu, which will set on the outside of the artboard. So this means the artboard will still have to be changed from  2.875”x3.875” to 2.625”x3.625”. But we still need to extend the artwork to the edge of the bleed to ensure there is actually content in the bleed. We have created an Illustrator action to do this by creating a square at the correct dimensions for the artboard, then using “Insert Menu Item” to add the action “Fit to Selected Art”, using the align buttons to center the square vertically and horizontally, then deleting the square, and then finally saving the pdf with trim marks enabled.

### 7.1 Set Up Illustrator Action

1. Open Adobe Illustrator.
2. Open the Actions panel ('Window' > 'Actions').
3. Load the [AddTrimMarksToPrintCards.aia](../assets/actions/illustrator/front-step7_back-step7/AddTrimMarksToPrintCards.aia) action set:
   - Click the panel menu icon (four horizontal lines) in the Actions panel.
   - Choose "Load Actions".
   - Navigate to the `assets/actions/illustrator/front-step7_back-step7/` directory and select `AddTrimMarksToPrintCards.aia`.
4. Modify the action to re-record the "Save" and "Close" steps
   - Expand the "AddTrimMarksToPrintCards" action set in the Actions panel.
   - Select the "AddTrimMarksToPrintCards" action.
   - Delete the last two steps: "Save" and "Close" (select each step and click the trash icon at the bottom of the Actions panel).
   - Click the "Begin recording" button (circle icon) at the bottom of the Actions panel.
   - With the action selected, go to 'File' > 'Save As'.
   - In the Save As dialog:
     - Keep the filename the same.
     - Choose the [High Quality Print] preset.
     - Go to the 'Marks and Bleeds' section in the sidebar, then navigate to the Marks section and check 'Trim Marks'.
     - Still within 'Marks and Bleeds', navigate to 'Bleeds', and set the bleed on all four sides to '0.125 in'.
   - Click Save.
   - Go to 'File' > 'Close'.
   - Click the "Stop recording" button (square icon) at the bottom of the Actions panel.

> [!NOTE]  
> We must re-record these steps because when an action is played back, it uses the directory path from when the action was initially recorded. By re-recording this step, you ensure that the files will be saved in the correct location during batch processing.
> [!TIP]  
> If no other files are open in Illustrator, the actions window may disappear. Click ‘Window’ > ‘Actions’ in the menu to bring back the Actions window so you can click the stop button.

### 7.2 Run Batch Process

1. From the Actions panel menu, click "Batch...".
2. In the Batch dialog:
   - Set: "AddTrimMarksToPrintCards"
   - Action: "AddTrimMarksToPrintCards"
   - Source: Choose the folder with your print version PDFs from [step 6](#6-add-border-for-digital-and-print-versions).
   - Destination: Set to 'Save and Close'.
3. Click OK to start the batch process.
4. Once the batch finishes, check output to ensure trim marks are added correctly. Verify bleed is set to 0.125" on all sides.

> [!NOTE]  
> If the batch does not seem to be saving the files, it may be because it is trying to save the files in the original location that was chosen when the action was recorded, and overwriting the same file over and over. If that is the case, you must re-record the “Save As” segment of the action, setting the trim mark and setting the document bleed to 0.125”, and setting it to replace the original file.
> [!WARNING]  
> Monitor the first output closely. This action works by first creating a square in the correct dimensions (2.625” x 3.625”). If for some reason the action is not creating the square in these dimensions, it may be because “Maintain Width and Height Proportions” (the chainlink icon) is enabled. If that is the case, disable it and then try again.

## 8. Convert to PNG and WebP (Digital Version Only)

This step is necessary only for the digital versions of the cards, converting them first to PNG and then to WebP format for optimal web display and digital distribution.

### 8.1 Convert PDF to PNG

1. Open Adobe Photoshop and go to 'File' > 'Scripts' > 'Browse'.
2. Navigate to the `scripts/adobe/photoshop/front-step8/` directory and select [convertPDFtoPNG.jsx](../scripts/adobe/photoshop/front-step8/convertPDFtoPNG.jsx).
3. When prompted:
   - Select the folder containing your digital version PDFs from [step 6](#6-add-border-for-digital-and-print-versions).
   - Choose an output folder for the PNG files.
The script will process all PDFs, converting each to PNG. 

### 8.2 Crop and Convert to WebP

Before you begin, make sure you have ImageMagick and cwebp installed on your system. If not, install them using your system's package manager:

- On macOS with Homebrew: `brew install imagemagick webp`
- On Ubuntu or Debian: `sudo apt-get install imagemagick webp`

1. Open a terminal or command prompt and navigate to the `scripts/shell/front-step8/` directory.
2. Make the `crop_and_convert_to_webp.sh` script executable by running:

   ```shell
   chmod +x crop_and_convert_to_webp.sh
   ```

3. Run the script:

   ```shell
   ./crop_and_convert_to_webp.sh
   ```

4. When prompted:
   - Enter the path to the folder containing your PNG files (output from [step 8.1](#81-convert-pdf-to-png)).
   - Enter the path where you want to save the cropped and converted WebP files.
   - Enter the desired resize percentage:

> [!NOTE]  
> It is recommended to reduce the size of the player card to around 40-50% so that the final dimensions are not larger than ~2000px. Enter 100 if you do not wish to resize.

The script will process all PNG files, cropping out excess transparent space and converting them to WebP format.

### 8.3 Rename WebP Files

You must remove spaces from the WebP filenames so that they do not have spaces. This is needed so that the url will work when the files are loaded into s3. Otherwise s3 will replace spaces with `%20` and then the filenames will not match with the records we add into the database.

1. In the same `scripts/shell/front-step8/` directory, run the `[replace_spaces_with_hyphens.py](../scripts/python/) script:

   ```shell
   python3 replace_spaces_with_hyphens.py
   ```

2. When prompted, enter the path to the directory containing your WebP files.

The script will rename all WebP files, replacing spaces with hyphens. This is necessary for proper URL formatting when the files are loaded into S3.

This completes the generation process for the card fronts! Always review the output at each stage to ensure quality and consistency across all cards. When you are ready, proceed with [generating the card backs](back-card-generation.md).

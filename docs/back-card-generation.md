# Back Card Generation Process

This guide details the process for generating the back side of AthletiFi player cards. The process involves creating blank backgrounds, adding borders, generating QR codes, and finalizing the card design for both digital and print formats.

## 1. Make Player Photos Blank and Generate Background Combos

To ensure proper naming and correspondence with the front images, we'll regenerate the back cards using components named identically to those used in front card generation.

### 1.1 Prepare Background PDFs

1. Copy the Background PDFs you've already created for both Silver and Bronze into a new directory for the BACK cards.

### 1.2 Create Blank Versions of Player Photos/Text Layer PDFs

1. Run the [create_blank_pdf_copies.py](../scripts/python/back-step1/create_blank_pdf_copies.py) script:

   ```shell
   python3 create_blank_pdf_copies.py
   ```

2. When prompted:
   - Enter the path to the directory containing the original Player Photos/Text Layer PDFs (These were the PDFs created in "[step 3](./front-card-generation.md#3-merge-text-layers-with-player-photos)" in the front card generation instructions.)
   - Enter the path where you want to save the new blank PDFs (this should be within your BACK components directory)

> [!NOTE]  
> The script will automatically detect the dimensions of your PDFs and create blank copies with the same names as the originals.

### 1.3 Generate Background and Player Combinations

1. Run the [merge-images-pdf.py](../scripts/python/front-step5_back-step1/merge-images-pdf.py) script:

   ```shell
   python3 merge-images-pdf.py
   ```

2. When prompted, provide the following information:
   - Number of layers: 2
   - Output directory: path to your desired output folder for digital cards
   - Layer 1 path: path to the directory containing background PDFs
   - Layer 2 path: path to the directory containing blank player photos PDFs
4. Repeat this process for any additional editions in this collection (e.g. Bronze or Silver)

### 1.4 Rename Files

1. Run the [rename_files.py](../scripts/python/front-step5_back-step1/rename_files.py) script:

   ```shell
   python3 rename_files.py
   ```

2. Choose option 1: "Rename newly generated files to the standard naming convention"
3. Enter the path to the folder with the PDFs you just generated

> [!IMPORTANT]
> The `rename_files.py` script may not use the same sequencing the second time even if you pass in the same set of files, as the process is not deterministic. Therefore, for the BACK cards, you need to run `rename_files.py` a second time.

4. Run the `rename_files.py` script again, this time selecting option 2 for fixing the number sequence of generated player card BACKS which do not match the sequence of the initial generation for FRONTs. When prompted:
   - Enter the directory path containing correctly named files (e.g., the final front card PDFs completed in [step 7](back-card-generation.md#7-add-trim-marks-for-backs))
   - Enter the directory path containing files to be renamed (e.g., back cards we are currently working on)

> [!NOTE]  
> This second run will ensure that the numbering sequence of the BACK cards matches the sequence of the FRONT cards, maintaining consistency between the front and back of each player card.

## 2. Render Borders Blue and Add to Cards

### 2.1 Prepare Files

1. Ensure all combined player/background PDFs from Step 1 are in a single folder. Even if you have different editions (e.g. Bronze and Silver) you will only need to run this script once for all of the player cards, because the back border is blue for them all.
2. Locate the back border for your club in the `assets/borders/<club_name>/back_border/` directory. The file should be named `<club_name>-vector_border_blue.pdf`.

### 2.2 Modify Vector Borders (optional)

If the back border for your club doesn't exist, follow these steps to create one:

1. Choose an existing back border file from another club as a template (e.g., from [athletifi_select](../assets/borders/athletifi_select/back_border/) or [coventry_sa](../assets/borders/coventry_sa/back_border/)).
2. Open the template file in Adobe Illustrator.
3. Find an existing vectorized version of the logo for the club you're generating cards for.
4. Import this logo into the Illustrator file and place it over the original club logo.
5. Adjust the size of the new logo to match the size of the previous club logo.
6. Position the new logo to roughly match the position of the previous logo.
7. Delete the previous club logo.
8. Save this as a new PDF file in the club folder for this club following the naming convention: `<club_name>-vector_border_blue.pdf`

### 2.3 Add Borders to Cards

1. Open Adobe Illustrator and go to 'File' > 'Scripts' > 'Other Script...'.
2. Navigate to the `scripts/adobe/illustrator/front-step6_back-step2/` directory and select [combinePlayerCardBorderWithBackgrounds.jsx](../scripts/adobe/illustrator/front-step6_back-step2/combinePlayerCardBorderWithBackgrounds.jsx).
3. When prompted by the script:
   - Select the folder containing your combined player/background PDFs.
   - Choose the appropriate border PDF file (print version).
   - Select an output folder for the final combined PDFs.
   - When prompted to set a custom offset, start with the default (0,0) unless you notice alignment issues.
   - The script will then ask if you want to set a custom offset or use the default (0,0). Set an offset of your choosing or use the default.
   - When prompted to check the alignment of the border on the first file, ensure that border was properly overlayed in the correct position. If it was, you can click yes to continue the batch. If it was not, click no so you can try a new offset.
   - Once you've confirmed the correct offset, the script will automatically process all remaining PDFs in the selected folder, adding the border to each one using the confirmed offset.
4. Review a few of the generated PDFs to ensure the border is correctly applied. Verify that the dimensions are still correct (3.875 x 2.875 inches).

## 3. Add Database Records to Properly Link to QR Code

### 3.1 Prepare Files

1. If you haven't done it already, convert all the player card PDFs to WEBP for adding into the database, as this is the file type that should be used for rendering on the platform.
2. Create a new CSV file named `card_filenames.csv` with all of the filenames for the player card PDFs.
   - This CSV just needs a single column with the header "filename".
   - List all the player card PDF filenames (for the backs) in this column, one filename per row.

### 3.2 Parse Filenames

1. Navigate to the `scripts/python/back-step3/` directory.
2. Run the [parse_filenames.py](../scripts/python/back-step3/parse_filenames.py) script:

   ```shell
   python3 parse_filenames.py
   ```

3. When prompted, enter the path to the CSV file containing the filenames.

> [!NOTE]  
> This script will generate a new CSV file called `parsed_card_data.csv` with extracted information from the filenames, including both the original PDF filename and the corresponding WebP filename.

> [!IMPORTANT]  
> The parse_card_data.csv will be needed in the next step as well as part of the QR Code generation process, so ensure that you keep it saved.

### 3.3 Generate Database Queries

1. Run the [generate_athletifi_db_queries.py](../scripts/python/back-step3/generate_athletifi_db_queries.py) script:

   ```shell
   python3 generate_athletifi_db_queries.py
   ```

2. Follow the prompts to generate the SQL queries for checking and updating records.

## 4. Generate QR Codes

### 4.1 Prepare QR Code Data

1. Run the QR code check query generated as the last step of the `generate_athletifi_db_queries.py` script and export the results as a CSV file.
2. Run the [process_qr_code_csv.py](../scripts/python/back-step4/process_qr_code_csv.py) script:

   ```shell
   python3 process_qr_code_csv.py
   ```

3. When prompted:
   - Enter the path to the CSV file exported from the QR code check query
   - Enter the path to the parsed_card_data.csv file (generated by parse_filenames.py)
   - Specify the output folder for the processed CSV
   - Enter the S3 URL prefix (or press Enter to use the default)

> [!NOTE]  
> This script will automatically create a CSV with the following changes:
> - Remove the S3 URL prefix from the card_image_url column
> - Change the file extension from .webp to .pdf
> - Rename the card_image_url column to "card_filename"
> - Prepend the QR code base URL `https://athleti.fi/qr-code/` to each qrcode_id value
> - Rename the qrcode_id column to "qr_code_url"
> - Remove the dashboard_slug column

### 4.2 Generate QR Codes

1. Ensure that the CSV created in the last step has the header `qr_code_url`, `qrcode_url`, or just `url`.
2. Make a design you are happy with using https://qr-code-styling.com/, then export a json into the project folder.
3. Navigate to the `scripts/node/batch-qr-code-generator/` directory.
4. Run the [batch-generate-qr.js](../scripts/node/batch-qr-code-generator/batch-generate-qr.js) script:

   ```shell
   node batch-generate-qr.js
   ```

5. When prompted, enter the full path to your CSV file containing the QR code URLs.
6. Set the output to SVG when prompted.

> [!NOTE]  
> The script will generate SVG QR codes in the qr_codes folder within the batch_qr_code_generator project folder. Each QR code will be named to match its corresponding card filename (with `_qr` appended at the end and .svg extension instead of .pdf)

7. Copy these files to the working directory for the back card PDFs in a new folder called `qr_codes_before`.

## 5. Format QR Codes in Illustrator

### 5.1 Set Up Illustrator Action

1. Open Adobe Illustrator.
2. If it is not already in your actions panel, load the needed action from the [StylizeQRCodeAndRemoveLinesJUL2024.aia](../assets/actions/illustrator/back-step5/stylizeQRCode.aia) file.
3. Open up the action "deleteLinesThenStylizReshape" and delete the last two steps: "Save as" and "Close".
4. Press the record button.
5. Record the "Save as" command:
   - Keep the filename the same
   - Keep the directory the same (this should be the directory that all the files in the batch will be)
   - Change the format from 'SVG' to 'Adobe PDF (pdf)'
   - Create a new folder called `qr_codes_after` and save the file there
   - Choose the [High Quality Print] preset
6. Record the "Close" command.
7. Press the Stop Button. The Action is now ready to run.

> [!NOTE]  
> If no other files are open, then the actions window may disappear. Click 'Window' > 'Actions' in the menu to bring back the Actions window so you can click the stop button.

### 5.2 Process QR Codes

1. If the actions window isn't showing, then click 'Window' > 'Actions'.
2. Click the hamburger menu in the Actions window, and then click "Batch...".
3. In the Batch dialog:
   - Select Set: "StylizeQRCode"
   - Select action: "deleteLinesThenStylizReshape"
   - Set source to folder, and choose the `qr_codes_before` folder where your new QR SVG files are.
   - Set Destination to 'None'
4. Click "OK" to start batch processing.

## 6. Add QRs to Back

### 6.1 Prepare Files

1. Ensure all back design PDFs (created in step 2) are in a single folder.
2. Place all formatted QR code PDFs (from step 5) in a separate folder.

### 6.2 Run QR Code Overlay Script

1. Open Adobe Illustrator.
2. Go to 'File' > 'Scripts' > 'Other Script' and select the [overlayQRCodes.jsx](../scripts/adobe/illustrator/back-step6/overlayQRCodes.jsx) script.
3. When prompted:
   - Select the folder containing your back design PDFs.
   - Select the folder containing your QR code PDFs.
   - Choose an output folder for the combined PDFs.
4. Review the results:
   - Check the completion message for a summary of processed files and any errors.
   - Open several PDFs in the output folder to verify that the QR codes are correctly positioned on the card backs.

> [!IMPORTANT]  
> If any files weren't processed, check that the filenames match between back designs and QR codes.

## 7. Add Trim Marks (for Backs)

For both the front and the backs, instead of printing at 2.5" x 3.5", which is standard trading card size, we will actually be printing at 2.625"x3.625". This means that we need to add an additional bleed of 0.125" (1/8") to bring the total to 2.875"x3.875".

### 7.1 Set Up Illustrator Action

1. Open Adobe Illustrator.
2. Load the [AddTrimMarksToPrintCards.aia](../assets/actions/illustrator/front-step7_back-step7/AddTrimMarksToPrintCards.aia) action set into Illustrator:
   - Open the Actions panel ('Window' > 'Actions').
   - Click the panel menu icon (four horizontal lines) and choose "Load Actions".
   - Navigate to the `assets/actions/illustrator/front-step7_back-step7/` directory and select `AddTrimMarksToPrintCards.aia`.
3. Open up the action and delete the last two steps: "Save as" and "Close".
4. Press the record button.
5. Record the "Save as" command:
   - Keep the filename the same
   - Keep the directory the same (this should be the directory that all the files in the batch will be)
   - Choose the [High Quality Print] preset
   - Go to the 'Marks and Bleeds' section in the sidebar, then navigate to the Marks section and check 'Trim Marks'.
   - Still within 'Marks and Bleeds', navigate to 'Bleeds', and set the bleed on all four sides to '0.125 in' (Top, Bottom, Left, Right)
6. Record the "Close" command.
7. Press the Stop Button. The Action is now ready to run.

> [!NOTE]  
> If no other files are open, then the actions window may disappear. Click 'Window' > 'Actions' in the menu to bring back the Actions window so you can click the stop button.

### 7.2 Run Batch Process

1. From the Actions menu, click the menu icon (three horizontal lines) and click "Batch…".
2. In the Batch dialog:
   - Set: "AddTrimMarksToPrintCards"
   - Action: "AddTrimMarksToPrintCards"
   - Choose the folder with your PDFs
   - Set Destination to "Save and Close"
3. Click OK to start the batch process.

> [!NOTE]  
> If the batch does not seem to be saving the files, it may be because it is trying to save the files in the original location that was chosen when the action was recorded, and overwriting the same file over and over. If that is the case, you must re-record the "Save As" segment of the action, setting the trim mark and setting the document bleed to 0.125", and setting it to replace the original file.

This completes the generation process for the card backs! Always review the output at each stage to ensure quality and consistency across all cards.
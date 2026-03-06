# Card Generation Runbook — 7-Player × 11-Card Batch (March 2026)

## Project Root

```
~/Code/athletifi-code/card-factory/
```

All paths below are relative to this root unless they start with `~/`.

---

## Player Roster

| # | Player | Jersey # |
|---|--------|----------|
| 1 | Axel Islas | 5 |
| 2 | Cameron Joyner | — |
| 3 | Doniyorjon Aminjonov | — |
| 4 | Jesus Marcelo Bayran-Jimenez | — |
| 5 | Kardigue Sissoko | — |
| 6 | Nycollas Andrade dos Santos | — |
| 7 | Ray Batista | — |

Every player gets **all 11 card designs** → **77 total cards**.

---

## 11 Background × Border Combinations

| # | Background | Border |
|---|-----------|--------|
| 1 | bg-blue-brush.png | Red |
| 2 | bg-blue-brush.png | Gold |
| 3 | bg-gold-on-black.png | Blue |
| 4 | bg-red-multipattern.png | Gold |
| 5 | bg-volcano-floor.png | Blue |
| 6 | bg-geometric-shatter.png | Blue |
| 7 | bg-kanji.png | Black |
| 8 | bg-stadium-lightning-bolt.png | Black |
| 9 | bg-gold-brush.png | Gold |
| 10 | bg-magenta-blue-swirls.png | Bronze |
| 11 | bg-trophy-purple.png | Silver |

### Grouped by Border Color

This grouping drives the entire pipeline — steps 4, 5, and 6 are all organized around it.

| Border | Backgrounds | Cards per player | Total cards |
|--------|------------|-----------------|-------------|
| **Blue** | gold-on-black, volcano-floor, geometric-shatter | 3 | 21 |
| **Gold** | blue-brush, red-multipattern, gold-brush | 3 | 21 |
| **Black** | kanji, stadium-lightning-bolt | 2 | 14 |
| **Red** | blue-brush | 1 | 7 |
| **Bronze** | magenta-blue-swirls | 1 | 7 |
| **Silver** | trophy-purple | 1 | 7 |
| | | **11** | **77** |

> **Note:** bg-blue-brush appears in both the Red group and the Gold group. Its PDF needs to be copied into both folders.

---

## Progress Tracker

- [x] **Step 1:** Process player photos → 7 processed PNGs at 3150×4350
- [x] **Step 2:** Create text layer SVGs → 7 SVGs
- [x] **Step 3:** Merge text layers with player photos → 7 player+text PDFs
- [x] **Step 4:** Convert background PNGs to PDFs and distribute into 6 border-color folders
- [x] **Step 5:** Run merge in COMBINE mode (6 times) → 77 combined PDFs, then rename
- [x] **Step 6:** Run `batchBorders.jsx` → 77 bordered print PDFs in `working/step6-output/`
- [ ] **Step 7:** Run AddTrimMarksToPrintCards batch on all 77 → 77 final print-ready PDFs
- [ ] **Back card generation** (Steps 1–7 for backs)
- [ ] **Cleanup:** Remove `working/` directory

---

## Step 1: Process Player Photos ✅ DONE

### 1.1 Install the Photoshop script

```bash
sudo cp scripts/adobe/photoshop/front-step1/processPlayerPhotoshop.jsx \
  "/Applications/Adobe Photoshop 2025/Presets/Scripts/"
```

> **Note:** Use your current Photoshop version's path. `sudo` is required on macOS.

Restart Photoshop after copying.

### 1.2 Create output directory

```bash
mkdir -p working/step1-processed-photos
```

### 1.3 Ensure all photos are PNGs

The batch script only processes `.png` files. If player photos are `.jpg` or `.jpeg`, rename them first:

```bash
cd /path/to/player-photos
for f in *.jpg *.jpeg; do
  [ -f "$f" ] && mv "$f" "${f%.*}.png"
done
```

### 1.4 Run the batch script

In Photoshop: **File → Scripts → Browse** → select `batchProcessPlayersPhotoshop.jsx`.

When prompted, select the folder containing player photos. Output files will have a `Resized_` prefix.

> **Note:** The `TouchUpAndResizePlayers` action (loaded from `assets/actions/photoshop/front-step1/Step1-ProcessPlayerPhotos.atn`) is an alternative that includes auto-levels and Camera Raw enhancements, but it has been unreliable with Photoshop 2025. Use `batchProcessPlayersPhotoshop.jsx` as the primary method.

### 1.5 Move and clean up output

```bash
cp /path/to/player-photos/Resized_*.png working/step1-processed-photos/
cd working/step1-processed-photos

# Strip the Resized_ prefix
for f in Resized_*.png; do mv "$f" "${f#Resized_}"; done

# Fix names to match SVG text layer conventions:
# - Spaces in first names must remain as spaces (not hyphens)
# - "dos Santos" not "dos-Santos" if that's how the CSV has it
```

> **Important:** PNG filenames must match the text layer SVG names. If the CSV first name is "Jesus Marcelo", the PNG must be `Jesus Marcelo-Bayran-Jimenez.png` (space between Jesus and Marcelo), not `Jesus-Marcelo-Bayran-Jimenez.png`.

Verify you have 7 files:

```bash
ls working/step1-processed-photos/
```

---

## Step 2: Create Text Layers ✅ DONE

### 2.1 Prepare player CSV

Save as `working/players.csv`:

```csv
PlayerFirstName,PlayerLastName,PlayerNumberA,PlayerNumberB
Axel,Islas,5,5
Cameron,Joyner,,
Doniyorjon,Aminjonov,,
Jesus Marcelo,Bayran-Jimenez,,
Kardigue,Sissoko,,
Nycollas,Andrade dos Santos,,
Ray,Batista,,
```

> For players without jersey numbers, leave `PlayerNumberA` and `PlayerNumberB` blank.

### 2.2 Open Illustrator template

Open `assets/templates/front-step2/Text Layers Template-For Single Digits and long last names.ai`.

If it has old variable data, clear it: **Window → Variables** → delete all datasets and variable definitions.

### 2.3 Import player data

**Window → Variables** → hamburger menu → **Load Variable Library…** → select `working/players.csv`.

Cycle through datasets to verify names and numbers look correct.

### 2.4 Export SVGs

```bash
mkdir -p working/step2-text-layers
```

**File → Scripts → Browse** → select `scripts/adobe/illustrator/front-step2/saveTextLayersAsSVG.jsx`.

When prompted, select `working/step2-text-layers/` as the output folder. You should get 7 SVG files.

---

## Step 3: Merge Text Layers with Player Photos ✅ DONE

### 3.1 Create output directory

```bash
mkdir -p working/step3-merged-player-pdfs
```

### 3.2 Run the merge script

In Illustrator: **File → Scripts → Browse** → select `scripts/adobe/illustrator/front-step3/mergeSvgTextWithPlayerPhotos.jsx`.

When prompted:
- **SVG folder:** `working/step2-text-layers/`
- **PNG folder:** `working/step1-processed-photos/`
- **Output folder:** `working/step3-merged-player-pdfs/`

You should get 7 PDFs. If any players show "No matching PNG found," check for name mismatches between SVG and PNG filenames (spaces vs hyphens — see Step 1.5 note).

---

## Step 4: Prepare Backgrounds (PNG → PDF) ✅ DONE

### 4.1 Convert all PNGs to PDFs

```bash
mkdir -p working/step4-all-bg-pdfs
cd scripts/python/front-step4/
python3 png-to-pdf.py
```

When prompted:
- **PNG directory:** `/full/path/to/assets/backgrounds/png/front-step4/`
- **Output directory:** `/full/path/to/working/step4-all-bg-pdfs/`
- **Blank PDF path:** `/full/path/to/assets/templates/front-step4/blank.pdf`

> **Note:** Use full absolute paths — the script does not expand `~`.

### 4.2 Distribute PDFs into border-color folders

```bash
cd working/step4-all-bg-pdfs

# Blue border (3 backgrounds)
cp bg-gold-on-black.pdf      ../../assets/backgrounds/pdf/blue/front-step4/
cp bg-volcano-floor.pdf      ../../assets/backgrounds/pdf/blue/front-step4/
cp bg-geometric-shatter.pdf  ../../assets/backgrounds/pdf/blue/front-step4/

# Gold border (3 backgrounds)
cp bg-blue-brush.pdf         ../../assets/backgrounds/pdf/gold/front-step4/
cp bg-red-multipattern.pdf   ../../assets/backgrounds/pdf/gold/front-step4/
cp bg-gold-brush.pdf         ../../assets/backgrounds/pdf/gold/front-step4/

# Black border (2 backgrounds)
cp bg-kanji.pdf              ../../assets/backgrounds/pdf/black/front-step4/
cp bg-stadium-lightning-bolt.pdf ../../assets/backgrounds/pdf/black/front-step4/

# Red border (1 background) — note: blue-brush is also in gold
cp bg-blue-brush.pdf         ../../assets/backgrounds/pdf/red/front-step4/

# Bronze border (1 background)
cp bg-magenta-blue-swirls.pdf ../../assets/backgrounds/pdf/bronze/front-step4/

# Silver border (1 background)
cp bg-trophy-purple.pdf      ../../assets/backgrounds/pdf/silver/front-step4/
```

### 4.3 Verify the distribution

```bash
cd assets/backgrounds/pdf
find . -name "front-step4" -not -name "*old*" -exec sh -c 'echo "{}:"; ls "{}"' \;
```

Expected: blue → 3, gold → 3, black → 2, red → 1, bronze → 1, silver → 1.

---

## Step 5: Combine Backgrounds with Player Photos ✅ DONE

### 5.1 Create working directories

```bash
mkdir -p working/step5-output/{blue,gold,black,red,bronze,silver}
```

### 5.2 Run the merge script (all 6 colors in one loop)

```bash
cd scripts/python/front-step5_back-step1/

PLAYER_PDFS="/full/path/to/working/step3-merged-player-pdfs/"
BG_BASE="/full/path/to/assets/backgrounds/pdf"
OUT_BASE="/full/path/to/working/step5-output"

for color in blue gold black red bronze silver; do
  echo "=== Running $color ==="
  printf "2\n${OUT_BASE}/${color}/\n${BG_BASE}/${color}/front-step4/\n${PLAYER_PDFS}\n2\n" \
    | python3 merge-images-pdf.py
done
```

Expected totals: blue=21, gold=21, black=14, red=7, bronze=7, silver=7. **77 total.**

### 5.3 Rename files

```bash
python3 rename_files.py
```

- Choose option **1**: "Rename newly generated files to the standard naming convention"
- Enter: `/full/path/to/working/step5-output/`

The script processes all 6 subfolders and tracks sequencing across them.

### 5.4 Verify output

Spot-check a few PDFs from each subfolder. Confirm 77 total files across the 6 subfolders.

---

## Step 6: Add Borders (Print Version) ✅ DONE

### 6.0 Pre-check: Verify border filenames

Before running, ensure no border files have leading spaces or other filename issues:

```bash
ls -la assets/borders/global_united_fc/
```

If any filenames have leading spaces, fix them:

```bash
cd assets/borders/global_united_fc/
mv *<color>* global_united_fc-print_vector_border_<color>.pdf
```

### 6.1 Create output directory

```bash
mkdir -p working/step6-output
```

### 6.2 Run the batch border script

In Illustrator: **File → Scripts → Other Script…** → select `scripts/adobe/illustrator/front-step6_back-step2/batchBorders.jsx`.

The script will:
1. Prompt for an optional custom offset (default 0,0)
2. Process the first file and pause for visual verification
3. On confirmation, process all remaining files across all 6 border-color groups

> **Note:** `batchBorders.jsx` uses artboard-bounds-based positioning, which correctly handles PDFs where the artboard origin is not at (0,0). The original `combinePlayerCardBorderWithBackgrounds.jsx` has a known bug where it positions the border off-canvas — use `batchBorders.jsx` instead.

### 6.3 Verify output

- Open several output PDFs — confirm borders are correctly overlaid
- Verify dimensions are still **3.875 × 2.875 inches**
- You should have **77 bordered PDFs** in `working/step6-output/`

---

## Step 7: Add Trim Marks (Print Version Only) ⬜ IN PROGRESS

### 7.1 Set up the Illustrator action

1. Open Illustrator → **Window → Actions**
2. Load `assets/actions/illustrator/front-step7_back-step7/AddTrimMarksToPrintCards.aia`
3. Expand the action and **delete the last two steps**: "Save" and "Close"
4. Open one PDF from `working/step6-output/` (make a backup copy first)
5. Ensure document units are set to **Inches** (Properties → Document → Units)
6. Click **Record** (circle button)
7. **File → Save As:**
   - Keep the filename and directory the same
   - Click "Yes" to replace
   - Choose **[High Quality Print]** preset
   - **Marks and Bleeds** → check **Trim Marks**
   - **Bleeds** → set all four sides to **0.125 in** (uncheck "Use Document Bleed Settings" if needed)
8. **File → Close**
9. Click **Stop** (square button)

> **Tip:** If the Actions window disappears (no other files open), go to Window → Actions to bring it back.

### 7.2 Run batch process

1. Actions panel menu → **Batch…**
2. Settings:
   - **Set:** AddTrimMarksToPrintCards
   - **Action:** AddTrimMarksToPrintCards
   - **Source:** `working/step6-output/` (all 77 PDFs in one folder)
   - **Destination:** Save and Close
3. Click OK

### 7.3 Verify output

- Open several PDFs and confirm trim marks are present
- Verify bleed is **0.125"** on all sides
- Final dimensions with bleed: **2.875" × 3.875"**, artboard: **2.625" × 3.625"**

> **Warning:** If the action creates the artboard at wrong dimensions, check that "Maintain Width and Height Proportions" (chainlink icon) is disabled.

---

## Back Card Generation ⬜ NOT STARTED

After front card Step 7 is complete, follow the back card generation process. Key steps:

1. **Create blank player PDFs** — Run `create_blank_pdf_copies.py` on `working/step3-merged-player-pdfs/`
2. **Generate background combos** — Run `merge-images-pdf.py` in COMBINE mode (same 6 border-color groups as fronts)
3. **Rename files** — Run `rename_files.py` option 1, then option 2 to match front card sequencing
4. **Add borders** — Run `batchBorders.jsx` (or `combinePlayerCardBorderWithBackgrounds.jsx`) with back-specific borders
5. **Database records** — Run `parse_filenames.py` and `generate_athletifi_db_queries.py` to link cards to QR codes
6. **Generate QR codes** — Run `process_qr_code_csv.py`, then `batch-generate-qr.js`
7. **Format QR codes** — Run Illustrator batch action to stylize and convert SVG → PDF
8. **Overlay QR codes** — Run `overlayQRCodes.jsx`
9. **Add trim marks** — Same action as front Step 7

> **Known issue:** 3 of 7 players have null `profile_id`, which blocks QR code generation. These need to be resolved before back card generation can proceed for those players.

---

## Cleanup

Once everything is verified:

```bash
rm -rf ~/Code/athletifi-code/card-factory/working/
```

---

## Notes & Gotchas

- **Blank jersey numbers:** 6 of 7 players have no number (only Axel Islas has #5). Leave PlayerNumberA and PlayerNumberB blank in the CSV. The single-digit + long-last-names template handles this.
- **bg-blue-brush is used twice** — it pairs with both the Red border and the Gold border. Its PDF must be copied into both `pdf/red/front-step4/` and `pdf/gold/front-step4/`.
- **PNG filenames must match SVG text layer names** — spaces in first names (e.g., "Jesus Marcelo") must stay as spaces in the PNG filename, not be converted to hyphens.
- **The `Resized_` prefix must be stripped** from Photoshop batch output before Step 3.
- **Use full absolute paths** in all Python scripts — they don't expand `~`.
- **Border filenames may have leading spaces** after download/conversion. Always check with `ls -la` before running Step 6.
- **`batchBorders.jsx` uses artboard-based positioning** — use it instead of the original `combinePlayerCardBorderWithBackgrounds.jsx`, which has a known off-canvas positioning bug.
- **`printf` piping for Step 5** eliminates the need to type inputs 6 times. The color list should match the subdirectories in `assets/backgrounds/pdf/`.
- **rename_files.py handles nested folders** so you only need to run it once, pointing at the parent `working/step5-output/` directory.
- **All 6 border runs in step 6 output to the same folder** (`step6-output/`). Since filenames include player names and background names, there shouldn't be collisions.
- **77 cards in one trim marks batch** in step 7. This will take a while in Illustrator — monitor the first output closely, then let it run.

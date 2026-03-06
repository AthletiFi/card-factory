# card-factory Workflow Improvement Report

**Date:** March 2026
**Context:** Global United FC — 7-player × 11-card batch (77 total print cards)
**Scope:** First database-driven print run. This report combines findings from all three sessions and covers every friction point, bug, architectural mismatch, and documentation gap encountered. It is intended as the canonical reference for updating the project before the next run.

---

## Table of Contents

1. [Fixes Already Applied](#1-fixes-already-applied)
2. [Architectural Shifts From the Original Design](#2-architectural-shifts-from-the-original-design)
3. [Missing Pre-Step: Database and S3 Asset Sourcing](#3-missing-pre-step-database-and-s3-asset-sourcing)
4. [Script Bugs and Changes Needed](#4-script-bugs-and-changes-needed)
5. [Documentation Changes Needed](#5-documentation-changes-needed)
6. [Asset Structure Changes](#6-asset-structure-changes)
7. [Data Quality Issues](#7-data-quality-issues)
8. [Platform-Side Changes Required](#8-platform-side-changes-required)
9. [Summary Table](#9-summary-table)

---

## 1. Fixes Already Applied

These issues were identified and resolved during this batch. No further action needed.

### 1.1 `png-to-pdf.py` — Output directory crash before creation

**Problem:** `sanitize_path()` was called on the output directory before it existed. Since `sanitize_path()` validates with `os.path.exists()`, it threw `FileNotFoundError` before `os.makedirs()` could run. Users had to manually `mkdir` every output directory beforehand.

**Fix applied:** Replaced the `sanitize_path()` call on the output directory with manual path sanitization followed by `os.makedirs(output_dir, exist_ok=True)`. Applied in both the `main()` function and the module-level code.

### 1.2 `rename_files.py` — No pattern for `bg-*` filenames

**Problem:** All 6 hardcoded regex patterns in `rename_new_files()` expected legacy edition names (`Bronze`, `Silver`, `Galaxy`, `Dragon Purple`, etc.). The new `merge-images-pdf.py` COMBINE output produces filenames like `bg-blue-brush_Axel-Islas-5-with-text-layer_1.pdf`, which matched none of them. Every file was skipped with "unrecognized pattern."

**Fix applied:** Added Pattern 7 (`bg-(.+?)_(.+?)-with-text-layer_(\d+)\.pdf`) with logic to handle optional jersey numbers. Produces output like `Axel-Islas-5-blue-brush-01.pdf` or `Cameron-Joyner-kanji-01.pdf`.

### 1.3 `combinePlayerCardBorderWithBackgrounds.jsx` — Border positioned off-canvas

**Problem:** The original script's `combineBorderWithBackground()` function sizes the border using `backgroundDoc.width` and `backgroundDoc.height`, then positions it with `app.getTranslationMatrix()`. This resulted in the border being placed completely off the artboard (e.g., border at X: -169.5, Y: 133.5 while the background was at X: 103.5, Y: 139.5). The root cause is that `doc.width`/`doc.height` and the translation matrix do not account for the artboard's actual origin position.

**Fix applied (in `batchBorders.jsx`):** Replaced the sizing and positioning logic with artboard-bounds-based placement:
```javascript
var artRect = backgroundDoc.artboards[0].artboardRect;
var artWidth = artRect[2] - artRect[0];
var artHeight = artRect[1] - artRect[3];
borderItem.width = artWidth;
borderItem.height = artHeight;
borderItem.position = [artRect[0] + xOffset, artRect[1] - yOffset];
```
This fix should also be backported to the original `combinePlayerCardBorderWithBackgrounds.jsx`.

---

## 2. Architectural Shifts From the Original Design

These are not bugs — they are fundamental differences between what the documentation describes and how the pipeline was actually used. They need to be reflected throughout the docs and in several scripts.

### 2.1 Edition-based organization → Border-color-based organization

**Original assumption:** Cards are organized by "edition" (Bronze, Silver). Each edition has one background set and one border. Folder structure, file naming, and regex patterns all revolve around editions.

**New reality:** Cards are organized by border color (blue, gold, black, red, bronze, silver). Each border-color group contains 1–N different backgrounds. A single player gets all 11 background × border combinations. There are no "editions" in the traditional sense for this club.

**Impact areas:**
- `assets/backgrounds/pdf/` folder structure changed from `pdf/{bronze,silver}/front-step4/` to `pdf/{blue,gold,black,red,bronze,silver}/front-step4/`
- Steps 5 and 6 are each run 6 times (once per border color group) instead of 1–2 times
- All references to "edition" throughout both docs need to be generalized to "border group" or "variant"

**Generalization note:** The set of border colors varies per club and per batch. The pipeline must not assume a fixed set of colors — it should derive the list from the batch's database records or from the subfolders present in `assets/backgrounds/pdf/`. All scripts and documentation that enumerate border colors (including `batchBorders.jsx` and the Step 5 shell loop) should be parameterized rather than hardcoded.

### 2.2 Per-club bordered PDFs → Flat per-color SVGs from S3

**Original assumption:** Borders live in `assets/borders/<club_name>/print_borders/` and `digital_borders/`, named `<club_name>-print_vector_border_<edition>.pdf`. They are already PDFs in the project.

**New reality for Global United FC:** Borders were downloaded from S3 as SVGs (`print-border-blue.svg`, etc.) and required manual conversion to PDF before use. They are stored flat in `assets/borders/global_united_fc/` without print/digital subfolders. Border names map to colors, not editions.

**Impact:** Step 6.1 in `front-card-generation.md` directs users to `assets/borders/<club_name>/print_borders/` — this path doesn't exist for Global United FC. The SVG-to-PDF conversion is completely undocumented.

**Generalization note:** A standard border naming convention needs to be established and documented. The current naming varies between clubs: older clubs use `<club_name>-print_vector_border_<edition>.pdf` while Global United FC uses `global_united_fc-print_vector_border_<color>.pdf`. The convention should be formalized as `<club_name>-print_vector_border_<color>.pdf` (or just `print-border-<color>.pdf`) and all scripts that construct border file paths — including `batchBorders.jsx` — should derive filenames from a consistent pattern rather than hardcoding them per club.

### 2.3 Targeted per-player assignments → Cartesian product for all players

**Original assumption:** A specific background is assigned to each player (or a small number per edition). Step 5 uses MERGE mode (1-for-1 pairing).

**New reality:** Every player gets every one of the 11 background × border designs. COMBINE mode produces the cartesian product. The workflow becomes: group backgrounds by border color → run COMBINE once per group → apply the matching border to that group.

**Impact:** The docs only describe running Step 5 "once per edition." The grouped-by-border-color approach — where Steps 5 and 6 are each run N times — is not documented at all.

**Generalization note:** Future batches may use either MERGE mode (specific player-to-background assignments) or COMBINE mode (all players get all backgrounds), or a mix. The documentation should describe both workflows clearly and help the operator choose based on their batch requirements. The Step 0 database query results should make it obvious which mode is needed.

### 2.4 QR code URL format: profile-based → order-based

**Original assumption (card-factory docs):** QR codes on card backs link to `https://athleti.fi/qr-code/<profile_id>`. The back card scripts (`scripts/python/back-step3/` and `scripts/python/back-step4/`) build URLs by querying the `cards.profile` column, then constructing URLs from profile IDs.

**New reality (current platform codebase):** The platform no longer uses the `athleti.fi/qr-code/<profile_id>` URL scheme. QR codes now resolve through the **order invite** system. The platform's `AccessRequests.tsx` component generates QR codes as:

```tsx
value={`${baseUrl}/invite/${order.id}`}
```

When scanned, the `/invite/<order_id>` route is handled by `getPhysicalCardRedirectURL()` in `src/actions/cardOrderActions.tsx`, which:
1. Looks up the `PhysicalCardOrder` by ID
2. Checks the invite mode (public or private) via the `Invites` temp store
3. If public: redirects to `/profile/<card.profile>?referer=<order_id>`
4. If private: creates an access request and notifies the card owner for approval

The scan target is the **PhysicalCardOrder UUID**, not the profile ID. The profile is resolved server-side at scan time. This is a fundamental change to how QR codes work.

**Impact on card-factory:**
- `scripts/python/back-step3/generate_athletifi_db_queries.py` builds queries around profile IDs — needs rewrite for order IDs
- `scripts/python/back-step3/parse_filenames.py` maps card filenames to profiles — needs to map to orders instead
- `scripts/python/back-step4/process_qr_code_csv.py` prepends `https://athleti.fi/qr-code/` to profile IDs — needs to use `<baseUrl>/invite/<order_id>` instead
- `back-card-generation.md` Steps 3 and 4 describe the old profile-based flow throughout

**Generalization note:** The base URL (currently `https://pleyr.com` or equivalent) must be configurable per environment. The card-factory scripts should accept it as a parameter rather than hardcoding any URL. The invite system also supports public/private modes that affect user experience on scan, but this is handled server-side and does not affect the QR URL printed on the card.

### 2.5 Profile required at print time → Profile may not exist yet

**Original assumption (card-factory docs):** Every card being printed has a `cards.profile` value that exists and points to the correct player. The back card workflow queries profile data to construct QR URLs.

**New reality (current platform codebase):** The `cards.profile` column is **nullable by design**. The GraphQL schema comment on `Card.representedProfile` is explicit:

> "Visitors are allowed to create Cards without first having a Profile; they will be provided with a mechanism to claim a card (and attach a concrete Profile) later. Therefore, representedProfile is nullable and createdByOutsider is a nullable String field."

Cards are created with `profile: null` in two common scenarios:

1. **Parent not logged in / no profile session:** The `emailPlayerCard()` flow derives `profileId` from the session. If the user has no profile (spectator, unauthenticated, or logged in as a parent creating a card for their kid), `profileId` is `undefined` and the card is inserted with `profile: null`.

2. **Parent logged in with their own profile, creating a card for their kid:** The `savePlayerCard()` flow passes the **parent's** `profileId`. The card gets `profile` set to the parent's profile — not the kid's. This is semantically incorrect for QR purposes (scanning the QR would route to the parent's profile page, not the child's), but it doesn't crash.

The platform includes a `claimCard()` action that sets `card.profile` after the fact, and the order confirmation email includes a "CLAIM YOUR CARD" CTA linking to `/claim-card/<card_id>`. So profile linking is designed to happen *after* card creation and ordering, not before.

**Impact on card-factory:** The old workflow treated `cards.profile IS NULL` as bad data. The new workflow must treat it as an expected state, where the QR code is printed with an `invite/<order_id>` URL that will work correctly once the card is claimed, and will need graceful handling if scanned before claiming.

> **⚠️ IMPORTANT:** This shift has a platform-side dependency. See [§8: Platform-Side Changes Required](#8-platform-side-changes-required) for details on what must be fixed in the web application before null-profile QR codes can work end-to-end.

---

## 3. Missing Pre-Step: Database and S3 Asset Sourcing

The existing documentation assumes all assets are already present in the project. There is no Step 0 covering how to identify which orders need to be printed, which assets to download, or where to find them. This entire phase had to be improvised from scratch.

### 3.1 What is missing from the docs

- No SQL query documented for identifying pending print orders
- No documentation of the `cards` table schema or how its fields map to pipeline steps
- No documentation of the two S3 buckets:
  - `athletifi-s3/user-uploads/<asset_id><ext>` for player photos
  - `athletifi-webapp-assets/card/` for backgrounds and borders
- No name-mapping table between database values (e.g. `"Blue Brush"`) and S3 filenames (e.g. `bg-blue-brush.png`)
- No step for updating `fulfillment_status` to `'printed'` after cards are generated
- No documentation of the order → card → profile data chain and how it maps to QR code generation

### 3.2 Recommended additions

Add a **Step 0** to `front-card-generation.md` covering:

**SQL query for pending orders (front card data + QR readiness check):**
```sql
SELECT
  c.id AS card_id,
  c.player_name,
  c.jersey_number,
  c.border,
  c.background,
  a.id AS asset_id,
  a.extension,
  p.id AS profile_id,
  pco.id AS order_id,
  pco.order_quantity,
  pco."user" AS ordering_user_id,
  CASE
    WHEN c.profile IS NULL THEN 'UNCLAIMED'
    WHEN c.profile IS NOT NULL AND p.owner = pco."user" THEN 'SELF_OWNED'
    WHEN c.profile IS NOT NULL AND p.owner != pco."user" THEN 'OWNER_MISMATCH'
    ELSE 'UNKNOWN'
  END AS profile_status
FROM physical_card_orders pco
JOIN cards c ON pco.card = c.id
JOIN assets a ON c.player_image = a.id
LEFT JOIN profiles p ON c.profile = p.id
WHERE pco.checkout_status = 'completed'
  AND pco.fulfillment_status = 'pending';
```

The `profile_status` column flags three states the operator must be aware of:
- **`SELF_OWNED`**: Card is linked to a profile that belongs to the person who ordered it. This is the happy path — QR code will work immediately when scanned.
- **`UNCLAIMED`**: Card has no profile link. QR code can be printed with `invite/<order_id>` URL, but scanning it will fail with a server error in the current platform code (see [§8.1](#81-getphysicalcardredirecturl-crashes-on-null-profile)). QR will start working after the card is claimed, *once the platform-side fix is deployed*.
- **`OWNER_MISMATCH`**: Card is linked to a profile, but the profile belongs to a different user than the one who ordered the card. This typically means a parent ordered a card for their kid and the card got linked to the parent's profile (see [§2.5](#25-profile-required-at-print-time--profile-may-not-exist-yet)). The QR code will work, but will route to the wrong person's profile page.

**S3 download commands:**
```bash
# Player photos
aws s3 cp s3://athletifi-s3/user-uploads/<asset_id><extension> ./player-photos/ --region us-east-2

# All backgrounds
aws s3 sync s3://athletifi-webapp-assets/card/ ./backgrounds/ \
  --exclude "*" --include "bg-*.png" --region us-east-2

# All print borders
aws s3 sync s3://athletifi-webapp-assets/card/ ./borders/ \
  --exclude "*" --include "print-border-*.svg" --region us-east-2
```

**Name-mapping table** (add to docs as a reference example):

> **Note:** The table below is specific to the Global United FC March 2026 batch. Each batch will have its own set of background × border combinations, derived from the Step 0 SQL query results. The operator should build an equivalent mapping table for each new batch by cross-referencing the `border` and `background` column values from the database with the actual S3 filenames.

| DB `border` value | DB `background` value | S3 filename |
|---|---|---|
| Blue | Blue Brush | `bg-blue-brush.png` |
| Blue | Geometric Shatter | `bg-geometric-shatter.png` |
| Blue | Volcano Floor | `bg-volcano-floor.png` |
| Blue | Gold On Black | `bg-gold-on-black.png` |
| Gold | Blue Brush | `bg-blue-brush.png` |
| Gold | Red Multipattern | `bg-red-multipattern.png` |
| Red | Blue Brush | `bg-blue-brush.png` |
| Black | Stadium Lightning Bolt | `bg-stadium-lightning-bolt.png` |
| Silver | Gold Brush | `bg-gold-brush.png` |
| Bronze | Geometric Shatter | `bg-geometric-shatter.png` |

**Generalization note:** Consider adding a script to `scripts/python/` that takes the SQL query output CSV and automatically generates: (1) the background × border grouping table, (2) the S3 download commands for the specific assets needed, (3) the `mkdir` commands for the border-color subfolder structure, and (4) the player CSV for Step 2. This would eliminate the most error-prone manual step in the pipeline.

**Post-run fulfillment update:**
```sql
UPDATE physical_card_orders
SET fulfillment_status = 'printed'
WHERE id IN ('<order_id_1>', '<order_id_2>', ...);
```

Add the standard query as a saved file in `scripts/sql/pending_print_orders.sql`.

---

## 4. Script Bugs and Changes Needed

### 4.1 `batchProcessPlayersPhotoshop.jsx` — Only processes PNG files

**Problem:** The file filter `folder.getFiles("*.png")` silently skips `.jpg` and `.jpeg` files. In this run, 6 of 7 photos were JPG or JPEG, so only 1 was processed on the first attempt. All files had to be renamed to `.png` before re-running.

**Fix:**
```javascript
// Old
var files = folder.getFiles("*.png");

// New
var files = folder.getFiles(function(f) {
    return /\.(png|jpg|jpeg|tif|tiff|psd)$/i.test(f.name);
});
```

### 4.2 `batchProcessPlayersPhotoshop.jsx` — `Resized_` prefix breaks downstream matching

**Problem:** The script saves output as `Resized_<original-name>.png`. The Step 3 merge script (`mergeSvgTextWithPlayerPhotos.jsx`) matches SVG names to PNG names and doesn't expect this prefix, causing matching to fail. Users had to manually strip the prefix.

**Fix:** Remove the prefix. Change `"Resized_" + doc.name` to just `doc.name`. The script already outputs to a separate folder, so there is no risk of overwriting originals.

### 4.3 `saveTextLayersAsSVG.jsx` — "NoNumber" literal bleeds into filenames

**Problem:** When `playerNumber` is null or empty, the script sets `playerNumber = "NoNumber"` and produces filenames like `text layer-Cameron-Joyner-NoNumber.svg`. This literal string then cascades into every downstream script that parses player names from filenames, and into the `rename_files.py` patterns.

**Fix:**
```javascript
// Current
if (playerNumber === null) { playerNumber = "NoNumber"; }
var filename = "text layer-" + playerFirstName + "-" + playerLastName + "-" + playerNumber + ".svg";

// Should be
var filename;
if (!playerNumber || playerNumber === "NoNumber") {
    filename = "text layer-" + playerFirstName + "-" + playerLastName + ".svg";
} else {
    filename = "text layer-" + playerFirstName + "-" + playerLastName + "-" + playerNumber + ".svg";
}
```

### 4.4 `mergeSvgTextWithPlayerPhotos.jsx` — Name matching is brittle with spaces vs hyphens

**Problem:** The matching function splits names on hyphens and checks if all parts appear in the PNG filename. Players with spaces in their names caused mismatches:
- SVG: `text layer-Jesus Marcelo-Bayran-Jimenez.svg` → PNG: `Jesus-Marcelo-Bayran-Jimenez.png` (space vs hyphen between "Jesus" and "Marcelo")
- SVG: `text layer-Nycollas-Andrade dos Santos.svg` → PNG: `Nycollas-Andrade-dos-Santos.png`

**Fix:** Normalize both names before comparison:
```javascript
function normalizeForMatching(name) {
    return name.replace(/[-\s]/g, '_').toLowerCase();
}
```
Apply this to both SVG name parts and PNG filenames before comparing.

### 4.5 `mergeSvgTextWithPlayerPhotos.jsx` — No support for numberless PNG filenames

**Problem:** The PNG naming patterns expected by the matching logic all require a jersey number. Players without numbers produce SVGs without numbers, but the PNG filenames also have no number — and no pattern accounts for this.

**Fix:** Add and document a numberless variant: `[PlayerFirstName]-[PlayerLastName].png`. Test that `findPlayerPngs()` correctly matches when neither the SVG nor the PNG has a number component.

### 4.6 `png-to-pdf.py` — `sanitize_path()` does not expand `~`

**Problem:** Entering `~/Code/athletifi-code/card-factory/...` caused a `FileNotFoundError` because Python's `os.path.exists()` does not expand `~`. Users must type full absolute paths.

**Fix:** Add `os.path.expanduser()` to `sanitize_path()` in every script that uses it:
```python
def sanitize_path(input_path):
    sanitized = input_path.strip('\'"').replace("\\ ", " ").strip()
    sanitized = os.path.expanduser(sanitized)  # add this line
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(...)
```
**Scripts affected:** `png-to-pdf.py`, `merge-images-pdf.py`, `rename_files.py`, `create_blank_pdf_copies.py`, `replace_spaces_with_hyphens.py`

### 4.7 `png-to-pdf.py` — Duplicate code that executes at module level

**Problem:** The file contains three copies of the same logic: the `main()` function, a bare module-level code block below `if __name__ == "__main__"`, and a commented-out "OLD UNSTYLIZED VERSION." The module-level code runs on import before `main()` runs, prompting the user twice. The fix applied in §1.1 had to be made in three separate places because of this.

**Fix:** Delete the module-level code block and the commented-out old version entirely. Keep only the `main()` function and the `if __name__ == "__main__": main()` entry point.

### 4.8 `png-to-pdf.py` — Does not process JPEG files

**Problem:** The file filter only looks for `.png` files, silently skipping `.jpg` and `.jpeg`.

**Fix:**
```python
# Old
png_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]

# New
png_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
```

### 4.9 `rename_files.py` — `get_file_info()` also needs Pattern 7

**Problem:** The `get_file_info()` function (used by option 2, "fix numbering for BACKS") has its own separate set of patterns that still only match legacy edition-based filenames. If option 2 is run against front cards that were renamed with Pattern 7, it won't recognize them.

**Fix:** Add a corresponding pattern to `get_file_info()` matching the output of Pattern 7 (e.g., `Axel-Islas-5-blue-brush-01.pdf`, `Cameron-Joyner-kanji-01.pdf`).

### 4.10 `combinePlayerCardBorderWithBackgrounds.jsx` — Only accepts PDF border files

**Problem:** The script's file filter (`getFiles("*.pdf")`) silently ignores SVG files. New borders from S3 are SVGs. They will not appear in the dialog.

**Fix (Option A — preferred):** Update the filter to accept both formats:
```javascript
// Old
var backgroundFiles = backgroundFolder.getFiles("*.pdf");

// New
var backgroundFiles = backgroundFolder.getFiles(/\.(pdf|svg)$/i);
```
Illustrator handles SVGs natively, so this is low-risk.

**Fix (Option B):** Document a manual SVG-to-PDF conversion step (see §5.7).

### 4.11 `combinePlayerCardBorderWithBackgrounds.jsx` — No per-card border logic

**Problem:** The script applies one border file to every PDF in the folder. With the new multi-color-border reality, this requires manually grouping cards into subfolders by border color and running the script once per group. For this run that was 6 Illustrator sessions.

**Workaround applied:** A batch wrapper script (`batchBorders.jsx`) was created during this run that iterates through all border-color groups automatically, processing the first file with a pause for alignment verification, then running the rest unattended. See §4.13 for generalization needs.

**Recommended long-term fix:** Add a CSV-driven mode to the original script. Accept a CSV with two columns — `card_filename`, `border_file` — and iterate through it, applying the designated border to each card. This enables a single run to process all cards regardless of border variety.

Until the script is updated, document the subfolder-grouping workaround explicitly:
```
step5-output/
  blue/    → run with print-border-blue.pdf
  gold/    → run with print-border-gold.pdf
  red/     → run with print-border-red.pdf
  black/   → run with print-border-black.pdf
```

### 4.12 `merge-images-pdf.py` — No non-interactive/CLI mode

**Problem:** Running the script interactively 6 times (once per border-color group) requires typing 5 inputs each time. We worked around this with `printf` piping, but it is not documented.

**Workaround applied:** Shell loop with `printf` piping:
```bash
for color in blue gold black red bronze silver; do
  printf "2\n${OUT}/${color}/\n${BGS}/${color}/front-step4/\n${PLAYERS}/\n2\n" \
    | python3 merge-images-pdf.py
done
```

**Generalization note:** The color list in this loop is hardcoded. For reuse across batches, the loop should either accept the color list as a parameter or auto-discover it from the subdirectories present in the backgrounds PDF folder:
```bash
for color in $(ls "$BG_BASE"); do
  [ -d "$BG_BASE/$color/front-step4" ] || continue
  # ... run merge
done
```

**Recommended long-term fix:** Add CLI argument support:
```bash
python3 merge-images-pdf.py \
  --layers 2 \
  --output ./out/ \
  --layer1 ./bgs/blue/ \
  --layer2 ./players/ \
  --mode combine
```
At minimum, document the `printf` piping technique in the runbook as a workaround.

### 4.13 `batchBorders.jsx` — Needs generalization before committing to repo

**Problem:** The `batchBorders.jsx` wrapper script created during this batch successfully automates Step 6 (applying borders to all border-color groups in a single Illustrator run). However, it currently has several hardcoded values that make it specific to this Global United FC batch:

- **Project root path:** Hardcoded to `/Users/qisforq/Code/athletifi-code/card-factory`
- **Club name:** Hardcoded to `global_united_fc` in both the border directory path and every border filename
- **Border color list:** Hardcoded array of 6 specific colors (`blue`, `gold`, `black`, `red`, `bronze`, `silver`)
- **Border filename pattern:** Hardcoded to `global_united_fc-print_vector_border_<color>.pdf`
- **Input/output paths:** Hardcoded to `working/step5-output` and `working/step6-output`

**Current script location:** `scripts/adobe/illustrator/front-step6_back-step2/batchBorders.jsx` (to be committed)

**Required changes for generalization:**
1. **Use folder selection dialogs** for project root, border folder, input folder, and output folder — matching the UX pattern of other JSX scripts in the project
2. **Auto-discover border colors** by scanning subdirectories of the step5-output folder, rather than hardcoding a list
3. **Auto-discover border files** by scanning the selected border folder for files matching `*border*<color>*` or `*<color>*border*`, rather than constructing filenames from a template
4. **Retain the offset prompt and first-file verification** workflow, which proved valuable during this batch
5. **Backport the artboard-based positioning fix** (see §1.3) into the original `combinePlayerCardBorderWithBackgrounds.jsx` as well

**Recommended generalized flow:**
```
1. User selects: step5-output folder, borders folder, output folder
2. Script scans step5-output/ subdirectories → discovers color list
3. For each color, script finds matching border file in borders folder
4. Prompts for offset, processes first file, pauses for verification
5. On confirmation, processes all remaining files across all color groups
```

### 4.14 `combinePlayerCardBorderWithBackgrounds.jsx` — Border positioning uses wrong coordinate system

**Problem:** The original script sizes the border with `backgroundDoc.width` / `backgroundDoc.height` and positions it using `app.getTranslationMatrix(xOffset, -yOffset)`. These values do not account for the artboard's actual position within the document coordinate space. When the artboard origin is not at (0,0) — which is common with PDFs generated by the merge script — the border lands off-canvas entirely.

**Fix:** Replace the sizing and positioning logic with artboard-bounds-based placement (same fix as applied in `batchBorders.jsx`, see §1.3):
```javascript
var artRect = backgroundDoc.artboards[0].artboardRect;
var artWidth = artRect[2] - artRect[0];
var artHeight = artRect[1] - artRect[3];

borderItem.width = artWidth;
borderItem.height = artHeight;
borderItem.position = [artRect[0] + xOffset, artRect[1] - yOffset];
```
This ensures the border is placed on the artboard regardless of the document's internal coordinate system.

### 4.15 `generate_athletifi_db_queries.py` — Generates queries using obsolete profile-based QR URL scheme

**Problem:** This script generates SQL queries that look up `cards.profile` to build QR code URLs in the format `https://athleti.fi/qr-code/<profile_id>`. The platform no longer uses this URL scheme. The current platform routes QR scans through `<baseUrl>/invite/<order_id>`, where `order_id` is the `physical_card_orders.id` UUID.

**Fix:** Rewrite the script to:
1. Query `physical_card_orders` joined to `cards` (instead of querying cards/profiles directly)
2. Use the order ID as the QR code identifier
3. Build URLs in the format `<baseUrl>/invite/<order_id>`
4. Accept the base URL as a configurable parameter (defaulting to the production URL)

The core query should become:
```sql
SELECT
  pco.id AS order_id,
  c.id AS card_id,
  c.player_name,
  c.profile AS profile_id
FROM physical_card_orders pco
JOIN cards c ON pco.card = c.id
WHERE pco.checkout_status = 'completed'
  AND pco.fulfillment_status = 'pending';
```

The script's output CSV should map each card filename to its `invite/<order_id>` URL rather than `qr-code/<profile_id>`.

### 4.16 `process_qr_code_csv.py` — Prepends obsolete `athleti.fi/qr-code/` URL prefix

**Problem:** This script hardcodes the QR code base URL as `https://athleti.fi/qr-code/` and appends profile-based `qrcode_id` values. Both the domain and the URL path are wrong for the current platform.

**Fix:** Change the default QR code base URL to `<baseUrl>/invite/` and use order IDs instead of profile/qrcode IDs. The script should:
1. Accept the base URL as a parameter (with a sensible default for the current production environment)
2. Map card filenames to order IDs (not profile IDs)
3. Produce output CSV with columns: `card_filename`, `qr_code_url` where `qr_code_url` = `<baseUrl>/invite/<order_id>`

### 4.17 `parse_filenames.py` — Output CSV schema assumes profile-based flow

**Problem:** This script produces a `parsed_card_data.csv` that maps filenames to data extracted from the filename itself. It does not include order IDs because the original workflow derived QR URLs from profile IDs, which came from a separate database query. In the new order-based flow, the QR URL depends on the order ID, which must come from the database — not from the filename.

**Fix:** The script's role in the pipeline needs to change. Rather than being the sole bridge between filenames and QR data, it should merge filename data with the Step 0 SQL query output. Specifically:
1. Accept both the card filename list and the Step 0 query output CSV as inputs
2. Match each filename to its corresponding order record (using player name + background + border as the join key)
3. Output a merged CSV containing: `card_filename`, `order_id`, `qr_code_url`, `profile_status`

The `profile_status` column (from §3.2) allows the operator to make informed decisions about which cards get QR codes and which need manual intervention.

**Generalization note:** The join between filenames and database records is inherently fragile because it depends on naming conventions. Consider adding the order ID to the card filename itself during the rename step (e.g., `Axel-Islas-5-blue-brush-<short_order_id>-01.pdf`) to make the mapping deterministic. Until then, document the expected matching logic clearly.

---

## 5. Documentation Changes Needed

### 5.1 Step 1.2 — Hardcoded Photoshop version path

**Current:** References `/Applications/Adobe Photoshop 2024/Presets/Scripts/`.

**Fix:** Change to "your current Photoshop version's Presets/Scripts folder" (e.g., `/Applications/Adobe Photoshop 2025/Presets/Scripts/`) and note that `sudo` may be required on macOS.

### 5.2 Step 1.3 — Fragile Photoshop action, JSX as primary method

**Problem:** The `TouchUpAndResizePlayers` action kept pausing on the Curves dialog and hanging on the script phase, requiring abandonment in favor of `batchProcessPlayersPhotoshop.jsx`.

**Fix:** Promote `batchProcessPlayersPhotoshop.jsx` as the primary method. Move the action-based approach to a "Optional Enhancement" note. Add a separate optional pre-processing step describing the Camera Raw / auto-levels settings the action provides. If the action is to remain supported, rebuild it from scratch on the current Photoshop version and test end-to-end.

### 5.3 Step 2.2 — No guidance for players without jersey numbers

**Current:** Four template variants are listed (single/double digit × normal/long name). The no-number case is not addressed.

**Fix:** Add a note explaining that for players without jersey numbers, leave `PlayerNumberA` and `PlayerNumberB` blank in the CSV and use any single-digit template. Verify templates render cleanly with empty number fields. Add a fifth template variant explicitly designed for the no-number case.

### 5.4 Step 2.4 — Illustrator Variables panel terminology

**Current:** Says to use "Import…" from the Variables panel menu.

**Fix:** Change to "Load Variable Library…" and note that the exact label may vary by Illustrator version.

### 5.5 Step 3.1 — No concrete naming chain example

**Current:** Says "ensure your file naming is consistent" without specifics.

**Fix:** Add a concrete example showing the full chain for a player with spaces in their name:
```
CSV:   Jesus Marcelo,Bayran-Jimenez,5,5
SVG:   text layer-Jesus Marcelo-Bayran-Jimenez-5.svg
PNG:   Jesus Marcelo-Bayran-Jimenez-5.png  ← must match (spaces preserved from CSV first name)
```
Also add the numberless variant:
```
CSV:   Cameron,Joyner,,
SVG:   text layer-Cameron-Joyner.svg
PNG:   Cameron-Joyner.png
```

**Generalization note:** The naming chain is the single most fragile part of the pipeline. Spaces in first names (e.g., "Jesus Marcelo") propagate through the SVG filename but may be converted to hyphens in the PNG filename, causing the merge script to fail. Until §4.4 is fixed, document that PNG filenames must preserve spaces where the CSV first name has spaces, and use hyphens only where the CSV last name has them.

### 5.6 Step 4 — Background PDF output folder structure

**Current:** Instructs outputting PDFs to `assets/backgrounds/pdf/bronze/front-step4/` or `silver/front-step4/`.

**Fix:** Update to describe the border-color grouping convention:
> Output PDFs should go into a folder that reflects how Step 6 will group them. If organizing by border color (the standard approach for multi-border batches), use `assets/backgrounds/pdf/<border_color>/front-step4/`. Example: backgrounds that will be paired with the blue border go into `assets/backgrounds/pdf/blue/front-step4/`.

Also note that the output directory can now be created automatically by the script (no need to pre-create it).

### 5.7 New pre-step — Border SVG to PDF conversion

**Current:** Not documented anywhere.

**Add:** A new pre-step to Step 6 (or a standalone section) explaining:
> If borders are downloaded from S3 as SVGs, they must be converted to PDF before use. Open each SVG in Illustrator, go to File → Save As, choose Adobe PDF format, select the [High Quality Print] preset, and save to `assets/borders/<club_name>/`. Name the file `<club_name>-print_vector_border_<color>.pdf`.

**Generalization note:** Consider scripting this conversion (Illustrator batch or a shell script using `rsvg-convert` or `inkscape --export-type=pdf`) since it will be needed for every new club whose borders are sourced from S3 as SVGs. Add the script to `scripts/` if created.

### 5.8 Steps 5 and 6 — Border-color grouping workflow

**Current:** Describes running Step 5 "once per edition" and Step 6 "separately for each edition."

**Fix:** Replace with a description of the border-color grouping approach:
1. After converting backgrounds to PDFs (Step 4), organize them into subfolders by border color
2. Run `merge-images-pdf.py` once per border-color subfolder using COMBINE mode
3. Run `combinePlayerCardBorderWithBackgrounds.jsx` (or `batchBorders.jsx`) once per border-color group, using the matching border PDF

Document the `printf` piping technique as a time-saver for the multi-run Step 5 process, and note that the color list should be derived from the actual subfolder structure rather than hardcoded:
```bash
BG_BASE="assets/backgrounds/pdf"
for color in $(ls "$BG_BASE"); do
  [ -d "$BG_BASE/$color/front-step4" ] || continue
  printf "2\n${OUT}/${color}/\n${BG_BASE}/${color}/front-step4/\n${PLAYERS}/\n2\n" \
    | python3 merge-images-pdf.py
done
```

Document `batchBorders.jsx` as the standard approach for Step 6, noting that it must be configured per-batch (see §4.13 for generalization requirements).

### 5.9 Step 5.3 — New filename convention in rename_files.py

**Current:** Lists four legacy filename conventions the script handles, all Bronze/Silver based.

**Add:** The Pattern 7 convention:
- **Input:** `bg-<background>_<PlayerName>-<OptionalNumber>-with-text-layer_<serial>.pdf`
- **Output:** `<PlayerName>-<OptionalNumber>-<background>-<serialByPlayer>.pdf`
- **Example:** `bg-blue-brush_Axel-Islas-5-with-text-layer_1.pdf` → `Axel-Islas-5-blue-brush-01.pdf`

### 5.10 Step 6.1 — Border file location

**Current:** Directs users to `assets/borders/<club_name>/print_borders/`.

**Fix:** Update to accommodate both the subfolder convention (existing clubs) and flat convention (Global United FC):
> Borders may be in `assets/borders/<club_name>/print_borders/` (older clubs) or directly in `assets/borders/<club_name>/` (newer clubs). Include a table mapping each border color to its file path for the current batch.

### 5.11 General — Generalize "edition" language

Throughout both docs, "edition" is used as the primary organizing concept. It should be generalized to "border group" or "variant" to accommodate both the legacy Bronze/Silver approach and the new per-color approach. This affects at least: Step 1.1, Step 5 headers, Step 6 headers, and the overview doc.

### 5.12 Prerequisites section — Python dependencies

**Problem:** Running `png-to-pdf.py` failed with `ModuleNotFoundError` for Pillow, then for PyMuPDF. The README mentions `requirements.txt` but users don't always run it, and the pinned versions are from 2023.

**Fix:** Add a "Prerequisites" check at the top of `front-card-generation.md` reminding users to run `pip install -r scripts/python/requirements.txt`. Update `requirements.txt` to use minimum version pins (e.g., `Pillow>=9.5.0`, `PyMuPDF>=1.22.1`) instead of exact pins.

### 5.13 `back-card-generation.md` — Step 1.1 and Step 2.1

**Step 1.1 current:** "Copy the Background PDFs you've already created for both Silver and Bronze."
**Fix:** Change to background-agnostic language. Note that the background used on the back card must match the background used on the front card for that specific player.

**Step 2.1 current:** Directs to `assets/borders/<club_name>/back_border/`.
**Fix:** Update to accommodate both flat and subfolder border structures.

### 5.14 Runbook template — Generalize for reuse across batches

**Problem:** The runbook created for this batch (`card-generation-runbook.md`) contains Global United FC-specific details: player roster, background × border mapping, exact file counts, and hardcoded paths. It cannot be reused as-is for another club.

**Fix:** Create a runbook template (`card-generation-runbook-template.md`) with placeholders for batch-specific values:
- `<CLUB_NAME>` — club folder name
- `<PLAYER_COUNT>` — number of players
- `<BORDER_COLORS>` — list of border colors for this batch
- `<COMBINATIONS_PER_PLAYER>` — number of background × border combinations
- `<TOTAL_CARDS>` — total card count
- `<BACKGROUND_BORDER_TABLE>` — the mapping table from Step 0

Include the Global United FC runbook as a worked example alongside the template.

### 5.15 `back-card-generation.md` — Steps 3 and 4 describe obsolete QR code flow

**Step 3 current:** Titled "Add Database Records to Properly Link to QR Code." Instructs the operator to run `parse_filenames.py` to extract profile information from filenames, then `generate_athletifi_db_queries.py` to produce SQL queries that link cards to profiles for QR code resolution.

**Step 4 current:** Titled "Generate QR Codes." Instructs the operator to run the QR code check query (which looks up profile-based `qrcode_id` values), then `process_qr_code_csv.py` to build QR URLs using `https://athleti.fi/qr-code/<profile_id>`.

**Fix — Step 3 rewrite:** Rename to "Prepare QR Code Data from Order Records." The step should:
1. Start from the Step 0 SQL query output, which already contains `order_id` for every card being printed
2. Run an updated `parse_filenames.py` (see §4.17) that merges filename data with order data to produce a mapping CSV: `card_filename` → `order_id` → `qr_code_url`
3. The QR URL for each card is simply `<baseUrl>/invite/<order_id>` — no profile lookup needed
4. Include a **profile status check** as a decision gate:
   - If all orders show `profile_status = 'SELF_OWNED'`: proceed normally, all QR codes will work on scan
   - If any orders show `UNCLAIMED` or `OWNER_MISMATCH`: flag them, apply the batch's handling policy (see §7.3), and note that QR codes for unclaimed cards will only work after the platform-side fix in §8.1 is deployed

**Fix — Step 4 rewrite:** Rename to "Generate QR Codes from Order URLs." The step should:
1. Use the merged CSV from Step 3 (not a separate database export)
2. Pass order-based invite URLs to the QR code generator instead of profile URLs
3. Keep the existing QR styling and SVG generation workflow (the visual design of the QR code itself is unchanged)

Remove all references to `qrcode_id`, `dashboard_slug`, and the `athleti.fi/qr-code/` URL prefix from both steps.

### 5.16 `back-card-generation.md` — Add QR code behavior documentation

**Current:** The back card documentation does not explain what happens when a QR code is scanned. It treats QR generation as a mechanical step (URL → image) without describing the user experience on the other end.

**Add:** A new subsection (either in Step 3 or as a standalone reference) explaining:
> **How QR codes work at scan time:**
>
> Each QR code encodes a URL in the format `<baseUrl>/invite/<order_id>`. When someone scans this code:
>
> 1. If the card owner set their QR to **Public mode**: the scanner is redirected to the player's profile page immediately.
> 2. If the card owner set their QR to **Private mode**: the scanner must log in, and their access request is queued for approval by the card owner.
> 3. If the card has **not been claimed yet** (i.e., `card.profile` is null): the scan currently fails with a server error. See [§8.1](#81-getphysicalcardredirecturl-crashes-on-null-profile) for the platform fix required to handle this gracefully.
>
> The public/private mode is managed by the card owner through their dashboard (Settings → QR & Requests). It defaults to private. The card-factory workflow does not control this setting — it only controls which URL is encoded in the QR image.

---

## 6. Asset Structure Changes

### 6.1 Background PNGs — New naming convention, old assets removed

| | Convention | Example |
|---|---|---|
| **Old** | Edition prefix, spaces | `Bronze v2 - Dark Blue.png` |
| **New** | `bg-` prefix, hyphenated | `bg-blue-brush.png` |

The old PNGs and their corresponding PDFs have been moved to `*-old/` directories. Old and new naming conventions are completely incompatible in the existing scripts. This is a clean break.

**Generalization note:** The `bg-` prefix convention should be documented as the standard going forward. All new backgrounds uploaded to S3 should follow this convention. The `rename_files.py` Pattern 7 and all downstream scripts depend on it.

### 6.2 Borders — New club folder without subfolders

| | Convention |
|---|---|
| **Old clubs** (`athletifi_select`, `coventry_sa`) | `print_borders/`, `digital_borders/`, `back_border/` subfolders |
| **New club** (`global_united_fc`) | Border PDFs stored flat at `assets/borders/global_united_fc/` |

**Generalization note:** This inconsistency must be resolved before onboarding additional clubs. Recommend: adopt the flat convention going forward (it's simpler and `batchBorders.jsx` already assumes it), migrate existing clubs to match, and update all documentation. Alternatively, if the subfolder convention is retained, update `batchBorders.jsx` and the border discovery logic to check both `<club>/print_borders/` and `<club>/` as fallback locations.

### 6.3 Generic borders — New folder convention needed

Borders that are not club-specific (color-only borders usable across clubs) have no documented home. Create `assets/borders/generic/print_borders/` as the canonical location and document it in the README.

---

## 7. Data Quality Issues

These are issues in the production database that affect card generation and should be handled during the Step 0 data prep phase.

### 7.1 Trailing empty strings in `player_name` arrays

Several `player_name` values contain a trailing empty string, e.g. `{Cameron,Joyner,""}`. This likely originates from the front-end form. If passed directly to the text layer CSV without cleaning, the empty token creates a stray element in the output filename.

**Fix:** Strip empty strings from `player_name` arrays during Step 0 data preparation before building the CSV for Step 2.

### 7.2 Missing jersey numbers in ~60% of orders

6 of 7 players in this batch had no `jersey_number`. The current documentation and templates don't explicitly address this case (see §4.3, §4.5, §5.3).

**Fix:** Handle at multiple levels — clean data at Step 0, fix the JSX script to omit number from filename, add a numberless template, and add the numberless PNG naming pattern.

### 7.3 Null or incorrect `profile` on cards — blocks or misdirects QR codes

**Original report note:** 3 of the 7 players (and 5 of the original 10 before removals) had a null `profile_id`, blocking QR code generation under the old `athleti.fi/qr-code/<profile_id>` scheme.

**Expanded analysis:** With the updated order-based QR URL scheme (`<baseUrl>/invite/<order_id>`), the *generation* of QR codes is no longer blocked by null profiles — the URL is derived from the order ID, which always exists. However, the **scan-time behavior** is still affected. There are three distinct scenarios:

**Scenario A — Card profile is correctly linked (`SELF_OWNED`):**
The user created a card, claimed it to their own profile, and ordered physical copies. `card.profile` points to the correct player. QR code works perfectly — scans redirect to the player's profile page (with public/private gating).

**Scenario B — Card profile is null (`UNCLAIMED`):**
This occurs when a parent or anonymous user creates a card for someone who doesn't have a Pleyr account, then orders physical copies. The `uploadPlayerCard()` function inserts the card with `profile: profileId` where `profileId` comes from the session. If the creator has no profile (spectator role, unauthenticated, or not logged in), `profileId` is `undefined` and the card is inserted with `profile: null`.

When someone scans the QR code, `getPhysicalCardRedirectURL()` hits:
```typescript
if (!order.card.profile) {
  throw new Error('Card is not associated with a profile');
}
```
This is a **hard server error** — no graceful fallback, no user-facing message. The QR code is completely broken.

However, the card *can* be claimed later via the `/claim-card/<card_id>` flow (the order confirmation email includes a "CLAIM YOUR CARD" button). Once claimed, `card.profile` is set and the QR starts working. The QR URL itself (`invite/<order_id>`) remains stable through this transition.

**Scenario C — Card profile points to wrong person (`OWNER_MISMATCH`):**
This occurs when a logged-in parent creates a card *for their kid* using the card creator. The `savePlayerCard()` flow passes the parent's `profileId`:
```typescript
const { userId, profileId } = await mustGetUserProfile();
await uploadPlayerCard({ ...args, userId, profileId, ... });
```
The card gets `profile` set to the **parent's** profile. If the parent then orders physical copies, the QR code will scan successfully — but it redirects to the parent's profile page, not the kid's. This is technically functional but semantically wrong. There is currently no "transfer card" or "re-assign profile" action in the platform to fix this after the fact.

**Handling policy for card-factory (what to do today):**

For the card-factory workflow, the QR URL generation itself now works regardless of profile state — `invite/<order_id>` is always constructible. The question is whether to print a QR that might not work when scanned.

Recommended tiered approach:
1. **`SELF_OWNED` orders:** Print QR codes normally. Everything works end-to-end.
2. **`UNCLAIMED` orders — if platform fix from §8.1 is deployed:** Print QR codes normally. Scanning before the card is claimed will show a friendly "claim this card" page instead of crashing. Once claimed, the QR activates.
3. **`UNCLAIMED` orders — if platform fix from §8.1 is NOT yet deployed:** Hold QR printing for these cards. The QR will produce a server error if scanned before claiming. Options: (a) print front-only and ship backs separately once claimed, (b) print with QR anyway and accept the temporary broken state, (c) contact the ordering user to claim their card before printing.
4. **`OWNER_MISMATCH` orders:** Print QR codes (they work), but flag these for manual review. The card owner may want to transfer the card to a child's profile in the future. Document the mismatch in the batch log.

Add a **profile status report** as a mandatory output of Step 0 so the operator can apply this policy before proceeding to back card generation.

### 7.4 `player_name` array structure creates ambiguity for multi-part names

Related to §7.1: the `cards.player_name` column is a Postgres text array (e.g., `{Jesus,Marcelo,Bayran-Jimenez}`). When there are more than two elements, it's ambiguous which parts are first name vs. last name. The card-factory pipeline currently assumes `player_name[0]` = first name and `player_name[1]` = last name, but players like "Jesus Marcelo Bayran-Jimenez" have a two-part first name stored as `{Jesus,Marcelo,Bayran-Jimenez}`.

**Fix:** During Step 0 data prep, document the convention: all elements except the last are treated as first name parts (joined with spaces), and the last element is treated as the last name. Handle the trailing empty string case (§7.1) before applying this convention.

---

## 8. Platform-Side Changes Required

These issues **cannot be fixed in card-factory alone**. They require changes to the Pleyr web application codebase. They are documented here so the card-factory team can (a) understand the constraints they're working within, (b) file the appropriate issues, and (c) plan print runs accordingly.

### 8.1 `getPhysicalCardRedirectURL()` crashes on null profile

> **⚠️ This is the critical blocker for printing QR codes on unclaimed cards.**

**Location:** `src/actions/cardOrderActions.tsx` → `getPhysicalCardRedirectURL()`

**Current behavior:** When someone scans a QR code (`/invite/<order_id>`), the handler looks up the order and its associated card. If `card.profile` is null, it throws an unhandled `Error('Card is not associated with a profile')`. This is not a `UserError` — it produces an opaque server error with no user-facing message.

**What it should do:** Instead of throwing, redirect to the claim flow:
```typescript
if (!order.card.profile) {
  // Card hasn't been claimed yet — redirect to claim page
  // so the scanned-card owner (or intended recipient) can
  // create an account and link their profile.
  return { url: `/claim-card/${Cards.unresolve(order.card)}` };
}
```

The `/claim-card/<card_id>` route and `claimCard()` action already exist in the codebase. They handle account creation, login, and setting `card.profile`. This single change makes every unclaimed-card QR code functional: instead of crashing, scanning routes the user to "claim this card and create your profile."

**Why this matters for card-factory:** Until this fix is deployed, every QR code printed for an `UNCLAIMED` card will produce a server error when scanned. The card-factory workflow can generate correct `invite/<order_id>` URLs today, but those URLs will fail at the destination. This is the one piece that requires coordination between the card-factory print pipeline and the platform engineering team.

**Recommended issue title:** `fix: handle null card.profile gracefully in QR code scan handler`

### 8.2 Parent-creates-card-for-kid links to wrong profile

**Location:** `src/actions/cardActions.tsx` → `savePlayerCard()` / `uploadPlayerCard()`

**Current behavior:** When a logged-in user with a profile creates a card via the card creator, `savePlayerCard()` always passes the creator's own `profileId` to `uploadPlayerCard()`. The card is inserted with `profile` set to the creator's profile. There is no mechanism to indicate "this card is for someone else."

**Impact:** A parent who creates a card for their child ends up with the card linked to the parent's profile. If they order physical copies, the QR code routes to the parent's profile, not the child's.

**What it should do (options):**
- **Option A (minimal):** Add a "this card is for someone else" toggle to the card creator. When selected, insert the card with `profile: null` and rely on the claim flow (§8.1) for the intended recipient to link it later.
- **Option B (more complete):** Add a "transfer card" action that lets a card owner reassign `card.profile` to a different profile. This would also support the case where a parent initially claims a card, then later wants to transfer it to their kid's newly created account.

**Why this matters for card-factory:** This is a product-level decision, not a bug per se. The card-factory workflow can detect `OWNER_MISMATCH` in Step 0 (see §3.2) and flag it for review, but it cannot fix the underlying data. Until the platform provides a transfer mechanism, these cards will have QR codes that work but route to the wrong person.

**Recommended issue title:** `feat: allow card creator to mark card as "for someone else" (skip profile link)`

### 8.3 No fulfillment status management in admin UI

**Current behavior:** The `physical_card_orders.fulfillment_status` column exists and supports values like `'pending'` and `'printed'`, but there is no admin UI for viewing pending orders or updating fulfillment status after printing. The card-factory operator must run raw SQL to query pending orders and update status post-run.

**What it should do:** An admin panel (or at minimum a protected API endpoint) should allow:
- Viewing all orders with `fulfillment_status = 'pending'`
- Bulk-updating `fulfillment_status` to `'printed'` or `'shipped'` with tracking info
- Exporting the order data needed by card-factory Step 0 as a CSV download

**Why this matters for card-factory:** Every print run currently starts and ends with manual SQL. This is error-prone and requires direct database access, which not all operators should have. An admin UI would also make it possible to automate the Step 0 data extraction entirely.

**Recommended issue title:** `feat: admin UI for physical card order fulfillment management`

---

## 9. Summary Table

### Priority 1 — Code fixes (prevent errors or silent failures)

| Script | Issue | Fix | Effort |
|--------|-------|-----|--------|
| All Python scripts | `sanitize_path()` doesn't expand `~` | Add `os.path.expanduser()` | Small |
| `png-to-pdf.py` | Duplicate bare-executing code blocks | Remove module-level code and commented-out old version | Small |
| `png-to-pdf.py` | Skips `.jpg` and `.jpeg` files | Add jpg/jpeg to file filter | Small |
| `batchProcessPlayersPhotoshop.jsx` | Skips `.jpg` and `.jpeg` files | Update `getFiles` filter | Small |
| `batchProcessPlayersPhotoshop.jsx` | `Resized_` prefix breaks downstream matching | Remove prefix from output filenames | Small |
| `saveTextLayersAsSVG.jsx` | "NoNumber" literal in filenames when jersey number is blank | Omit number from filename when blank | Small |
| `mergeSvgTextWithPlayerPhotos.jsx` | Brittle name matching on spaces vs hyphens | Normalize before comparison | Small |
| `mergeSvgTextWithPlayerPhotos.jsx` | No support for numberless PNG filenames | Add and test numberless pattern | Small |
| `rename_files.py` | `get_file_info()` lacks Pattern 7 (back card sequencing breaks) | Add Pattern 7 equivalent | Small |
| `combinePlayerCardBorderWithBackgrounds.jsx` | Only accepts `.pdf` border files, ignores SVGs | Update `getFiles` filter to include SVGs | Small |
| `combinePlayerCardBorderWithBackgrounds.jsx` | Border positioned off-canvas (wrong coordinate system) | Use artboard bounds for sizing and positioning (see §4.14) | Small |
| `generate_athletifi_db_queries.py` | Generates queries using obsolete profile-based QR URL scheme | Rewrite to use order IDs and `invite/<order_id>` URLs (see §4.15) | Medium |
| `process_qr_code_csv.py` | Hardcodes obsolete `athleti.fi/qr-code/` URL prefix | Change to `<baseUrl>/invite/` with order IDs (see §4.16) | Medium |
| `parse_filenames.py` | Output CSV assumes profile-based flow; lacks order ID mapping | Merge filename data with Step 0 order data (see §4.17) | Medium |

### Priority 2 — Automation (save significant time)

| Improvement | Effort |
|-------------|--------|
| Add CLI args to `merge-images-pdf.py` for non-interactive batch runs | Medium |
| Add CSV-driven per-card border mode to `combinePlayerCardBorderWithBackgrounds.jsx` | Medium |
| Generalize and commit `batchBorders.jsx`: replace hardcoded paths/colors with folder dialogs and auto-discovery (see §4.13) | Medium |
| Add a batch runner shell script for Step 5 that auto-discovers border-color subfolders | Small |
| Create a Step 0 prep script that parses SQL output and generates download commands, folder structure, and player CSV | Medium |
| Script the SVG-to-PDF border conversion (see §5.7) | Small |

### Priority 3 — Documentation (reduce confusion and manual improvisation)

| Section | Fix | Effort |
|---------|-----|--------|
| New Step 0 | SQL query (with profile status check), S3 download commands, name-mapping table (as example, not hardcoded), fulfillment update | Medium |
| §1.2 | Version-agnostic Photoshop path, note `sudo` may be needed | Small |
| §1.3 | Promote JSX batch script as primary; action as optional | Small |
| §2.2 | Guidance for players with no jersey number | Small |
| §2.4 | "Load Variable Library…" terminology fix | Small |
| §3.1 | Concrete naming chain example (CSV → SVG → PNG) with generalization notes | Small |
| §4 | Prerequisite check for Python deps; update `requirements.txt` | Small |
| §4 | Border-color folder grouping for background PDF output | Small |
| §5–6 | Describe border-color grouping workflow with auto-discovery patterns; document `printf` piping and `batchBorders.jsx` | Medium |
| §5.3 | Document Pattern 7 filename convention | Small |
| §6.1 | Update border file path to accommodate flat and subfolder structures | Small |
| New pre-step | SVG → PDF border conversion process | Small |
| General | Generalize "edition" language to "border group / variant" | Medium |
| `back-card-generation.md` Steps 3–4 | Rewrite for order-based QR URL scheme; remove all `athleti.fi/qr-code/` references (see §5.15) | Medium |
| `back-card-generation.md` new subsection | Document QR code scan-time behavior and public/private modes (see §5.16) | Small |
| `back-card-generation.md` §1.1 and §2.1 | Update for new border paths, naming, and background-agnostic language | Medium |
| `assets/csv/` | Add numberless player examples to example CSVs | Small |
| New template | Create `card-generation-runbook-template.md` with placeholders for batch-specific values | Medium |

### Priority 4 — Asset structure

| Item | Effort |
|------|--------|
| Standardize border folder convention (flat vs. subfolder); apply to all clubs | Small |
| Create `assets/borders/generic/print_borders/` for non-club-specific borders | Small |
| Document `bg-` prefix as the standard naming convention for all new backgrounds | Small |
| Document both folder conventions in README until migration is complete | Small |

### Priority 5 — Platform-side changes (requires web app engineering team)

| Issue | Impact on card-factory | Effort | Blocking? |
|-------|----------------------|--------|-----------|
| `getPhysicalCardRedirectURL()` crashes on null `card.profile` (§8.1) | QR codes for unclaimed cards produce server errors when scanned | Small | **Yes** — blocks printing QR codes for any order where the card hasn't been claimed |
| No "this card is for someone else" toggle in card creator (§8.2) | Cards created by parents for kids get linked to the wrong profile; QR routes to parent | Medium | No — QR technically works, just routes to wrong person |
| No admin UI for fulfillment management (§8.3) | Every print run requires direct database access for Step 0 query and post-run status update | Medium | No — manual SQL works, but is error-prone and limits who can run a batch |
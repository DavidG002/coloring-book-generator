# Coloring Book Page Generator

A Python tool to generate simple, print-ready coloring book pages for children (ages 3–10) using OpenAI's `gpt-image-2` image generation API. Designed for high-volume batch generation with multilingual publishing support.

## Features

- Generates small, optimized PNG files (~5–15 KB per image)
- Outputs images sized for A4 (595×842 pixels)
- Automatic pose and expression variation — every image in a batch looks different
- Supports multiple categories with separate prompt and variation files
- Automatic unique variation numbering (`subject_v001.png`, `subject_v002.png`, ...)
- Multilingual publishing pipeline with SEO-ready filenames and WordPress manifest CSV
- Command-line control with dry-run preview and safety confirmation for large batches

## Project Structure

```text
coloring-book-generator/
├── generate_pages.py        # Image generation script
├── publish_translations.py  # Multilingual publishing script
├── categories/              # One .txt file per category listing subjects
├── prompts/                 # Category-specific prompts + variation poses
├── translations/            # Per-category, per-language translation files
│   └── dinosaurs/
│       └── he.json          # Hebrew translation example
├── output/                  # Generated working images (gitignored)
├── publish/                 # Ready-to-upload translated images (gitignored)
│   └── he/
│       └── dinosaurs/       # Hebrew publish folder (created automatically)
├── venv/                    # Virtual environment (gitignored)
├── .env                     # API key (gitignored)
└── README.md
```

## Setup

1. Clone the repo and activate a virtual environment:
   ```bash
   git clone https://github.com/yourname/coloring-book-generator.git
   cd coloring-book-generator
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

The `output/` and `publish/` folders are already present from the clone — no manual setup needed. All subfolders are created automatically when you run the scripts.

---

## Generating Images

### Basic usage

```bash
# Preview what will be generated without spending API budget (always do this first)
python generate_pages.py --category dinosaurs --new-variations 5 --dry-run

# Generate 1 image per dinosaur in the list (10 dinosaurs = 10 images)
python generate_pages.py --category dinosaurs --new-variations 1

# Generate 2 images per dinosaur (10 dinosaurs = 20 images)
python generate_pages.py --category dinosaurs --new-variations 2

# Generate 5 variations of a single subject
python generate_pages.py --category dinosaurs --subject "T-Rex" --new-variations 5

# Limit total images in a run
python generate_pages.py --category dinosaurs --new-variations 3 --max-images 10
```

> Any run over 15 images will ask for confirmation before starting.

### Recommended batch sizes

| Goal | Command |
|---|---|
| Test a new category | `--new-variations 1 --dry-run` first, then 1 run |
| Daily content batch | `--new-variations 2`, split across categories |
| Large volume | Max 50–70 per run; split into multiple runs for easier quality review |

---

## Image Size and Positioning

The subject is scaled to **50% of the canvas height** by default, centered on a white A4 canvas. This is controlled by one line in `generate_pages.py`:

```python
max_subject_size = int(canvas_height * 0.50)
```

Increase the percentage to make the subject larger (less white margin), decrease it for more breathing room. A range of `0.55`–`0.70` works well for most subjects. Anything above that risks the subject feeling cropped rather than intentionally placed.

**Note:** Changing this value affects new generations only — already-generated images are not affected.

---

## Prompt Files and Variation System

Each category has a prompt file in `prompts/` that controls both the visual style and the pose/expression variety across a batch.

### Prompt file format

```text
Simple black and white coloring page for children ages 3 to 10.
Large dinosaur as the main subject with clean black outlines.
...rest of style instructions...

VARIATIONS:
facing left, full body side view, walking pose, curious expression
facing right, full body side view, roaring with mouth wide open, excited
front-facing, sitting down, big friendly smile, arms out
three-quarter view from above, looking up at the sky, surprised expression
full body, running pose, leaning forward with speed, determined look
...
```

Everything **above** `VARIATIONS:` is the base style prompt sent to the model.  
Everything **below** `VARIATIONS:` is a list of pose/expression modifiers — one per line.

The script cycles through the variations list automatically by variation number, so a batch of 5 images will each get a distinct pose without any manual tracking. The list can be any length; it wraps around if you generate more images than there are entries.

### Variation modifiers by category type

Modifiers should match what makes sense for the subject:

- **Animals / characters** → poses, expressions, angles (`sitting`, `roaring`, `waving`)
- **Vehicles / objects** → viewpoints, context (`front three-quarter view`, `side view on a road`, `aerial top-down view`)

If a prompt file has no `VARIATIONS:` section, the script falls back to a built-in set of animal/character poses.

### Adding a new category

1. Create the subjects list:
   ```bash
   touch categories/vehicles.txt
   ```
   Add one subject per line:
   ```text
   Car
   Truck
   Airplane
   Boat
   ```

2. Create a matching prompt file:
   ```bash
   touch prompts/vehicles.txt
   ```
   Write your base prompt, then add a `VARIATIONS:` section with viewpoints that make sense for that category. See `prompts/dinosaurs.txt` as a reference.

---

## Publishing (Multilingual)

After generating images, run the publishing script to produce SEO-ready, translated copies with Hebrew (or other language) filenames and a WordPress import manifest.

### Flow

```
generate_pages.py  →  output/{category}/subject_v001.png   (English working files)
        ↓
publish_translations.py  →  publish/he/{category}/דף-צביעה-דינוזאור-טי-רקס-1.png
                         →  publish/he/{category}/manifest.csv
```

The original English files in `output/` are never touched or moved.

### Running the publish script

```bash
# Preview translated filenames before copying anything
python publish_translations.py --lang he --category dinosaurs --dry-run

# Publish all dinosaurs images in Hebrew
python publish_translations.py --lang he --category dinosaurs

# Publish all categories at once
python publish_translations.py --lang he
```

### The manifest CSV

Each publish folder gets a `manifest.csv` with one row per image:

| Column | Description |
|---|---|
| `filename` | Translated Hebrew filename |
| `alt_text` | SEO alt text (`דף צביעה דינוזאור טי רקס להדפסה חינם`) |
| `title` | Image title attribute |
| `category_en` / `subject_en` | Original English values for reference |
| `source_path` | Path to the English working file |

The manifest is rebuilt in full on every run — it always reflects the current complete state of the publish folder, not just the newest additions. Re-running after adding new images is safe; existing files are overwritten with identical content.

### Uploading to WordPress

Once the publish script has run, the `publish/he/{category}/` folder contains everything needed to upload to WordPress. There are two ways to do this depending on your preference.

**Option A — Manual upload (simplest)**

Open `manifest.csv` in Excel or Google Sheets alongside your WordPress Media Library. For each row:

1. Upload the image file from `publish/he/{category}/` to the WordPress Media Library
2. Once uploaded, click the image in the Media Library and fill in:
   - **Alt Text** → paste from the `alt_text` column
   - **Title** → paste from the `title` column
3. Attach the image to the relevant page or post

This works well for smaller batches and requires no plugins.

**Option B — Bulk import with WP All Import (recommended for large batches)**

[WP All Import](https://www.wpallimport.com/) is a WordPress plugin that can import images and their metadata in bulk from a CSV file.

1. Install and activate the **WP All Import** plugin on your WordPress site
2. Upload all the images from `publish/he/{category}/` to your Media Library first (you can drag and drop multiple files at once in the Media Library)
3. In WP All Import, create a new import using the `manifest.csv` file
4. Map the CSV columns to WordPress fields:
   - `filename` → identifies the media file
   - `alt_text` → Image Alt Text
   - `title` → Image Title
5. Run the import

> **Tip:** The `manifest.csv` uses UTF-8 encoding with a BOM so Hebrew characters display correctly when opening in Excel. If characters look broken, make sure Excel is reading it as UTF-8.

### Before adding a new category — check the live site first

Before creating a new translation JSON, always check the target website for an existing coloring page in a similar category. This ensures your filenames, alt text, and category names match the phrasing the site already uses — which is what search engines already associate with the site.

**What to look for on the site:**

1. **URL slug** — open an existing coloring page and look at the URL. For example:
   
   This tells you the exact Hebrew phrasing for that category in filenames

2. **Page title and headings** — the H1 or page title usually contains the canonical phrasing, e.g. 

3. **Image alt text** — right-click an existing coloring page image → Inspect, and check the  attribute. This is the exact format to replicate in your 

**Then build your JSON to match:**

If the site uses  in URLs and  in alt text, your  should reflect that exactly — not a guess at what sounds right.

> This step takes 5 minutes and makes a real difference to SEO. Do it before writing the JSON, not after.

---

### Adding a new language

1. Create a translation file for each category:
   ```bash
   touch translations/dinosaurs/es.json
   ```

2. Follow the same structure as `translations/dinosaurs/he.json`:
   ```json
   {
     "_category": "dinosaurio",
     "_filename_template": "dibujo-para-colorear-{category}-{item}",
     "_alt_template": "dibujo para colorear {category} {item} gratis",
     "_title_template": "dibujo para colorear {category} {item}",
     "items": {
       "T-Rex": "t-rex",
       "Triceratops": "triceratops"
     }
   }
   ```
   > **Tip:** Before finalising the filename template for a new language, check how real competitor sites in that market phrase their coloring page URLs — matching their phrasing improves search ranking.

3. Run the publish script with the new language code:
   ```bash
   python publish_translations.py --lang es --category dinosaurs
   ```

No changes to `generate_pages.py` or `publish_translations.py` are needed.

---

## Cost Reference

All generation uses `gpt-image-2` at `quality="low"`, which is the cheapest available tier.

| Volume | Approximate cost |
|---|---|
| 1 image | ~$0.007 |
| 100 images | ~$0.70 |
| 1,000 images | ~$7.00 |

---

## License

MIT

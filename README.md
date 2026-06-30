Markdown
# Coloring Book Page Generator

A Python tool to generate simple, minimal coloring book pages for children (ages 3–10) using OpenAI's image generation.

## Features

- Generates very small PNG files (~4–15 KB)
- Outputs images sized for A4 (595×842 pixels at 96 DPI)
- Supports multiple categories with separate prompt files
- Automatic unique variation numbering (`subject_v001.png`, `subject_v002.png`)
- Command-line control with safety features

## Project Structure

```text
coloring-book-generator/
├── generate_pages.py
├── categories/          # One .txt file per category
├── prompts/             # Category-specific prompts (optional)
├── output/              # Generated images (gitignored)
├── venv/                # Virtual environment (gitignored)
├── .env                 # API key (gitignored)
└── README.md
Setup
Create and activate a virtual environment:

Bash
python -m venv venv
source venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Create a .env file with your OpenAI API key:

Code snippet
OPENAI_API_KEY=sk-proj-your-key-here
Usage
Generate Images
Bash
# Generate 2 new unique T-Rex images
python generate_pages.py --category dinosaurs --subject "T-Rex" --new-variations 2

# Generate up to 50 images from the dinosaurs category
python generate_pages.py --category dinosaurs --new-variations 3 --max-images 50

# Preview before generating (recommended)
python generate_pages.py --category dinosaurs --new-variations 3 --dry-run
Recommended Limits
Normal daily work: Use --max-images 50

Building fast: Run 2 batches of 50 per day

Large volume: Maximum 70–80 images per run

New category: Always start with --dry-run first

Tip: Even if cost is not an issue, splitting large amounts into smaller batches makes it easier to check quality.

Creating a New Category
Create a new file in the categories/ folder:

Bash
touch categories/vehicles.txt
Add one subject per line inside vehicles.txt:

Plaintext
Car
Truck
Airplane
Boat
(Optional but recommended) Create a matching prompt file:

Bash
touch prompts/vehicles.txt
How It Works
Images are generated at high resolution, then resized and centered on a 595×842 canvas (A4 at 96 DPI).

Uses 1-bit thresholding to keep file sizes very small.

Each run automatically continues from the next variation number.

Category-specific prompts are loaded from the prompts/ folder when available.

Notes
You can adjust BW_THRESHOLD in the script if lines appear too thick or jagged.

The output/ folder is gitignored by default.

License
MIT
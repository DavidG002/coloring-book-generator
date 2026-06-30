# Coloring Book Page Generator

A Python tool to generate simple, minimal coloring book pages for children (ages 3–10) using OpenAI's image generation.

## Features

- Generates very small PNG files (~4–15 KB)
- Outputs images sized for A4 (595×842 pixels at 96 DPI)
- Supports multiple categories with separate prompt files
- Automatic unique variation numbering (`subject_v001.png`, `subject_v002.png`...)
- Command-line control with safety features

## Project Structure
coloring-book-generator/
├── generate_pages.py
├── categories/          # One .txt file per category
├── prompts/             # Category-specific prompts (optional)
├── output/              # Generated images (gitignored)
├── venv/                # Virtual environment (gitignored)
├── .env                 # API key (gitignored)
└── README.md


## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Create a .env file with your OpenAI API key:
envOPENAI_API_KEY=sk-proj-your-key-here

Usage

Generate Images
Bash# Generate 2 new unique T-Rex images
python generate_pages.py --category dinosaurs --subject "T-Rex" --new-variations 2

# Generate up to 50 images from the dinosaurs category
python generate_pages.py --category dinosaurs --new-variations 3 --max-images 50

# Preview before generating (recommended)
python generate_pages.py --category dinosaurs --new-variations 3 --dry-run
Recommended Limits


Daily GoalRecommended ApproachCommand ExampleNotesNormal daily work30 – 50 images per run--max-images 50ComfortableBuilding fast2 × 50 images per dayRun twice with --max-images 50Good balanceLarge batchesMax 70–80 images per run--max-images 70AcceptableFirst time new categoryAlways use --dry-run first--dry-runSafety
Tip: Even if cost is not an issue, splitting large amounts into multiple runs makes it easier to check quality.
Creating a New Category

Create a new file in the categories/ folder:Bashtouch categories/vehicles.txt
Add one subject per line:txtCar
Truck
Airplane
Boat
(Optional but recommended) Create a matching prompt file:Bashtouch prompts/vehicles.txt

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

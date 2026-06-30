# Coloring Book Page Generator

A Python tool to generate simple, minimal coloring book pages for children (ages 3–10) using OpenAI's image generation.

## Features

- Generates very small PNG files (~4–15 KB)
- Outputs images sized for A4 (595×842 pixels at 96 DPI)
- Supports multiple categories with separate prompt files
- Automatic unique variation numbering (`subject_v001.png`, `subject_v002.png`...)
- Command-line control for daily generation
- Safety features (`--max-images`, `--dry-run`, confirmation prompts)

## Project Structure
coloring-book-generator/
├── generate_pages.py          # Main generation script
├── categories/                # One .txt file per category
│   └── dinosaurs.txt
├── prompts/                   # Category-specific prompts
│   └── dinosaurs.txt
├── output/                    # Generated images (gitignored)
├── venv/                      # Virtual environment (gitignored)
├── .env                       # API key (gitignored)
├── .gitignore
└── README.md
text## Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate

Install dependencies:Bashpip install -r requirements.txt
Create a .env file with your OpenAI API key:envOPENAI_API_KEY=sk-proj-your-key-here

Usage
Basic Examples
Bash# Generate 2 new unique T-Rex variations
python generate_pages.py --category dinosaurs --subject "T-Rex" --new-variations 2

# Generate maximum 10 images from the dinosaurs category
python generate_pages.py --category dinosaurs --new-variations 2 --max-images 10

# Preview what would be generated (dry run)
python generate_pages.py --category dinosaurs --new-variations 2 --dry-run

# Generate from all categories
python generate_pages.py
Useful Flags



































FlagDescriptionExample--categoryGenerate from a specific category--category dinosaurs--subjectGenerate only for one subject--subject "T-Rex"--new-variationsNumber of new unique images per subject--new-variations 3--max-imagesHard limit on total images generated--max-images 15--dry-runPreview without generating--dry-run
How It Works

Images are generated at 1024×1024 then resized and centered on a 595×842 canvas (A4 at 96 DPI).
Uses 1-bit thresholding for extremely small file sizes.
Each new run automatically continues from the next variation number.
Category-specific prompts are loaded from the prompts/ folder when available.

Notes

File sizes are kept very small (~4–15 KB) for easy web hosting.
You can adjust BW_THRESHOLD in the script if lines appear too thick or jagged.
The output/ folder is gitignored by default.

License
MIT

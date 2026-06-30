import os
import base64
import time
import argparse
import glob
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm
from PIL import Image
import io

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ====================== CONFIG ======================
CATEGORIES_DIR = "categories"
OUTPUT_DIR = "output"
PROMPTS_DIR = "prompts"

# --- PNG size/quality tuning ---
# GPT-image output has faint compression noise scattered across the whole
# canvas (not just at line edges), which is invisible to the eye but hurts
# PNG compression badly. We snap near-white and near-black pixels to pure
# white/black to kill that noise, while leaving genuine anti-aliasing near
# line edges (values between the two thresholds) untouched so curves stay
# smooth instead of jagged.
WHITE_CLEAN_THRESHOLD = 245  # pixels brighter than this -> pure white (255)
BLACK_CLEAN_THRESHOLD = 10   # pixels darker than this -> pure black (0)

# Number of colors in the final adaptive palette. 8 keeps a thin smooth
# anti-aliased edge around lines while staying small. Drop to 4 for an even
# smaller file with slightly less edge smoothness.
PALETTE_COLORS = 8

DEFAULT_BASE_PROMPT = (
    "Simple black and white coloring page for children ages 3 to 10. "
    "Large main subject that fills most of the page with thick bold black outlines. "
    "Very minimal details and clean shapes that are easy to color. "
    "Large centered object with lots of white space around it. "
    "Minimal or no background. Clean white background. "
    "Simple friendly cartoon style, not overly babyish. "
    "High contrast thick lines, suitable for young children. "
    "Print-ready line art. "
)


def get_category_prompt(category_name):
    prompt_path = os.path.join(PROMPTS_DIR, f"{category_name}.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return DEFAULT_BASE_PROMPT


def get_subjects_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_next_variation_number(category_dir, subject):
    """Find the next available variation number for PNG files."""
    pattern = os.path.join(category_dir, f"{subject.lower().replace(' ', '_')}_v*.png")
    existing_files = glob.glob(pattern)

    if not existing_files:
        return 1

    numbers = []
    for file in existing_files:
        try:
            num = int(file.split('_v')[-1].replace('.png', ''))
            numbers.append(num)
        except:
            continue
    return max(numbers) + 1 if numbers else 1


def generate_image(prompt, output_path):
    try:
        response = client.images.generate(
            model="gpt-image-2",
            prompt=prompt,
            size="1024x1024",
            quality="low",
        )
        image_b64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)

        image = Image.open(io.BytesIO(image_bytes))

        # Target A4 canvas (595x842)
        canvas_width = 595
        canvas_height = 842

        # Keep subject at 50%
        max_subject_size = int(canvas_height * 0.70)
        image.thumbnail((max_subject_size, max_subject_size), Image.LANCZOS)

        # --- Noise cleanup + small palette (smooth edges, small file) ---
        # Snap near-white/near-black pixels to pure white/black to kill the
        # invisible compression noise that bloats PNG size, but leave the
        # real anti-aliasing band right around line edges untouched so
        # curves stay smooth instead of jagged like a hard 1-bit threshold.
        gray = image.convert("L")
        clean_lut = [
            0 if v < BLACK_CLEAN_THRESHOLD else (255 if v > WHITE_CLEAN_THRESHOLD else v)
            for v in range(256)
        ]
        cleaned_subject = gray.point(clean_lut, mode="L")

        # Paste onto a clean white A4 canvas (still grayscale at this point)
        canvas = Image.new("L", (canvas_width, canvas_height), 255)
        x = (canvas_width - cleaned_subject.width) // 2
        y = (canvas_height - cleaned_subject.height) // 2
        canvas.paste(cleaned_subject, (x, y))

        # Quantize to a small adaptive palette with NO dithering. Dithering
        # would reintroduce scattered noise across flat areas and bloat the
        # file right back up.
        new_image = canvas.convert(
            "P", palette=Image.ADAPTIVE, colors=PALETTE_COLORS, dither=Image.NONE
        )

        new_image.save(
            output_path,
            "PNG",
            optimize=True,
            compress_level=9,
        )

        return True
    except Exception as e:
        print(f"\nError generating image: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Daily coloring book image generator (PNG)")
    parser.add_argument("--category", type=str, help="Category to generate from")
    parser.add_argument("--subject", type=str, help="Generate only for this specific subject")
    parser.add_argument("--new-variations", type=int, default=1,
                        help="How many new unique images per subject")
    parser.add_argument("--max-images", type=int, default=None,
                        help="Maximum number of images to generate")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what will be generated")

    args = parser.parse_args()

    if args.category:
        category_files = [f"{args.category}.txt"]
    else:
        category_files = [f for f in os.listdir(CATEGORIES_DIR) if f.endswith(".txt")]

    tasks = []

    for cat_file in category_files:
        category_name = os.path.splitext(cat_file)[0]
        subjects = get_subjects_from_file(os.path.join(CATEGORIES_DIR, cat_file))

        if args.subject:
            subjects = [s for s in subjects if s.lower() == args.subject.lower()]

        category_output_dir = os.path.join(OUTPUT_DIR, category_name)
        os.makedirs(category_output_dir, exist_ok=True)

        base_prompt = get_category_prompt(category_name)

        for subject in subjects:
            next_var = get_next_variation_number(category_output_dir, subject)
            for i in range(args.new_variations):
                variation_num = next_var + i
                tasks.append((category_name, subject, variation_num, base_prompt))

    if args.max_images:
        tasks = tasks[:args.max_images]

    print(f"\nPlanned generations: {len(tasks)}")

    if args.dry_run:
        for cat, subj, var_num, _ in tasks:
            print(f"  → {cat} / {subj}_v{var_num:03d}.png")
        print("\nDry run complete.")
        return

    if len(tasks) > 15:
        confirm = input(f"Generate {len(tasks)} images? (y/n): ")
        if confirm.lower() != "y":
            print("Cancelled.")
            return

    for category_name, subject, variation_num, base_prompt in tqdm(tasks, desc="Generating"):
        category_output_dir = os.path.join(OUTPUT_DIR, category_name)
        os.makedirs(category_output_dir, exist_ok=True)

        filename = f"{subject.lower().replace(' ', '_')}_v{variation_num:03d}.png"
        output_path = os.path.join(category_output_dir, filename)

        prompt = base_prompt + f" Cute {subject}."
        success = generate_image(prompt, output_path)

        if success:
            time.sleep(1.2)
        else:
            time.sleep(5)

    print(f"\n✅ Done! Generated {len(tasks)} new PNG images.")


if __name__ == "__main__":
    main()
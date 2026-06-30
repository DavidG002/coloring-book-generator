"""
publish_translations.py

Takes the English working files produced by generate_pages.py
(output/{category}/{subject}_v{NNN}.png) and produces a translated,
publish-ready copy for a given language, following that language's
on-site naming convention.

This does NOT touch or move the original English files in output/ —
those stay untouched as your internal working copies.

For each language, this creates:
    publish/{lang}/{category}/{translated-filename}.png
    publish/{lang}/{category}/manifest.csv

The manifest.csv has one row per image with the filename, alt text,
title, and the original English subject/category — enough to import
into WordPress (e.g. via WP All Import) or to use as an upload
checklist.

Usage:
    python publish_translations.py --lang he --category dinosaurs
    python publish_translations.py --lang he                # all categories
    python publish_translations.py --lang he --dry-run       # preview only

Adding a new language later (e.g. Spanish):
    1. Create translations/{category}/es.json for each category, following
       the same structure as the he.json files (see TRANSLATION FILE FORMAT
       below).
    2. Run: python publish_translations.py --lang es
    No changes needed to this script or to generate_pages.py.

TRANSLATION FILE FORMAT (translations/{category}/{lang}.json):
{
  "_category": "<category name in this language>",
  "_filename_template": "<template using {category} and {item}>",
  "_alt_template": "<template using {category} and {item}>",
  "_title_template": "<template using {category} and {item}>",
  "items": {
    "<English subject as it appears in categories/*.txt>": "<translated subject>",
    ...
  }
}
"""

import os
import re
import csv
import json
import glob
import shutil
import argparse

CATEGORIES_DIR = "categories"
OUTPUT_DIR = "output"
TRANSLATIONS_DIR = "translations"
PUBLISH_DIR = "publish"


def load_translation(category, lang):
    path = os.path.join(TRANSLATIONS_DIR, category, f"{lang}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def slugify(text, lang):
    """
    Turn translated text into a clean, URL-safe filename fragment.
    Keeps letters (incl. non-Latin scripts like Hebrew), digits, and
    hyphens; spaces become hyphens; everything else is dropped.
    """
    text = text.strip()
    text = re.sub(r"\s+", "-", text)
    # Keep word characters (Unicode-aware, so Hebrew/Spanish letters survive)
    # plus hyphens; drop punctuation like apostrophes, quotes, etc.
    text = re.sub(r"[^\w\-]", "", text, flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def get_subjects(category):
    path = os.path.join(CATEGORIES_DIR, f"{category}.txt")
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_variation_files(category, subject):
    """All generated PNG variations for one subject, in order."""
    category_dir = os.path.join(OUTPUT_DIR, category)
    pattern = os.path.join(category_dir, f"{subject.lower().replace(' ', '_')}_v*.png")
    return sorted(glob.glob(pattern))


def variation_number(filepath):
    match = re.search(r"_v(\d+)\.png$", filepath)
    return int(match.group(1)) if match else 0


def publish_category(category, lang, dry_run=False):
    translation = load_translation(category, lang)
    if translation is None:
        print(f"  ⚠ No {lang}.json translation file for '{category}', skipping.")
        return []

    category_he = translation["_category"]
    filename_template = translation["_filename_template"]
    alt_template = translation["_alt_template"]
    title_template = translation["_title_template"]
    items = translation["items"]

    subjects = get_subjects(category)
    publish_category_dir = os.path.join(PUBLISH_DIR, lang, category)
    if not dry_run:
        os.makedirs(publish_category_dir, exist_ok=True)

    rows = []

    for subject in subjects:
        translated_subject = items.get(subject)
        if not translated_subject:
            print(f"  ⚠ No '{lang}' translation for subject '{subject}' in '{category}', skipping.")
            continue

        files = get_variation_files(category, subject)
        if not files:
            continue

        base_name = filename_template.format(category=category_he, item=translated_subject)
        base_slug = slugify(base_name, lang)
        alt_text = alt_template.format(category=category_he, item=translated_subject)
        title_text = title_template.format(category=category_he, item=translated_subject)

        for source_path in files:
            # Always number, using the underlying v001/v012/etc. number from
            # the working file. This keeps the published filename stable
            # forever once it's live — a later batch adding more variations
            # of the same subject must never rename an already-published file.
            num = variation_number(source_path)
            target_filename = f"{base_slug}-{num}.png"
            target_path = os.path.join(publish_category_dir, target_filename)

            if dry_run:
                print(f"  → {source_path}  =>  {target_path}")
            else:
                shutil.copy2(source_path, target_path)

            rows.append({
                "filename": target_filename,
                "alt_text": alt_text,
                "title": title_text,
                "category_en": category,
                "category_translated": category_he,
                "subject_en": subject,
                "subject_translated": translated_subject,
                "source_path": source_path,
            })

    if not dry_run and rows:
        manifest_path = os.path.join(publish_category_dir, "manifest.csv")
        with open(manifest_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"  ✓ Wrote {manifest_path} ({len(rows)} rows)")

    return rows


def main():
    parser = argparse.ArgumentParser(description="Publish translated, SEO-ready coloring page copies.")
    parser.add_argument("--lang", required=True, help="Language code, e.g. 'he', matching translations/*/{lang}.json")
    parser.add_argument("--category", type=str, help="Limit to a single category (default: all categories with a translation file for this language)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without copying files or writing the manifest")
    args = parser.parse_args()

    if args.category:
        categories = [args.category]
    else:
        categories = [
            name for name in os.listdir(TRANSLATIONS_DIR)
            if os.path.isdir(os.path.join(TRANSLATIONS_DIR, name))
        ]

    total = 0
    for category in categories:
        print(f"\n[{category}] -> lang={args.lang}")
        rows = publish_category(category, args.lang, dry_run=args.dry_run)
        total += len(rows)

    print(f"\n{'Would publish' if args.dry_run else 'Published'} {total} image(s) total for lang='{args.lang}'.")


if __name__ == "__main__":
    main()

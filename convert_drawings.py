# convert_drawings.py

import os
from pptx import Presentation
from pdf2image import convert_from_path
from PIL import Image

INPUT_PPTX = "Copy of Vex Engineering Notebook 8780E '25 - '26.pptx"
OUTPUT_DIR = "images"
DPI = 300  # quality

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 1: Convert .pptx to PDF pages, then to images
def pptx_to_images(pptx_path):
    pdf_path = pptx_path.replace(".pptx", ".pdf")

    # Convert pptx to pdf (via LibreOffice or manually saved in PowerPoint)
    print("👉 First, manually convert your PPTX to PDF (e.g. in PowerPoint: File > Save As > PDF).")
    print("Then set the PDF path here and rerun the script.")
    exit(1)

# Step 2: Extract drawings from slide images
def extract_regions(image, slide_index):
    # Example split: 2 rows × 3 columns
    slide_width, slide_height = image.size
    rows = 2
    cols = 3

    box_width = slide_width // cols
    box_height = slide_height // rows

    regions = []
    count = 1
    for row in range(rows):
        for col in range(cols):
            left = col * box_width
            top = row * box_height
            right = left + box_width
            bottom = top + box_height
            cropped = image.crop((left, top, right, bottom))
            filename = f"{OUTPUT_DIR}/slide{slide_index+1}_img{count}.png"
            cropped.save(filename)
            print(f"✅ Saved: {filename}")
            count += 1

def main():
    slides = convert_from_path("Copy of Vex Engineering Notebook 8780E '25 - '26.pdf", dpi=DPI)
    for i, slide_image in enumerate(slides):
        extract_regions(slide_image, i)

if __name__ == "__main__":
    main()

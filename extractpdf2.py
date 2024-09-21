#!/usr/bin/python
import sys
import os
import time


def create_extract_directory(file_path):
    # Extract the base name without extension
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    dir_name = os.path.dirname(file_path)
    # Append the suffix
    new_dir_name = os.path.join(dir_name, f"{base_name}_extract")
    # Create the directory
    os.makedirs(new_dir_name, exist_ok=True)
    return new_dir_name


import re

import fitz  # PyMuPDF
import io
from PIL import Image


def extract_jpg_from_pdf(pdf_path, output_folder):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Iterate through the pages
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        image_list = page.get_images(full=True)
        
        # Print the number of images found in this page
        print(f"[INFO] Found {len(image_list)} images on page {page_number + 1}")
        
        # Iterate through the images
        for img_index, img in enumerate(image_list):
            # Extract the image bytes
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            
            print(f"[INFO] Extracted image {img_index + 1} with extension: {image_ext}")
            
            # Only save if the image is in JPG format
            if image_ext == "jpeg":
                image_name = f"page_{page_number + 1}_img_{img_index + 1}.jpg"
                image_path = f"{output_folder}/{image_name}"
                image.save(image_path)
                print(f"[INFO] Saved image: {image_path}")


def main():
    filename = sys.argv[1]

    
    extract_dir = create_extract_directory(filename)
    
    extract_jpg_from_pdf(filename, extract_dir)
    
    sys.exit(0)
    


if __name__ == '__main__':
    main()

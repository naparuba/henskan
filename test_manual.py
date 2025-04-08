import os
import shutil

from PIL import ImageDraw
from PIL import ImageFont

from henskan.archive_pdf import ArchivePDF
from henskan.image import EReaderData, convert_image, save_image
from henskan.parameters import parameters

chapter_name = 'test_title'
parameters.set_output_directory('./test_out')
parameters.set_title('test_title')
parameters.add_chapter(chapter_name)

parameters.set_device('Kobo Elipsa 2E', 13)

directory = parameters.get_output_directory()
book_path = os.path.join(directory, parameters.get_title())
if not os.path.isdir(book_path):
    os.makedirs(book_path)
device = parameters.get_device()
output_format = EReaderData.get_archive_format(device)

archive = ArchivePDF(book_path, 'test_title', 'Kobo Elipsa 2E')


def _add_image_block_text(image, text):
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    
    # Define the font and color
    font = ImageFont.truetype("arial.ttf", 36)  # Adjust the font path and size as needed
    text_color = "black"
    
    # Calculate text position for top-middle
    
    position = ((image.width) / 2, 10)  # Adjust the y-coordinate as needed
    
    # Draw the text
    draw.text(position, text, fill=text_color, font=font)
    
    # Return the modified image
    return image


# IN: from 1 to 27
for in_idx in range(1, 28):
    print(f'######### In image: {in_idx}')
    img_src = f'./test_in/img{in_idx}.jpg'
    
    # Source image
    target = os.path.join(book_path, f'img{in_idx}_src.jpg')
    shutil.copy(img_src, target)
    archive.add_chapter('Source Image')
    archive.add(target)
    
    # 1: Full
    target = os.path.join(book_path, f'img{in_idx}_full.jpg')
    converted_images = convert_image(img_src)
    img = _add_image_block_text(converted_images[0], 'All')
    save_image(img, target)
    archive.add_chapter('All')
    archive.add(target)
    
    # 2: split
    
    # Left
    converted_images = convert_image(img_src, split_left=True)
    target = os.path.join(book_path, f'img{in_idx}_left.jpg')
    img = _add_image_block_text(converted_images[0], 'Split left')
    save_image(img, target)
    archive.add_chapter('All')
    archive.add(target)
    
    # Right
    converted_images = convert_image(img_src, split_right=True)
    target = os.path.join(book_path, f'img{in_idx}_right.jpg')
    img = _add_image_block_text(converted_images[0], 'Split Right')
    save_image(img, target)
    archive.add_chapter('All')
    archive.add(target)

archive.close()
print(f'Finish processing {book_path}')

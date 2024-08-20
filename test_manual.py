import os
import shutil

from PIL import ImageDraw
from PIL import ImageFont


from henskan.archive_pdf import ArchivePDF
from henskan.image import EReaderData, convert_image, save_image
from henskan.parameters import parameters

img_src = './test_in/img1.jpg'

chapter_name = 'test_title'

parameters.set_output_directory('./test_out')
parameters.set_title('test_title')
parameters.add_chapter(chapter_name)
parameters.add_image(img_src, chapter_name)
parameters.set_device('Kobo Elipsa 2E', 13)

directory = parameters.get_output_directory()
book_path = os.path.join(directory, parameters.get_title())
if not os.path.isdir(book_path):
    os.makedirs(book_path)
device = parameters.get_device()
output_format = EReaderData.get_archive_format(device)

archive = ArchivePDF(book_path, 'test_title', 'Kobo Elipsa 2E')


def _get_target(index):
    print(f'Processing {index}')
    return os.path.join(book_path, '%05d.png' % index)


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


# Source image
target = os.path.join(book_path, '00000.jpg')
shutil.copy(img_src, target)
archive.add_chapter('Source Image')
archive.add(target)



# 1: All
target = _get_target(1)
converted_images = convert_image(img_src)
img = _add_image_block_text(converted_images[0], 'All')
save_image(img, target)
archive.add_chapter('All')
archive.add(target)


# 2: just autocrop
target = _get_target(2)
converted_images = convert_image(img_src)
img = _add_image_block_text(converted_images[0], 'just autocrop')
save_image(img, target)
archive.add_chapter('Autocrop')
archive.add(target)

# 3: autocrop and resize
target = _get_target(3)
converted_images = convert_image(img_src)
img = _add_image_block_text(converted_images[0], 'autocrop and resize')
save_image(img, target)
archive.add_chapter('Autocrop and Resize')
archive.add(target)

# 4: autocrop and quantize
target = _get_target(4)
converted_images = convert_image(img_src)
img = _add_image_block_text(converted_images[0], 'autocrop and quantize')
save_image(img, target)
archive.add_chapter('Autocrop and Quantize')
archive.add(target)

archive.close()
print(f'Finish processing {book_path}')

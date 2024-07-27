import os.path
import time
from enum import Enum

import numpy as np

import cv2
# HACK weasyprint.HTML because it's imported by doctr but useless in our case, & buggy to install!
import sys

from PIL import ImageStat, ImageEnhance, Image, ImageDraw, ImageFont

from mangle.archive_pdf import ArchivePDF
from mangle.image import convert_image, save_image

vendors_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vendors')
if not os.path.exists(vendors_dir):
    print(f'Cannot find vendors directory: {vendors_dir}')
    sys.exit(2)
sys.path.insert(0, vendors_dir)
from weasyprint import HTML

a = HTML
del a
from doctr.models import detection_predictor

# LDFLAGS=-L/opt/homebrew/lib DYLD_LIBRARY_PATH=/opt/homebrew/lib python tt.py
# os.environ.get("DOCTR_CACHE_DIR", os.path.join(os.path.expanduser("~"), ".cache", "doctr")) => where to load models
doctr_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
if not os.path.exists(doctr_cache_dir):
    os.mkdir(doctr_cache_dir)
os.environ['DOCTR_CACHE_DIR'] = doctr_cache_dir

_g_predictor = None


def _get_predictor():
    global _g_predictor
    if _g_predictor is None:
        t0 = time.time()
        _g_predictor = detection_predictor('db_resnet50', pretrained=True, assume_straight_pages=False, preserve_aspect_ratio=True)
        print(f'Predictor loaded in {time.time() - t0:.2f} seconds')
    return _g_predictor


# predictor = detection_predictor('db_resnet50', pretrained=True, assume_straight_pages=False, preserve_aspect_ratio=True)

def _detect_text_positions(image_path, image_path_out):
    # type: (str, str) -> None
    img = Image.open(image_path)
    img_cv2 = cv2.imread(image_path)
    width, high = img.size
    
    # TODO: ratio can have problem if width is higher than high
    ratio = high / width
    img_np = np.array(img, dtype=np.uint8)
    
    _predictor = _get_predictor()
    t0 = time.time()
    out = _predictor([img_np])[0]
    print(f'{image_path} {time.time() - t0:.2f} ')
    # print(f'out: {out} {type(out)}')
    words = out['words']
    # print(f'words: {words} {len(words)}')
    for group in words:  # type: tuple[tuple[float, float]]
        # print(f'group: {group}')
        point_1 = (int(group[0][0] * high), int(group[0][1] * width * ratio))
        point_2 = (int(group[2][0] * high), int(group[2][1] * width * ratio))
        # print(f'{width} {high} point_1: {point_1} point_2: {point_2}')
        cv2.rectangle(img_cv2, point_2, point_1, (0, 255, 0), 5)
    
    # save cv2 image into a jpg file
    cv2.imwrite(image_path_out, img_cv2)
    archive.add(image_path_out)
    
    # import matplotlib.pyplot as plt
    
    # plt.imshow(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGBA))
    # plt.show()


class COLORS(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 224, 100)


# white_threshold = 5
# black_threshold = 100


class PIXEL_CATEGORY(Enum):
    WHITE = 1
    BLACK = 2
    OTHER = 3


def _detect_pixel_category(pixel, white_threshold, black_threshold):
    # type: (tuple[int, int, int], int, int) -> PIXEL_CATEGORY
    if pixel[0] > 255 - white_threshold and pixel[1] > 255 - white_threshold and pixel[2] > 255 - white_threshold:
        return PIXEL_CATEGORY.WHITE
    elif pixel[0] < black_threshold and pixel[1] < black_threshold and pixel[2] < black_threshold:
        return PIXEL_CATEGORY.BLACK
    else:
        return PIXEL_CATEGORY.OTHER


def _add_image_block_text(image, text, alternative_position):
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    
    # Define the font and color
    font = ImageFont.truetype("arial.ttf", 20)  # Adjust the font path and size as needed
    text_color = "red"
    
    # Calculate text position for top-middle
    
    position = ((image.width) / 10, 5)  # Adjust the y-coordinate as needed
    if alternative_position:
        position = ((image.width) / 2, 10)
    
    # Draw the text
    draw.text(position, text, fill=text_color, font=font)
    
    # Return the modified image
    return image


def _do_save_image_with_bloc(image, dest, recursive_call=False):
    img_copy = image.copy()
    # get the last part of the path
    last_part = os.path.basename(dest)
    img_with_block = _add_image_block_text(img_copy, last_part, recursive_call)
    save_image(img_with_block, dest)
    archive.add(dest)


def _save_image(index, image, suffix):
    # type: (int, Image, str) -> None
    dst = f"test_out/img{index}_{suffix}.jpg"
    _do_save_image_with_bloc(image, dst)
    
    # Also transform to classic with this pre-operation
    # _classic_transform(dst, f"test_out/img{index}_{suffix}_classic.png", recursive_call=True)


def _classic_transform(image_path, dest_path, recursive_call=False):
    converted_images = convert_image(image_path)
    _do_save_image_with_bloc(converted_images[0], dest_path, recursive_call=recursive_call)


def _get_variance(image):
    # type: (Image) -> float
    stat = ImageStat.Stat(image)
    return (stat.var[0] + stat.var[1] + stat.var[2]) / 3.0


def _simple_threshold(i, image):
    for k in range(1, 5):
        img = image.copy()
        d = img.getdata()
        
        white_threshold = 5 + k * 25
        black_threshold = 100 + k * 25
        new_pixels = []
        for pixel in d:
            pixel_category = _detect_pixel_category(pixel, white_threshold, black_threshold)
            if pixel_category == PIXEL_CATEGORY.WHITE:
                new_pixels.append(COLORS.WHITE.value)
            elif pixel_category == PIXEL_CATEGORY.BLACK:
                new_pixels.append(COLORS.BLACK.value)
            else:
                new_pixels.append(COLORS.WHITE.value)
        
        # update image data
        img.putdata(new_pixels)
        
        # save new image
        _save_image(i, img, f'simple_threshold_{k}')
    return image


def _image_original(image):
    # type: (Image) -> Image
    _save_image(i, image, 'original')
    return image


def _image_enhance_color(image):
    # type: (Image) -> Image
    enhancer = ImageEnhance.Color(image)
    
    # 1= original, <1 less colors, >1 more colors
    # LOW => bad
    
    # HIGH
    image = enhancer.enhance(1.5)
    _save_image(i, image, 'enhance_color_high')
    
    # Very HIGH
    image = enhancer.enhance(10)
    _save_image(i, image, 'enhance_color_very_high')
    
    return image


def _image_contrast(image):
    # type: (Image) -> Image
    enhancer = ImageEnhance.Contrast(image)
    
    # low => bad quality
    
    # HIGH
    image = enhancer.enhance(1.5)  # 1= original, <1 less contrast, >1 more contrast
    _save_image(i, image, 'contrast_high')
    
    # VERY HIGH
    image = enhancer.enhance(10)  # 1= original, <1 less contrast, >1 more contrast
    _save_image(i, image, 'contrast_very_high')
    
    return image


## ALL SUCKS
# def _image_brightness(image):
#     # type: (Image) -> Image
#     enhancer = ImageEnhance.Brightness(image)
#
#     # LOW
#     image = enhancer.enhance(0.5)  # 1= original, <1 less brightness, >1 more brightness
#     _save_image(i, image, 'brightness_low')
#
#     # HIGH
#     image = enhancer.enhance(1.5)  # 1= original, <1 less brightness, >1 more brightness
#     _save_image(i, image, 'brightness_high')
#
#     return image


def _image_sharpness(image):
    # type: (Image) -> Image
    enhancer = ImageEnhance.Sharpness(image)
    
    # LOW => bad quality
    # image = enhancer.enhance(0.5)  # 1= original, <1 less sharpness, >1 more sharpness
    # _save_image(i, image, 'sharpness_low')
    
    # HIGH
    image = enhancer.enhance(1.5)  # 1= original, <1 less sharpness, >1 more sharpness
    _save_image(i, image, 'sharpness_high')
    
    # VERY HIGH
    image = enhancer.enhance(10)
    _save_image(i, image, 'sharpness_very_high')
    
    return image


archive = ArchivePDF('test_out/out', 'test_title', 'Kobo Elipsa 2E')

for i in range(1, 13):
    start = time.time()
    in_path = f"test_in/img{i}.jpg"
    image = Image.open(in_path)
    image = image.convert('RGB')
    
    # original
    original_image = _image_original(image)
    print(f'{i}  {time.time() - start:.2f} ORIGINAL Image {i} {image.size}')
    
    _classic_transform(in_path, f"test_out/img{i}_classic.png")
    
    # IA detection:
    _detect_text_positions(in_path, f"test_out/img{i}_ia.jpg")
    
    # Enhance color
    color_image = _image_enhance_color(image)
    print(f'{i}  {time.time() - start:.2f} COLOR Image {i} {image.size}')
    
    # Contrast
    contrast_image = _image_contrast(image)
    print(f'{i}  {time.time() - start:.2f} CONTRAST Image {i} {image.size}')
    
    # Brightness => all sucks
    # brightness_image = _image_brightness(image)
    # brightness_variance = _get_variance(brightness_image)
    # print(f'{i}  {time.time() - start:.2f} BRIGHTNESS  {image.size}')
    
    # Sharpness
    sharpness_image = _image_sharpness(image)
    print(f'{i}  {time.time() - start:.2f} SHARPNESS Image {i} {image.size}')
    
    # Threshold
    threshold_image = _simple_threshold(i, image)
    print(f'{i}  {time.time() - start:.2f} THRESOLD Image {i} {image.size}')

archive.close()

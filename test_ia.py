import os.path
import time
from enum import Enum

import numpy as np

import cv2
# HACK weasyprint.HTML because it's imported by doctr but useless in our case, & buggy to install!
import sys

from PIL import ImageStat, ImageEnhance, Image, ImageDraw, ImageFont, ImageChops

from henskan.archive_pdf import ArchivePDF
from henskan.image import convert_image, save_image, _apply_grey_palette, _apply_basic_grey, Palette15b, Palette16
from henskan.parameters import parameters

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
    GREY = 3
    OTHER = 4


def _detect_pixel_category(pixel, white_threshold, black_threshold, verbose=False):
    # type: (tuple[int, int, int], int, int, bool) -> PIXEL_CATEGORY
    if pixel[0] >= 255 - white_threshold and pixel[1] >= 255 - white_threshold and pixel[2] >= 255 - white_threshold:
        return PIXEL_CATEGORY.WHITE
    elif pixel[0] <= black_threshold and pixel[1] <= black_threshold and pixel[2] <= black_threshold:
        return PIXEL_CATEGORY.BLACK
    elif abs(pixel[0] - pixel[1]) < 10 and abs(pixel[0] - pixel[2]) < 10:  # a diff in 5 (on 255) is ok for "quite the same"
        return PIXEL_CATEGORY.GREY
    else:
        # if verbose:
        #    print(f'OTHER pixel: {pixel} ')
        return PIXEL_CATEGORY.OTHER

SOLID_COLORS = []

def _load_solid_colors_from_csv():
    with open('./test_in/solid_colors.csv', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rgb = tuple(line.split(',')[1].split('-'))
            print(f'RGB {rgb}')
            SOLID_COLORS.append((int(rgb[0]), int(rgb[1]), int(rgb[2])))

#_load_solid_colors_from_csv()

def _load_solid_colors_from_gen():
    N = 3  # => 64 colors
    for i in range(N+1):
        r = int(255 / N  * i)
        for j in range(N+1):
            g = int(255 / N  * j)
            for k in range(N+1):
                b = int(255 /N * k)
                print(f'RGB {r} {g} {b}')
                SOLID_COLORS.append((r, g, b))

_load_solid_colors_from_gen()
print(f'Len SOLID_COLORS: {len(SOLID_COLORS)}')

from functools import lru_cache

@lru_cache(maxsize=65535)
def _change_by_nearest_solid_color(pixel):
    min_dist = 99999999
    nearest_color = None
    for rgb in SOLID_COLORS:
        r_ref = rgb[0]
        g_ref = rgb[1]
        b_ref = rgb[2]
        r_pixel = pixel[0]
        g_pixel = pixel[1]
        b_pixel = pixel[2]
        
        # Must take a color "higher" than the pixel color
        if r_pixel > r_ref or g_pixel > g_ref or b_pixel > b_ref:
            continue
        
        color_dist = (r_ref - r_pixel) ** 2 + (g_ref - g_pixel) ** 2 + (b_ref - b_pixel) ** 2
        if color_dist < min_dist:
            min_dist = color_dist
            nearest_color = rgb
    return nearest_color

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
    # type: (str, str, bool) -> None
    converted_images = convert_image(image_path)
    _do_save_image_with_bloc(converted_images[0], dest_path, recursive_call=recursive_call)


def _into_palette_15(img, dest_path, recursive_call=False):
    # type: (Image, str, bool) -> None
    
    palette = Palette15b
    img = _apply_grey_palette(img, palette)
    _do_save_image_with_bloc(img, dest_path, recursive_call=recursive_call)


def _into_palette_16(img, dest_path, recursive_call=False):
    # type: (Image, str, bool) -> None
    
    palette = Palette16
    img = _apply_grey_palette(img, palette)
    _do_save_image_with_bloc(img, dest_path, recursive_call=recursive_call)




def _into_classic_grey(image, dest_path, recursive_call=False):
    # type: (Image, str, bool) -> None
    img = _apply_basic_grey(image)
    _do_save_image_with_bloc(img, dest_path, recursive_call=recursive_call)


def _get_variance(image):
    # type: (Image) -> float
    stat = ImageStat.Stat(image)
    return (stat.var[0] + stat.var[1] + stat.var[2]) / 3.0


def _is_globally_grey__slow(i, image):
    # type: (int, Image) -> bool
    pixels = image.getdata()
    
    nb_pixels = len(pixels)
    nb_pixels_in_colors_over_threshold = nb_pixels * 0.1  # if more than 10% of pixels are in colors, then it's not grey and we can stop the loop
    nb_pixels_in_colors = 0
    cats = {}
    for pixel in pixels:
        cat = _detect_pixel_category(pixel, 0, 0, verbose=True)
        if cat not in cats:
            cats[cat] = 0
        cats[cat] += 1
        if cat == PIXEL_CATEGORY.OTHER:
            nb_pixels_in_colors += 1
            if nb_pixels_in_colors > nb_pixels_in_colors_over_threshold:
                print(f' {i} too many pixels in colors, over 10%: {nb_pixels_in_colors} / {nb_pixels}')
                return False
    print(f' {i} cats: {cats}')
    total_pixels = cats.get(PIXEL_CATEGORY.WHITE, 0) + cats.get(PIXEL_CATEGORY.BLACK, 0) + cats.get(PIXEL_CATEGORY.GREY, 0) + cats.get(
            PIXEL_CATEGORY.OTHER, 0)
    nb_others = cats.get(PIXEL_CATEGORY.OTHER, 0)
    pct_colors = nb_others / total_pixels * 100
    print(f' {i} pct_colors: {pct_colors:.2f}%')
    is_grey = pct_colors < 10  # if less than 10% of colors, then it's mostly grey
    return is_grey


# Check if image is monochrome (1 channel or 3 identical channels)
def is_totally_greyscale__fast(i, image):
    # type: (int, Image) -> bool
    if image.mode not in ("L", "RGB"):
        # Unsupported image mode
        return False
    
    if image.mode == "RGB":
        rgb = image.split()
        extrema = ImageChops.difference(rgb[0], rgb[1]).getextrema()[1]
        print(f' {i} extrema 1?  {extrema}')
        if extrema >= 15:
            return False
        extrema = ImageChops.difference(rgb[0], rgb[2]).getextrema()[1]
        print(f' {i} extrema 2?  {extrema}')
        if extrema >= 15:
            return False
    return True


def _simple_threshold(i, image):
    for k in range(0, 5):
        img_mask = image.copy()
        img_colored = image.copy()
        d = img_mask.getdata()
        
        white_threshold = 5 + k * 25
        black_threshold = 100 + k * 25
        new_pixels_mask = []
        new_pixels_colored = []
        for pixel in d:
            pixel_category = _detect_pixel_category(pixel, white_threshold, black_threshold)
            if pixel_category == PIXEL_CATEGORY.WHITE:
                new_pixels_mask.append(COLORS.WHITE.value)
                new_pixels_colored.append(COLORS.WHITE.value)
            elif pixel_category == PIXEL_CATEGORY.BLACK:
                new_pixels_mask.append(COLORS.BLACK.value)
                new_pixels_colored.append(pixel)  # on black part, keep the original color, the detection is a mask
            else:
                new_pixels_mask.append(COLORS.WHITE.value)
                new_pixels_colored.append(COLORS.WHITE.value)
        
        # update image data
        img_mask.putdata(new_pixels_mask)
        # save new image
        _save_image(i, img_mask, f'simple_threshold_{k}')
        
        # colored version
        img_colored.putdata(new_pixels_colored)
        _save_image(i, img_colored, f'simple_threshold_{k}_colored')
    return image


def _image_to_nearest_color(i, image):
    img = image.copy()
    pixels = list(img.getdata())
    
    new_pixels = []
    for pixel in pixels:
        new_pixel = _change_by_nearest_solid_color(pixel)
        new_pixels.append(new_pixel)
    
    # update image data
    img.putdata(new_pixels)
    
    # save new image
    _save_image(i, img, f'nearest_color')
    return img


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

for i in range(1, 27):
    print(f'\n\n')
    start = time.time()
    in_path = f"test_in/img{i}.jpg"
    image = Image.open(in_path)
    image = image.convert('RGB')
    
    # original
    before = time.time()
    original_image = _image_original(image)
    print(f'{i}  {time.time() - before:.2f} ORIGINAL Image {i} {image.size}')
    
    # Grey detection
    before = time.time()
    is_grey = is_totally_greyscale__fast(i, image)  # if True, then we can trust it's grey
    print(f'{i}  {time.time() - before:.2f} GREYSCALE Image FAST => is_grey: {is_grey}')
    
    if not is_grey:  # maybe it's a grey with a little bit of colors, so must check for real colors presence
        before_slow = time.time()
        is_grey = _is_globally_grey__slow(i, image)
        print(f'{i}  {time.time() - before_slow:.2f} SLOW DETECT COLORS => is_grey: {is_grey}')
        if is_grey:
            print(f'{i}  *********** WAS IN FACT GREY ***********')
    
    print(f'{i}  {time.time() - before:.2f} GREYSCALE Image {is_grey=}')
    
    _classic_transform(in_path, f"test_out/img{i}_classic.png")
    
    _into_palette_15(image, f"test_out/img{i}_palette_15.png")
    
    _into_palette_16(image, f"test_out/img{i}_palette_16.png")
    
    _into_classic_grey(image, f"test_out/img{i}_classic_grey.png")
    
    # IA detection:
    try:
        _detect_text_positions(in_path, f"test_out/img{i}_ia.jpg")
    except ValueError:
        print(f'Error in IA detection for {in_path}')
    
    # Enhance color
    before = time.time()
    color_image = _image_enhance_color(image)
    print(f'{i}  {time.time() - before:.2f} COLOR Image {i} {image.size}')
    
    # Contrast
    before = time.time()
    contrast_image = _image_contrast(image)
    print(f'{i}  {time.time() - before:.2f} CONTRAST Image {i} {image.size}')
    
    # Brightness => all sucks
    # brightness_image = _image_brightness(image)
    # brightness_variance = _get_variance(brightness_image)
    # print(f'{i}  {time.time() - start:.2f} BRIGHTNESS  {image.size}')
    
    # Sharpness
    before = time.time()
    sharpness_image = _image_sharpness(image)
    print(f'{i}  {time.time() - before:.2f} SHARPNESS Image {i} {image.size}')
    
    # Threshold
    before = time.time()
    threshold_image = _simple_threshold(i, image)
    print(f'{i}  {time.time() - before:.2f} THRESOLD Image {i} {image.size}')

    # Nearest color
    before = time.time()
    nearest_color_image = _image_to_nearest_color(i, image)
    print(f'{i}  {time.time() - before:.2f} NEAREST COLOR Image {i} {image.size}')

archive.close()

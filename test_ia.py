import os.path
import time
from enum import Enum

import numpy as np

import cv2
# HACK weasyprint.HTML because it's imported by doctr but useless in our case, & buggy to install!
import sys

from PIL import ImageStat, ImageEnhance, Image

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
        print(f'Predictor loaded in {time.time() - t0} seconds')
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
    print(f'{image_path} Predicted in {time.time() - t0} seconds')
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
    
    # import matplotlib.pyplot as plt
    
    # plt.imshow(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGBA))
    # plt.show()


class COLORS(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 224, 100)


white_threshold = 5
black_threshold = 100


class PIXEL_CATEGORY(Enum):
    WHITE = 1
    BLACK = 2
    OTHER = 3


def _detect_pixel_category(pixel):
    # type: (tuple[int, int, int]) -> PIXEL_CATEGORY
    if pixel[0] > 255 - white_threshold and pixel[1] > 255 - white_threshold and pixel[2] > 255 - white_threshold:
        return PIXEL_CATEGORY.WHITE
    elif pixel[0] < black_threshold and pixel[1] < black_threshold and pixel[2] < black_threshold:
        return PIXEL_CATEGORY.BLACK
    else:
        return PIXEL_CATEGORY.OTHER


def _save_image(index, image, suffix):
    # type: (int, Image, str) -> None
    image.save(f"test_out/img{index}_{suffix}.jpg")


def _get_variance(image):
    # type: (Image) -> float
    stat = ImageStat.Stat(image)
    return (stat.var[0] + stat.var[1] + stat.var[2]) / 3.0


def _simple_threshold(image):
    d = image.getdata()
    
    new_pixels = []
    for pixel in d:
        pixel_category = _detect_pixel_category(pixel)
        if pixel_category == PIXEL_CATEGORY.WHITE:
            new_pixels.append(COLORS.WHITE.value)
        elif pixel_category == PIXEL_CATEGORY.BLACK:
            new_pixels.append(COLORS.BLACK.value)
        else:
            new_pixels.append(COLORS.WHITE.value)
    
    # update image data
    image.putdata(new_pixels)
    
    # save new image
    _save_image(i, image, 'simple_threshold')
    return image


def _image_original(image):
    # type: (Image) -> Image
    _save_image(i, image, 'original')
    return image


def _image_enhance_color(image):
    # type: (Image) -> Image
    enhancer = ImageEnhance.Color(image)
    
    # 1= original, <1 less colors, >1 more colors
    # LOW
    image = enhancer.enhance(0.5)
    _save_image(i, image, 'enhance_color_low')
    
    # HIGH
    image = enhancer.enhance(1.5)
    _save_image(i, image, 'enhance_color_high')
    
    return image


def _image_contrast(image):
    # type: (Image) -> Image
    enhancer = ImageEnhance.Contrast(image)
    
    # LOW
    image = enhancer.enhance(1.5)  # 1= original, <1 less contrast, >1 more contrast
    _save_image(i, image, 'contrast_low')
    
    # HIGH
    image = enhancer.enhance(0.5)  # 1= original, <1 less contrast, >1 more contrast
    _save_image(i, image, 'contrast_high')
    
    return image


def _image_brightness(image):
    # type: (Image) -> Image
    enhancer = ImageEnhance.Brightness(image)
    
    # LOW
    image = enhancer.enhance(0.5)  # 1= original, <1 less brightness, >1 more brightness
    _save_image(i, image, 'brightness_low')
    
    # HIGH
    image = enhancer.enhance(1.5)  # 1= original, <1 less brightness, >1 more brightness
    _save_image(i, image, 'brightness_high')
    
    return image


def _image_sharpness(image):
    # type: (Image) -> Image
    enhancer = ImageEnhance.Sharpness(image)
    
    # LOW
    image = enhancer.enhance(0.5)  # 1= original, <1 less sharpness, >1 more sharpness
    _save_image(i, image, 'sharpness_low')
    
    # HIGH
    image = enhancer.enhance(1.5)  # 1= original, <1 less sharpness, >1 more sharpness
    _save_image(i, image, 'sharpness_high')
    
    return image


for i in range(1, 11):
    start = time.time()
    in_path = f"test_in/img{i}.jpg"
    out_path = f"test_out/img{i}.jpg"
    image = Image.open(in_path)
    image = image.convert('RGB')
    initial_variance = _get_variance(image)
    
    # original
    original_image = _image_original(image)
    original_variance = _get_variance(original_image)
    print(f'ORIGINAL Image {i} {image.size} took {time.time() - start} variances: {initial_variance} -> {original_variance}')
    
    # IA detection:
    _detect_text_positions(in_path, out_path)
    
    # Enhance color
    color_image = _image_enhance_color(image)
    color_variance = _get_variance(color_image)
    print(f'COLOR Image {i} {image.size} took {time.time() - start} variances: {initial_variance} -> {color_variance}')
    
    # Contrast
    contrast_image = _image_contrast(image)
    contrast_variance = _get_variance(contrast_image)
    print(f'CONTRAST Image {i} {image.size} took {time.time() - start} variances: {initial_variance} -> {contrast_variance}')
    
    # Brightness
    brightness_image = _image_brightness(image)
    brightness_variance = _get_variance(brightness_image)
    print(f'BRIGHTNESS Image {i} {image.size} took {time.time() - start} variances: {initial_variance} -> {brightness_variance}')
    
    # Sharpness
    sharpness_image = _image_sharpness(image)
    sharpness_variance = _get_variance(sharpness_image)
    print(f'SHARPNESS Image {i} {image.size} took {time.time() - start} variances: {initial_variance} -> {sharpness_variance}')
    
    # Threshold
    threshold_image = _simple_threshold(image)
    threshold_variance = _get_variance(threshold_image)
    print(f'THRESOLD Image {i} {image.size} took {time.time() - start} variances: {initial_variance} -> {threshold_variance}')

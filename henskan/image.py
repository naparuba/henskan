# Copyright 2011-2019 Alex Yatskov
# Copyright 2020+     Gabès Jean (naparuba@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import io
import time
import traceback
from enum import Enum
from math import ceil
from typing import Tuple

from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat

from .archive import ARCHIVE_FORMATS
from .parameters import parameters

DEBUG = False


def set_debug():
    global DEBUG
    DEBUG = True


def _get_palette(size):
    # type: (int) -> list
    _palette = []
    for i in range(size):
        _palette.extend([i, i, i])
    return _palette


Palette4 = [
    0x00, 0x00, 0x00,
    0x55, 0x55, 0x55,
    0xaa, 0xaa, 0xaa,
    0xff, 0xff, 0xff
]

Palette15a = [
    0x00, 0x00, 0x00,
    0x11, 0x11, 0x11,
    0x22, 0x22, 0x22,
    0x33, 0x33, 0x33,
    0x44, 0x44, 0x44,
    0x55, 0x55, 0x55,
    0x66, 0x66, 0x66,
    0x77, 0x77, 0x77,
    0x88, 0x88, 0x88,
    0x99, 0x99, 0x99,
    0xaa, 0xaa, 0xaa,
    0xbb, 0xbb, 0xbb,
    0xcc, 0xcc, 0xcc,
    0xdd, 0xdd, 0xdd,
    0xff, 0xff, 0xff,
]

Palette15b = [
    0x00, 0x00, 0x00,
    0x11, 0x11, 0x11,
    0x22, 0x22, 0x22,
    0x33, 0x33, 0x33,
    0x44, 0x44, 0x44,
    0x55, 0x55, 0x55,
    0x77, 0x77, 0x77,
    0x88, 0x88, 0x88,
    0x99, 0x99, 0x99,
    0xaa, 0xaa, 0xaa,
    0xbb, 0xbb, 0xbb,
    0xcc, 0xcc, 0xcc,
    0xdd, 0xdd, 0xdd,
    0xee, 0xee, 0xee,
    0xff, 0xff, 0xff,
]

Palette16 = [
    0x00, 0x00, 0x00,
    0x11, 0x11, 0x11,
    0x22, 0x22, 0x22,
    0x33, 0x33, 0x33,
    0x44, 0x44, 0x44,
    0x55, 0x55, 0x55,
    0x66, 0x66, 0x66,
    0x77, 0x77, 0x77,
    0x88, 0x88, 0x88,
    0x99, 0x99, 0x99,
    0xaa, 0xaa, 0xaa,
    0xbb, 0xbb, 0xbb,
    0xcc, 0xcc, 0xcc,
    0xdd, 0xdd, 0xdd,
    0xee, 0xee, 0xee,
    0xff, 0xff, 0xff,
]


class EReaderData:
    Profiles = {
        'Kindle 1':                         ((600, 800), Palette4, ARCHIVE_FORMATS.PDF),
        'Kindle 2/3/Touch':                 ((600, 800), Palette15a, ARCHIVE_FORMATS.PDF),
        'Kindle 4 & 5':                     ((600, 800), Palette15b, ARCHIVE_FORMATS.PDF),
        'Kindle DX/DXG':                    ((824, 1200), Palette15a, ARCHIVE_FORMATS.PDF),
        'Kindle Paperwhite 1 & 2':          ((758, 1024), Palette15b, ARCHIVE_FORMATS.PDF),
        'Kindle Paperwhite 3/Voyage/Oasis': ((1072, 1448), Palette16, ARCHIVE_FORMATS.PDF),
        'Kobo Mini/Touch':                  ((600, 800), Palette15b, ARCHIVE_FORMATS.CBZ),
        'Kobo Glo':                         ((768, 1024), Palette15b, ARCHIVE_FORMATS.CBZ),
        'Kobo Glo HD':                      ((1072, 1448), Palette15b, ARCHIVE_FORMATS.CBZ),
        'Kobo Aura':                        ((758, 1024), Palette15b, ARCHIVE_FORMATS.CBZ),
        'Kobo Aura HD':                     ((1080, 1440), Palette16, ARCHIVE_FORMATS.CBZ),
        'Kobo Aura H2O':                    ((1080, 1430), Palette16, ARCHIVE_FORMATS.CBZ),
        'Kobo Libra H2O':                   ((1264, 1680), Palette16, ARCHIVE_FORMATS.CBZ),
        'Kobo Elipsa 2E':                   ((1440, 1872), Palette16, ARCHIVE_FORMATS.CBZ),
    }
    
    
    @staticmethod
    def get_size(device):
        # type: (str) -> tuple[int, int]
        return EReaderData.Profiles[device][0]
    
    
    @staticmethod
    def get_palette(device):
        # type: (str) -> list
        return EReaderData.Profiles[device][1]
    
    
    @staticmethod
    def get_archive_format(device):
        # type: (str) -> ARCHIVE_FORMATS
        return EReaderData.Profiles[device][2]
    
    
    @staticmethod
    def is_device_exists(device):
        return device in EReaderData.Profiles


# decorate a function that use image, *** and if there
# is an exception raise by PIL (IOError) then return
# the original image because PIL cannot manage it
def protect_bad_image(func):
    def func_wrapper(*args, **kwargs):
        # If you cannot convert (like a bogus image) return the original one
        # args will be "image" and other params are after
        try:
            return func(*args, **kwargs)
        except (IOError, ValueError):  # Exception from PIL about bad image
            print(f' * protect_bad_image:: Bad image, return original {traceback.format_exc()}')
            return args[0]
    
    
    return func_wrapper


@protect_bad_image
def _split_left(image):
    # type: (Image) -> Image
    width_img, height_img = image.size
    
    return image.crop((0, 0, width_img // 2, height_img))


@protect_bad_image
def _split_right(image):
    # type: (Image) -> Image
    width_img, height_img = image.size
    
    return image.crop((width_img // 2, 0, width_img, height_img))


class PIXEL_CATEGORY(Enum):
    WHITE = 1
    BLACK = 2
    GREY = 3
    OTHER = 4


def _detect_pixel_category(pixel):
    # type: (tuple[int, int, int]) -> PIXEL_CATEGORY
    if pixel[0] >= 255 and pixel[1] >= 255 and pixel[2] >= 255:
        return PIXEL_CATEGORY.WHITE
    elif pixel[0] <= 0 and pixel[1] <= 0 and pixel[2] <= 0:
        return PIXEL_CATEGORY.BLACK
    elif abs(pixel[0] - pixel[1]) < 10 and abs(pixel[0] - pixel[2]) < 10:  # a diff in 10 (on 255) is ok for "quite the same"
        return PIXEL_CATEGORY.GREY
    else:
        return PIXEL_CATEGORY.OTHER


@protect_bad_image
def _is_globally_grey__slow(image):
    # type: (Image) -> bool
    pixels = image.getdata()
    
    nb_pixels = len(pixels)
    nb_pixels_in_colors_over_threshold = nb_pixels * 0.1  # if more than 10% of pixels are in colors, then it's not grey and we can stop the loop
    nb_pixels_in_colors = 0
    cats = {}
    for pixel in pixels:
        cat = _detect_pixel_category(pixel)
        if cat not in cats:
            cats[cat] = 0
        cats[cat] += 1
        if cat == PIXEL_CATEGORY.OTHER:
            nb_pixels_in_colors += 1
            if nb_pixels_in_colors > nb_pixels_in_colors_over_threshold:
                print(f' too many pixels in colors, over 10%: {nb_pixels_in_colors} / {nb_pixels}')
                return False
    print(f' cats: {cats}')
    total_pixels = cats.get(PIXEL_CATEGORY.WHITE, 0) + cats.get(PIXEL_CATEGORY.BLACK, 0) + cats.get(PIXEL_CATEGORY.GREY, 0) + cats.get(
            PIXEL_CATEGORY.OTHER, 0)
    nb_others = cats.get(PIXEL_CATEGORY.OTHER, 0)
    pct_colors = nb_others / total_pixels * 100
    print(f' pct_colors: {pct_colors:.2f}%')
    is_grey = pct_colors < 10  # if less than 10% of colors, then it's mostly grey
    return is_grey


# Check if image is monochrome (1 channel or 3 identical channels)
@protect_bad_image
def _is_totally_greyscale__fast(image):
    # type: ( Image) -> bool
    if image.mode not in ("L", "RGB"):
        # Unsupported image mode
        return False
    
    if image.mode == "RGB":
        rgb = image.split()
        extrema = ImageChops.difference(rgb[0], rgb[1]).getextrema()[1]
        print(f' extrema 1?  {extrema}')
        if extrema >= 15:
            return False
        extrema = ImageChops.difference(rgb[0], rgb[2]).getextrema()[1]
        print(f' extrema 2?  {extrema}')
        if extrema >= 15:
            return False
    return True


@protect_bad_image
def _is_image_grey(image):
    # type: (Image) -> bool
    before = time.time()
    is_grey = _is_totally_greyscale__fast(image)  # if True, then we can trust it's grey
    print(f'{time.time() - before:.2f} GREYSCALE Image FAST => is_grey: {is_grey}')
    
    if not is_grey:  # maybe it's a grey with a little bit of colors, so must check for real colors presence
        before_slow = time.time()
        is_grey = _is_globally_grey__slow(image)
        print(f'  {time.time() - before_slow:.2f} SLOW DETECT COLORS => is_grey: {is_grey}')
        if is_grey:
            print(f'  *********** WAS IN FACT GREY ***********')
    return is_grey


@protect_bad_image
def _apply_grey_palette(image, palette):
    # type: (Image, list) -> Image
    
    colors = len(palette) // 3
    if colors < 256:
        palette = palette + palette[:3] * (256 - colors)
    
    pal_img = Image.new('P', (1, 1))
    pal_img.putpalette(palette)
    
    return image.quantize(palette=pal_img)


@protect_bad_image
def _apply_basic_grey(image):
    # type: (Image) -> Image
    
    return ImageOps.grayscale(image)


@protect_bad_image
def _quantize_image(image, palette):
    # type: (Image, list) -> Image
    
    t0 = time.time()
    img_palette = _apply_grey_palette(image, palette)
    t1 = time.time()
    img_basic_grey = _apply_basic_grey(image)
    t2 = time.time()
    
    # Get image that is smaller in disk size
    
    # Save both images to buffers
    with io.BytesIO() as temp_palette_file:
        img_palette.save(temp_palette_file, format='PNG')
        palette_file_size = len(temp_palette_file.getvalue())
    t3 = time.time()
    
    with io.BytesIO() as temp_basic_file:
        img_basic_grey.save(temp_basic_file, format='PNG')
        basic_file_size = len(temp_basic_file.getvalue())
    t4 = time.time()
    
    print(f'Times: Palette:{t1 - t0:.3f}s  Basic:{t2 - t1:.3f}s  Save-palette:{t3 - t2:.3f}s  Save-basic:{t4 - t3:.3f}s')
    print(f'Sizes: Palette:{palette_file_size}  Basic:{basic_file_size}')
    
    # Get smaller one
    if palette_file_size < basic_file_size:
        print(f' * Quantize image => Using palette image')
        return img_palette
    print(f' * Quantize image => Using basic grey image')
    return img_basic_grey


@protect_bad_image
def _resize_image(image, to_size):
    # type: (Image, tuple[int, int]) -> Image
    width_to_set, height_to_set = to_size
    width_img, height_img = image.size
    
    ratio_img = float(width_img) / float(height_img)
    ratio_width = float(width_img) / float(width_to_set)
    ratio_height = float(height_img) / float(height_to_set)
    
    if ratio_width > ratio_height:
        width_img = width_to_set
        height_img = int(width_to_set / ratio_img)
    elif ratio_width < ratio_height:
        height_img = height_to_set
        width_img = int(height_to_set * ratio_img)
    else:
        width_img, height_img = to_size
    
    if DEBUG:
        print(' * Resizing image from %s to %s/%s' % (image.size, width_img, height_img))
    
    # Ok we can resize
    return image.resize((width_img, height_img), Image.Resampling.LANCZOS)


@protect_bad_image
def _fill_image_to_whole_size(image, to_size):
    # type: (Image, tuple[int, int]) -> Image
    white = (255, 255, 255)
    final_image = Image.new("RGB", to_size, white)  # Fond blanc
    
    margin_left = 10
    image_width, _ = image.size
    to_width, _ = to_size
    
    # If the image is small enough, put a margin of the left
    if image_width <= to_width - margin_left:
        paste_position = (margin_left, 0)
    else:  # ok no place for the margin ^^
        paste_position = (0, 0)
    
    final_image.paste(image, paste_position)
    
    return final_image


@protect_bad_image
def _format_image_to_rgb(image):
    # type: (Image) -> Image
    if image.mode == 'RGB':
        return image
    
    return image.convert('RGB')


@protect_bad_image
def _orient_image(image, device_size):
    # type: (Image, tuple[int, int]) -> Image
    width_dev, height_dev = device_size
    width_img, height_img = image.size
    
    if (width_img > height_img) != (width_dev > height_dev):
        return image.rotate(90, Image.Resampling.LANCZOS, True)
    return image


# We will auto crop the image, by removing just white part around the image
# by inverting colors, and asking a bounder box ^^
@protect_bad_image
def _blurauto_crop_image(image):
    # type: (Image) -> Image
    orig_image = image
    power = 2.0  # mode: pifometre
    # work on a black image
    blur_image = ImageOps.invert(image.convert(mode='L'))
    blur_image = blur_image.point(lambda x: x and 255)
    blur_image = blur_image.filter(ImageFilter.MinFilter(size=3))
    blur_image = blur_image.filter(ImageFilter.GaussianBlur(radius=5))
    blur_image = blur_image.point(lambda x: (x >= 16 * power) and x)
    blur_bbox = blur_image.getbbox()
    if blur_bbox:
        return orig_image.crop(blur_bbox)
    return orig_image


def _find_dominant_color(img):
    # type: (Image) -> Tuple[int]
    # Resizing parameters
    width, height = 150, 150
    img = img.resize((width, height), resample=0)
    # Get colors from image object
    pixels = img.getcolors(width * height)
    # Sort them by count number(first element of tuple)
    sorted_pixels = sorted(pixels, key=lambda t: t[0])
    # Get the most frequent color
    dominant_color = sorted_pixels[-1][1]
    return dominant_color


def _get_image_variance(image):
    # type: (Image) -> float
    return ImageStat.Stat(image).var[0]


@protect_bad_image
def _auto_crop_image(image):
    # type: (Image) -> Image
    fixed_threshold = 5.0
    
    before = time.time()
    
    if ImageChops.invert(image).getbbox() is None:
        if DEBUG:
            print(' * autoCropImage => Using simpleCropImage because no bbox')
        image = _simple_crop_image(image)
        return image
    
    width, height = image.size
    delta = 2
    diff = delta
    if _get_image_variance(image) < 2 * fixed_threshold:
        if DEBUG:
            print(' * autoCropImage => Image variance is already too small, give back image')
        image = _simple_crop_image(image)
        return image
    
    while _get_image_variance(image.crop((0, height - diff, width, height))) < fixed_threshold and diff < height:
        diff += delta
    diff -= delta
    page_number_cut1 = diff
    if diff < delta:
        diff = delta
    old_stat = _get_image_variance(image.crop((0, height - diff, width, height)))
    diff += delta
    while _get_image_variance(image.crop((0, height - diff, width, height))) - old_stat > 0 and diff < height // 4:
        old_stat = _get_image_variance(image.crop((0, height - diff, width, height)))
        diff += delta
    diff -= delta
    page_number_cut2 = diff
    diff += delta
    old_stat = _get_image_variance(image.crop((0, height - diff, width, height - page_number_cut2)))
    while _get_image_variance(image.crop((0, height - diff, width, height - page_number_cut2))) < fixed_threshold + old_stat and diff < height // 4:
        diff += delta
    diff -= delta
    page_number_cut3 = diff
    delta = 5
    diff = delta
    while _get_image_variance(image.crop((0, height - page_number_cut2, diff, height))) < fixed_threshold and diff < width:
        diff += delta
    diff -= delta
    page_number_x1 = diff
    diff = delta
    while _get_image_variance(image.crop((width - diff, height - page_number_cut2, width, height))) < fixed_threshold and diff < width:
        diff += delta
    diff -= delta
    page_number_x2 = width - diff
    if page_number_cut3 - page_number_cut1 > 2 * delta and float(page_number_x2 - page_number_x1) / float(page_number_cut2 - page_number_cut1) <= 9.0 \
            and _get_image_variance(image.crop((0, height - page_number_cut3, width, height))) / ImageStat.Stat(image).var[0] < 0.1 \
            and page_number_cut3 < height // 4 - delta:
        diff = page_number_cut3
    else:
        diff = page_number_cut1
    
    if DEBUG:
        print(' * autoCropImage:: Computing crop diff to %s (in %.3f)' % (diff, time.time() - before))
        image.save('tmp/1_before_crop.png')
    
    before = time.time()
    image = image.crop((0, 0, width, height - diff))
    if DEBUG:
        print(' * autoCropImage:: apply crop to %s (in %.3f)' % (diff, time.time() - before))
        image.save('tmp/2_after_crop.png')
    
    before = time.time()
    image = _simple_crop_image(image)
    if DEBUG:
        print(' * autoCropImage:: simple crop to %s in %.3f' % (image.size, time.time() - before))
        image.save('tmp/3_after_simple_crop.png')
    
    before = time.time()
    image = _blurauto_crop_image(image)
    if DEBUG:
        print(' * autoCropImage:: Blurauto %s in %.3f' % (image.size, time.time() - before))
        image.save('tmp/4_after_auto_blur.png')
    
    return image


@protect_bad_image
def _simple_crop_image(image):
    # type: (Image) -> Image
    try:
        x0, y0, xend, yend = ImageChops.invert(image).getbbox()
    except TypeError:  # bad image, specific to chops
        return image
    image = image.crop((x0, y0, xend, yend))
    return image


QUITE_BLACK_LIMIT = 25  # 25: totally my choice after look at colors ^^


# Can be black is really black, or just VERY dark
def _is_quite_black(pixel, precision=QUITE_BLACK_LIMIT):
    # type: (tuple[int, int, int], int) -> bool
    if pixel == (0, 0, 0):
        return True
    if pixel[0] <= precision and pixel[1] <= precision and pixel[2] <= precision:
        return True
    return False


def _is_quite_white(pixel, precision=QUITE_BLACK_LIMIT):
    # type: (tuple[int, int, int], int) -> bool
    if pixel == (255, 255, 255):
        return True
    if pixel[0] >= 255 - precision and pixel[1] >= 255 - precision and pixel[2] >= 255 - precision:
        return True
    return False


def _is_background_pixel(pixel, is_black_background):
    # type: (tuple[int, int, int], bool) -> bool
    if is_black_background:
        return _is_quite_black(pixel, precision=10)
    return _is_quite_white(pixel, precision=10)


LINE_DEBUG = -1

MIN_BOX_ALLOWED_HEIGHT = 36  # lower than this height, it's a bogus box

SOFT_MAX_BLOC_HEIGHT = 1500  # if higher than this, try to split into parts again

HARD_MAX_BLOC_HEIGHT = 3000  # if higher than this, stop the block


def _get_image_height(image):
    # type: (Image) -> int
    return image.size[1]


def _get_image_width(image):
    # type: (Image) -> int
    return image.size[0]


WHITE_PIXEL = (255, 255, 255)


# Remove images that are full white or full black
def _is_full_background_image(image):
    # type: (Image) -> bool
    precision = 5
    image_rgb = image.convert('RGB')
    height = _get_image_height(image)
    width = _get_image_width(image)
    pixels = image_rgb.load()
    start_pixel = pixels[0, 0]
    is_white = _is_quite_white(start_pixel, precision=precision)
    is_black = _is_quite_black(start_pixel, precision=precision)
    if DEBUG:
        print('  is_full_background_image:: white=%s   black=%s' % (is_white, is_black))
    if is_white:
        for x in range(width):
            for y in range(height):
                pixel = pixels[x, y]
                if not _is_quite_white(pixel, precision=precision):
                    if DEBUG:
                        print('    is_full_background_image:: the pixel %s/%s is not white %s-%s-%s' % (x, y, pixel[0], pixel[1], pixel[2]))
                    return False
        # all was white
        return True
    if is_black:
        for x in range(width):
            for y in range(height):
                pixel = pixels[x, y]
                if not _is_quite_black(pixel, precision=precision):
                    if DEBUG:
                        print('    is_full_background_image:: the pixel %s/%s is not black %s-%s-%s' % (x, y, pixel[0], pixel[1], pixel[2]))
                    return False
        # all was black
        return True
    
    # First pixel was not white or black
    return False




def _load_image(source):
    # type: (str) -> Image
    try:
        return Image.open(source)
    except IOError:
        raise RuntimeError('Cannot read image file %s' % source)


def save_image(image, target):
    # type: (Image, str) -> None
    try:
        image.save(target)
    except IOError:
        raise RuntimeError('Cannot write image file %s' % target)


# Look if the image is more width than height, if not, means it's should not be split (like the front page of a manga,
# when all the inner pages are double)
def is_splitable(source):
    # type: (str) -> bool
    image = _load_image(source)
    try:
        width, height = image.size
        return width > height
    except IOError:
        raise RuntimeError('Cannot read image file %s' % source)


def convert_image(source, split_right=False, split_left=False):
    # type: (str,  bool, bool) -> list[Image]
    
    device = parameters.get_device()
    try:
        size = EReaderData.get_size(device)
        palette = EReaderData.get_palette(device)
    except KeyError:
        raise RuntimeError('Unexpected output device %s' % device)
    
    # Load image from source path
    image = _load_image(source)
    
    # Webtoon is special, manually take order
    if parameters.is_webtoon():
        from .webtoon import split_webtoon as _split_webtoon
        converted_images = []  # we can have more than 1 results
        images = _split_webtoon(image)
        for image in images:
            image = _format_image_to_rgb(image)
            image = _apply_basic_grey(image)
            image = _resize_image(image, size)
            image = _fill_image_to_whole_size(image, size)  # note: after gray pass (adding white pixel here)
            converted_images.append(image)
        
        return converted_images
    
    image = _format_image_to_rgb(image)
    
    # Apply splits:
    if split_right:  # flags & ImageFlags.SplitRight:
        image = _split_right(image)
    if split_left:
        # if flags & ImageFlags.SplitRightLeft:
        image = _split_left(image)
    
    # Auto crop (remove useless white) the image, but before manage size and co, clean the source so
    image = _auto_crop_image(image)
    # Always Orient based the size: if too large, go paysage
    image = _orient_image(image, size)
    
    # Grey :
    #  * MANGA: if the image is mostly grey, we can apply a grey palette
    #  * COMICS/WEBTOONS: but if it was with colors, then the pillow got a better result (but FAR bigger, so not ok for manga)
    # Adapt to EReader palette
    if _is_image_grey(image):
        image = _apply_grey_palette(image, palette)  # palette are ok for manga black and white, and very small
    else:
        image = _apply_basic_grey(image)  # pillow is better for colors, but is very FAT
    
    # Adapt to the EReader native resolution
    image = _resize_image(image, size)
    image = _fill_image_to_whole_size(image, size)  # note: after gray pass (adding white pixel here)
    
    return [image]  # only one image if not webtoon



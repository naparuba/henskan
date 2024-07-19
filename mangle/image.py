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
import time
from math import ceil

from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat

from .archive import ARCHIVE_FORMATS
from .parameters import parameters

DEBUG = False


def set_debug():
    global DEBUG
    DEBUG = True


class EReaderData:
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
    
    Profiles = {
        'Kindle 1':                         ((600, 800), Palette4, ARCHIVE_FORMATS.PDF),
        'Kindle 2/3/Touch':                 ((600, 800), Palette15a, ARCHIVE_FORMATS.PDF),
        'Kindle 4 & 5':                     ((600, 800), Palette15b, ARCHIVE_FORMATS.PDF),
        'Kindle DX/DXG':                    ((824, 1200), Palette15a, ARCHIVE_FORMATS.PDF),
        'Kindle Paperwhite 1 & 2':          ((758, 1024), Palette15b, ARCHIVE_FORMATS.PDF),
        'Kindle Paperwhite 3/Voyage/Oasis': ((1072, 1448), Palette15b, ARCHIVE_FORMATS.PDF),
        'Kobo Mini/Touch':                  ((600, 800), Palette15b, ARCHIVE_FORMATS.CBZ),
        'Kobo Glo':                         ((768, 1024), Palette15b, ARCHIVE_FORMATS.CBZ),
        'Kobo Glo HD':                      ((1072, 1448), Palette15b, ARCHIVE_FORMATS.CBZ),
        'Kobo Aura':                        ((758, 1024), Palette15b, ARCHIVE_FORMATS.CBZ),
        'Kobo Aura HD':                     ((1080, 1440), Palette15b, ARCHIVE_FORMATS.CBZ),
        'Kobo Aura H2O':                    ((1080, 1430), Palette15a, ARCHIVE_FORMATS.CBZ),
        'Kobo Libra H2O':                   ((1264, 1680), Palette15a, ARCHIVE_FORMATS.CBZ),
        'Kobo Elipsa 2E':                   ((1440, 1872), Palette15a, ARCHIVE_FORMATS.CBZ),
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


@protect_bad_image
def _quantize_image(image, palette):
    # type: (Image, list) -> Image
    colors = len(palette) // 3
    if colors < 256:
        palette = palette + palette[:3] * (256 - colors)
    
    pal_img = Image.new('P', (1, 1))
    pal_img.putpalette(palette)
    
    return image.quantize(palette=pal_img)


@protect_bad_image
def _resize_image(image, size):
    # type: (Image, tuple[int, int]) -> Image
    width_dev, height_dev = size
    width_img, height_img = image.size
    
    if width_img <= width_dev and height_img <= height_dev:
        return image
    
    ratio_img = float(width_img) / float(height_img)
    ratio_width = float(width_img) / float(width_dev)
    ratio_height = float(height_img) / float(height_dev)
    
    if ratio_width > ratio_height:
        width_img = width_dev
        height_img = int(width_dev / ratio_img)
    elif ratio_width < ratio_height:
        height_img = height_dev
        width_img = int(height_dev * ratio_img)
    else:
        width_img, height_img = size
    
    if DEBUG:
        print(' * Resizing image from %s to %s/%s' % (image.size, width_img, height_img))
    
    return image.resize((width_img, height_img), Image.Resampling.LANCZOS)


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
    # type: (Image) -> int
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


def __get_image_height(image):
    # type: (Image) -> int
    return image.size[1]


def __get_image_width(image):
    # type: (Image) -> int
    return image.size[0]


WHITE_PIXEL = (255, 255, 255)


# Remove images that are full white or full black
def _is_full_background_image(image):
    # type: (Image) -> bool
    precision = 5
    image_rgb = image.convert('RGB')
    height = __get_image_height(image)
    width = __get_image_width(image)
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


def __fail_back_to_cut_very_big_one(image):
    # type: (Image) -> list[Image]
    image_height = __get_image_height(image)
    image_width = __get_image_width(image)
    print("__fail_back_to_cut_very_big_one:: %s" % image_height)
    if image_height <= HARD_MAX_BLOC_HEIGHT:
        return [image]
    
    hard_split_images = []
    nb_images = int(ceil(float(image_height) / HARD_MAX_BLOC_HEIGHT))
    
    for idx in range(nb_images):
        hard_split = image.crop((0, idx * HARD_MAX_BLOC_HEIGHT, image_width, (idx + 1) * HARD_MAX_BLOC_HEIGHT))
        hard_split_images.append(hard_split)
    print("__fail_back_to_cut_very_big_one:: cut into %s parts" % len(hard_split_images))
    return hard_split_images


# We have a block image that is too big, try to see if with linear cut it's possible to
# have more parts
def __try_to_smart_split_block(image, is_black_background, level=1):
    # type: (Image, bool, int) -> list[Image]
    image = _simple_crop_image(image)
    if DEBUG:
        image.save('tmp/input_%s.jpg' % level)
    image_height = __get_image_height(image)
    image_width = __get_image_width(image)
    print(" === [LEVEL=%s] Try to smart split block of size %s / %s  (mostly black=%s)" % (level, image_height, image_width, is_black_background))
    
    # Maybe the image is now too small: just give it back :)
    if image_height <= 200:
        return [image]
    
    split_pixel = WHITE_PIXEL if not is_black_background else (0, 0, 0)
    print(" ==== Finding for pixel: %s" % str(split_pixel))
    pixels = image.load()
    for y in range(500, image_height - 200, 10):  # do not try to cut too early, it's useless
        # First look if the left => higher right is possible for split
        line_is_valid = False
        found_angle = None
        from_left = True
        pixel = pixels[0, y]
        if _is_background_pixel(pixel, is_black_background):
            for angle_int in range(0, 200):
                angle = float(angle_int) // 100
                found_angle = angle
                line_is_valid = True
                for x in range(image_width):
                    tested_pixel_y = y - ceil(x * angle)
                    if tested_pixel_y <= 0:
                        line_is_valid = False
                        break
                    tested_pixel = pixels[x, tested_pixel_y]
                    if not _is_background_pixel(tested_pixel, is_black_background):
                        line_is_valid = False
                        break
                # We did found a valid split line
                if line_is_valid:
                    break
            if line_is_valid:
                print("LEFT:: found a valid split line, angle=%s y=%s" % (found_angle, y))
        
        # Then is the line is not found look if the right => higher left is possible for split
        if not line_is_valid and pixels[image_width - 1, y] == split_pixel:
            from_left = False
            for angle_int in range(0, 200):
                angle = float(angle_int) // 100
                found_angle = angle
                line_is_valid = True
                
                for x in range(image_width - 1, -1, -1):
                    tested_pixel_y = y - int(ceil((image_width - x) * angle))
                    if tested_pixel_y <= 0:
                        line_is_valid = False
                        break
                    
                    tested_pixel = pixels[x, tested_pixel_y]
                    if not _is_background_pixel(tested_pixel, is_black_background):
                        line_is_valid = False
                        break
                # We did found a valid split line
                if line_is_valid:
                    # print "[RIGHT] Line %s is splitable with angle=%s" % (y, found_angle)
                    break
        
        # Maybe nor left or right was able to split, skip this line
        if not line_is_valid:
            continue
        
        print("Yeah, we can cut from %s with angle %s and from left:%s" % (y, found_angle, from_left))
        
        split_pixels = {}
        if from_left:
            for x in range(image_width):
                split_pixels[x] = y - int(ceil(x * found_angle))
        else:
            for x in range(image_width - 1, -1, -1):
                split_pixels[x] = y - int(ceil((image_width - x) * found_angle))
        lower_y = min(split_pixels.values())
        higher_y = max(split_pixels.values())
        
        # We will have 2 images:
        # * higher part that will erase all UNDER the line
        # * lower part that will erase all TOP the line
        higher_part_image = image.copy()
        higher_part_pixels = higher_part_image.load()
        rest_to_split_image = image.copy()
        rest_to_split_pixels = rest_to_split_image.load()
        
        # For debug:
        if DEBUG:
            if from_left:
                for x in range(image_width):
                    tested_pixel_y = y - ceil(x * found_angle)
                    # print " ====== LEFT [Y=%s Angle=%s] SPLIT LINE WAS Testing pixel %s / %s :: %s" % (y, found_angle, x, tested_pixel_y, str(pixels[x, tested_pixel_y]))
                    pixels[x, tested_pixel_y] = (255, 0, 0)
            else:
                for x in range(image_width - 1, -1, -1):
                    tested_pixel_y = y - int(ceil((image_width - x) * found_angle))
                    # print " ====== RIGHT [Y=%s Angle=%s] SPLIT LINE WAS Testing pixel %s / %s :: %s" % (y, found_angle, x, tested_pixel_y, str(pixels[x, tested_pixel_y]))
                    pixels[x, tested_pixel_y] = (255, 0, 0)
        
        if DEBUG:
            image.save('tmp/with_line_%s.jpg' % level)
            print("SPLIT RANGE", lower_y, higher_y)
        
        # HIGHER PART: clean all BELOW the line
        for y in range(lower_y, higher_y):
            for x in range(image_width):
                line_y = split_pixels[x]
                if y > higher_y or y > line_y:
                    higher_part_pixels[x, y] = WHITE_PIXEL
        
        # We must crop it to remove all useless part
        higher_part_image = higher_part_image.crop((0, 0, image_width, higher_y))
        if DEBUG:
            higher_part_image.save('tmp/higher_part_%s.jpg' % level)
        
        # LOWER PART: clean all OVER the line
        for y in range(lower_y, higher_y):
            for x in range(image_width):
                line_y = split_pixels[x]
                if y < lower_y or y < line_y:
                    rest_to_split_pixels[x, y] = WHITE_PIXEL
        
        rest_to_split_image = rest_to_split_image.crop((0, lower_y, image_width, image_height))
        if DEBUG:
            rest_to_split_image.save('tmp/rest_%s.jpg' % level)
        
        res = [higher_part_image]
        
        rest_image_splitted = __try_to_smart_split_block(rest_to_split_image, is_black_background, level=level + 1)
        res.extend(rest_image_splitted)
        
        return res
    
    # We did fail to split it so give back the original image
    print("did fail to smart split the image, still %s high" % image_height)
    # fuck
    fail_back_images = __fail_back_to_cut_very_big_one(image)
    return fail_back_images


def __parse_webtoon_block(image, start_of_box, width, end_of_box, split_final_images, is_black_background):
    # type: (Image, int, int, int, list[Image], bool) -> None
    from .similarity import similarity
    box_image = image.crop((0, start_of_box, width, end_of_box))
    
    potential_images = [box_image]
    # Maybe it's too high
    img_height = __get_image_height(box_image)
    if img_height >= SOFT_MAX_BLOC_HEIGHT:
        print(" *** WebToon block is too high (%s), trying to split it again" % img_height)
        potential_images = __try_to_smart_split_block(box_image, is_black_background, level=0)
    
    for p_image in potential_images:
        # TODO: TEST: if all pixels are black: drop
        image_cropped = _auto_crop_image(p_image)
        print('  ** image cropped size: %s' % str(image_cropped.size))
        try:
            variance = _get_image_variance(image_cropped)
        except ZeroDivisionError:  # seems that the image is too small, let the real test look for it
            print('   ** Image seems to have issue, skipping variance check')
            variance = 999  # do not delete it
        
        if variance < 1:  # mostly the same color, skip it
            similarity.add_deleted_image('too_low_variance', image_cropped, 'variance_%.2f' % variance, do_move=True)
            print('  ** SKIP image cropped variance: %s is too small' % str(variance))
            continue
        # Skip images that are too small (bugs in cut detection protection)
        if __get_image_height(image_cropped) <= MIN_BOX_ALLOWED_HEIGHT:
            print("SKIP: image is too small to save (%dpx)" % __get_image_height(image_cropped))
            continue
        if not similarity.is_valid_image(image_cropped):
            print(" ** DROPPING IMAGE")
            continue
        if _is_full_background_image(image_cropped):
            print(" ** Dropping full white/black image")
            similarity.add_deleted_image('too_white', image_cropped, 0, do_move=True)
            continue
        print(" Split size: %s" % str(image_cropped.size))
        split_final_images.append(image_cropped)


def _split_webtoon(image):
    # type: (Image) -> list[Image]
    split_images = []
    width, height = image.size
    
    # If we have a black background, good luck to split by white
    most_color = _find_dominant_color(image)
    is_black_background = most_color == (0, 0, 0)
    
    print(" TOON: analysing image %s/%s  (is black background=%s)" % (width, height, is_black_background))
    MIN_COLOR_HEIGHT = 30  # not less than 30px for a picture
    MAX_BOX_HEIGHT = 1400  # if more than 1400, if possible, close box
    pixels = image.load()  # this is not a list, nor is it list()'able
    
    lines = []
    for y in range(height):
        is_white = True
        for x in range(width):
            cpixel = pixels[x, y]
            # If classic white background
            if not is_black_background:
                if cpixel != WHITE_PIXEL:
                    is_white = False
                    break
            else:  # black background, do not look at black
                if y == LINE_DEBUG:
                    print("PIXEL: %s => %s" % (x, str(cpixel)))
                if not _is_quite_black(cpixel) and not cpixel == WHITE_PIXEL:
                    is_white = False
                    break
                # else:
                #    print "Line %s is white" % y
        if y == LINE_DEBUG:
            print("%s IS WHITE LINE: %s" % (y, is_white))
        lines.append((y, is_white))
    
    print("Number of white lines: %s" % (len([c for c in lines if c[1]])))
    
    start_of_box = None
    in_box = False
    last_black_line = None
    for (y, is_white_line) in lines:
        # First line: we are starting a box or not
        if y == 0:
            in_box = not is_white_line
            if in_box:
                start_of_box = y
                last_black_line = y
            continue
        
        if in_box and False:
            current_box_size = y - start_of_box
            if current_box_size > HARD_MAX_BLOC_HEIGHT:
                __parse_webtoon_block(image, start_of_box, width, y, split_images, is_black_background)
                last_black_line = None
                start_of_box = None
                in_box = False
                print("***" * 20, "Protection, split at", current_box_size)
                continue
        
        # we already start
        # If black can continue a box or start a new one
        if not is_white_line:
            # we are a black line, so maybe we just continue the box
            if in_box:
                last_black_line = y
                continue
            # or we start a new one
            else:
                print(' - Starting a box at %s' % y)
                in_box = True
                last_black_line = y
                start_of_box = y
                continue
        # Is a white line, we can close the box
        else:
            if not in_box:
                # TODO: do not allow a too big white part
                continue
            current_box_size = y - start_of_box
            # print "WHITE: current box size detecte", current_box_size
            # Close the box only if the last black if far ago
            # Of if the box is very high
            distance_from_last_black = y - last_black_line
            if distance_from_last_black > MIN_COLOR_HEIGHT or current_box_size > MAX_BOX_HEIGHT:
                __parse_webtoon_block(image, start_of_box, width, y, split_images, is_black_background)
                last_black_line = None
                start_of_box = None
                in_box = False
    
    # We did finish, if we are in a box, close it
    if in_box:
        __parse_webtoon_block(image, start_of_box, width, last_black_line, split_images, is_black_background)
    
    return split_images


def guess_manga_or_webtoon_image(source):
    # type: (str) -> str
    image = _load_image(source)
    try:
        width, height = image.size
    except IOError:
        raise RuntimeError('Cannot read image file %s' % source)
    
    # A webtoon is  far higher than a manga, so we can take a 4x ration as high means a webtoon
    # and if not, is a manga
    
    return 'webtoon' if height > 4 * width else 'manga'


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
        converted_images = []  # we can have more than 1 results
        images = _split_webtoon(image)
        for image in images:
            image = _format_image_to_rgb(image)
            image = _resize_image(image, size)
            image = _quantize_image(image, palette)
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
    # Adapt to the EReader native resolution
    image = _resize_image(image, size)
    # Adapt to EReader palette
    image = _quantize_image(image, palette)
    
    return [image]  # only one image if not webtoon

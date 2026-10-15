#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Webtoon-specific processing functions.

This module handles the detection and splitting of webtoon images,
which are typically very tall vertical strips that need to be split
into smaller panels for better readability on e-readers.
"""
from __future__ import print_function

from math import ceil

from PIL import Image

from .image import (
    _find_dominant_color,
    _is_full_background_image,
    _auto_crop_image,
    _simple_crop_image,
    _get_image_variance,
    _is_quite_black,
    _is_background_pixel,
    _load_image,
    _get_image_height,
    _get_image_width,
    WHITE_PIXEL,
    DEBUG,
    LINE_DEBUG,
    MIN_BOX_ALLOWED_HEIGHT,
    SOFT_MAX_BLOC_HEIGHT,
    HARD_MAX_BLOC_HEIGHT,
)

# Import similarity module for image validation
# Note: imported lazily in functions to avoid circular dependencies


def __fail_back_to_cut_very_big_one(image):
    # type: (Image) -> list[Image]
    """
    Fallback method to split a very large image into chunks.
    
    When smart splitting fails, this method cuts the image into
    equal-sized vertical chunks based on HARD_MAX_BLOC_HEIGHT.
    
    Args:
        image: PIL Image to split
        
    Returns:
        List of PIL Images (chunks)
    """
    image_height = _get_image_height(image)
    image_width = _get_image_width(image)
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


def __try_to_smart_split_block(image, is_black_background, level=1):
    # type: (Image, bool, int) -> list[Image]
    """
    Attempt to intelligently split a large webtoon block.
    
    This function tries to find diagonal or horizontal split lines
    by analyzing the background pixels. It can detect angled cuts
    (common in webtoons) and split the image accordingly.
    
    Args:
        image: PIL Image to split
        is_black_background: True if the webtoon has a black background
        level: Recursion level (for debugging)
        
    Returns:
        List of PIL Images (split panels)
    """
    image = _simple_crop_image(image)
    if DEBUG:
        image.save('tmp/input_%s.jpg' % level)
    image_height = _get_image_height(image)
    image_width = _get_image_width(image)
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
    """
    Parse and process a single webtoon block (panel).
    
    This function extracts a block from the webtoon image, applies
    additional splitting if needed, crops it, validates it, and
    adds it to the final images list.
    
    Args:
        image: Full webtoon PIL Image
        start_of_box: Y coordinate where the block starts
        width: Width of the image
        end_of_box: Y coordinate where the block ends
        split_final_images: List to append valid images to (modified in place)
        is_black_background: True if the webtoon has a black background
    """
    from .similarity import similarity
    box_image = image.crop((0, start_of_box, width, end_of_box))
    
    potential_images = [box_image]
    # Maybe it's too high
    img_height = _get_image_height(box_image)
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
            similarity._add_deleted_image('too_low_variance', image_cropped, 'variance_%.2f' % variance, do_move=True)
            print('  ** SKIP image cropped variance: %s is too small' % str(variance))
            continue
        # Skip images that are too small (bugs in cut detection protection)
        if _get_image_height(image_cropped) <= MIN_BOX_ALLOWED_HEIGHT:
            print("SKIP: image is too small to save (%dpx)" % _get_image_height(image_cropped))
            continue
        if not similarity.is_valid_image(image_cropped, do_move=True):
            print(" ** [similarity] DROPPING IMAGE")
            continue
        if _is_full_background_image(image_cropped):
            print(" ** Dropping full white/black image")
            similarity._add_deleted_image('too_white', image_cropped, 0, do_move=True)
            continue
        print(" Split size: %s" % str(image_cropped.size))
        split_final_images.append(image_cropped)


def split_webtoon(image):
    # type: (Image) -> list[Image]
    """
    Split a webtoon image into multiple panels.
    
    This is the main entry point for webtoon processing. It analyzes
    the image to find panel boundaries (white or black separator lines)
    and splits the image accordingly.
    
    Args:
        image: PIL Image of a webtoon
        
    Returns:
        List of PIL Images (individual panels)
    """
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
            # print "WHITE: current box size detect", current_box_size
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
    """
    Detect if an image is a manga or a webtoon based on aspect ratio.
    
    Webtoons are typically very tall (height > 4 * width), while
    manga pages are closer to square or slightly taller.
    
    Args:
        source: Path to the image file
        
    Returns:
        'webtoon' or 'manga'
        
    Raises:
        RuntimeError: If the image cannot be read
    """
    image = _load_image(source)
    try:
        width, height = image.size
    except IOError:
        raise RuntimeError('Cannot read image file %s' % source)
    
    # A webtoon is  far higher than a manga, so we can take a 4x ration as high means a webtoon
    # and if not, is a manga
    
    return 'webtoon' if height > 4 * width else 'manga'


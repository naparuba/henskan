import sys
import os
import image

image.set_debug()

DEVICE = 'Kobo Aura H2O'

my_dir = os.path.abspath(os.path.curdir)
print "Image module: %s" % image

IMG1_PATH = os.path.join(my_dir, 'resources', 'img1.jpg')
if not os.path.exists(IMG1_PATH):
    print "ERROR: no img1 to test"
    sys.exit(2)


WEBTOON2_PATH = os.path.join(my_dir, 'resources', 'webtoon_2.jpg')
if not os.path.exists(WEBTOON2_PATH):
    print "ERROR: no webtoon2 to test"
    sys.exit(2)


WEBTOON3_PATH = os.path.join(my_dir, 'resources', 'webtoon_3.jpg')
if not os.path.exists(WEBTOON3_PATH):
    print "ERROR: no webtoon3 to test"
    sys.exit(2)


WEBTOON4_PATH = os.path.join(my_dir, 'resources', 'webtoon_4.jpg')
if not os.path.exists(WEBTOON4_PATH):
    print "ERROR: no webtoon4 to test"
    sys.exit(2)


WEBTOON5_PATH = os.path.join(my_dir, 'resources', 'webtoon_5.jpg')
if not os.path.exists(WEBTOON5_PATH):
    print "ERROR: no webtoon5 to test"
    sys.exit(2)


# Clean all tmp
TMP_DIR = os.path.join(my_dir, 'tmp')
print " * Cleaning tmp dir: %s" % TMP_DIR
for f_path in os.listdir(TMP_DIR):
    full_path = os.path.join(TMP_DIR, f_path)
    print "  - %s" % full_path
    os.unlink(full_path)


def find_dominant_color(img):
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


# Test webtoon
from PIL import Image, ImageStat

def parse_webtoon(number):
    WEBTOON_PATH = os.path.join(my_dir, 'resources', 'webtoon_%s.jpg' % number)
    if not os.path.exists(WEBTOON_PATH):
        print "ERROR: no webtoon to test"
        sys.exit(2)
    
    print " ======== WEBTOON %s ========" % number
    source = WEBTOON_PATH
    target = os.path.join(TMP_DIR, 'webtoon_%s.jpg' % number)
    flags = image.ImageFlags.AutoCrop | image.ImageFlags.Resize | image.ImageFlags.Quantize | image.ImageFlags.Webtoon
    
    img = Image.open(source)
    print "VARIANCE %s" % number, ImageStat.Stat(img).var
    print "Most color: %s" % str(find_dominant_color(img))
    
    print ' * Converting image %s' % source
    split_images = image.convertImage(source, target, DEVICE, flags)
    for (idx, split_image) in enumerate(split_images):
        pth = os.path.join(TMP_DIR, 'toon%s_%d.png' % (number, idx))
        split_image.save(pth)
    print '  - Done in %s' % target


parse_webtoon(1)
parse_webtoon(2)
parse_webtoon(3)
parse_webtoon(4)
parse_webtoon(5)
parse_webtoon(6)


# Test normal image
source = IMG1_PATH
target = os.path.join(TMP_DIR, 'imp1.converted.png')
flags = image.ImageFlags.AutoCrop | image.ImageFlags.Resize | image.ImageFlags.Quantize

print ' * Converting image %s' % source
image.convertImage(source, target, DEVICE, flags)
print '  - Done in %s' % target
